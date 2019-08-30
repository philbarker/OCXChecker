from rdflib import Namespace, Literal, URIRef, BNode
from rdflib.namespace import RDF, RDFS
from cgi import escape

SDO = Namespace("http://schema.org/")


def do_checks(self):
    # refactor this into datachecks.py to set results of DataChecks
    checks = DataChecks(self.ocx_graph, self.schema_graph)
    checks.find_primary_entities(self.primary_ocx_types)
    checks.check_named_entities()
    checks.check_all_predicates()
    return checks.results


class CheckResult:
    def __init__(self, n, d, p=False):
        self.name = n
        self.description = d
        self.passes = p
        self.info = []
        self.warnings = []
        self.results = []

    def add_info(self, info):
        self.info.append(info)


class DataChecks:
    from .utils import (
        deduplicate,
        schema_label_string,
        type_string,
        get_parent_classes,
        get_types,
    )

    def __init__(self, graph, schema_graph):
        self.graph = graph
        self.schema_graph = schema_graph
        self.results = {}

    def subject_predicate_check(self, s, p):
        result = CheckResult("subject check", "subject is in predicate's domain", True)
        valid_subject_types = []
        p_domain_labels = ""
        for p_domain in self.schema_graph.objects(p, SDO.domainIncludes):
            valid_subject_types.append(p_domain)
            p_domain_label = self.schema_label_string(p_domain, "", ", ")
            p_domain_labels = p_domain_labels + p_domain_label
        p_domain_labels = p_domain_labels[:-2]
        type_name, types = self.get_types(s)
        types_string = self.type_string(types)
        s_name = ""
        for name in self.graph.objects(s, SDO.name):
            s_name = s_name + " " + name
        if s_name == "":
            s_name = "with no name"
        result.add_info("used on object named " + s_name)
        result.add_info("object is of type " + types_string)
        result.add_info("property has expected domain " + p_domain_labels)
        domain_valid = False
        for t in types:
            if t in valid_subject_types:
                domain_valid = True
        if domain_valid:
            result.passes = True
        elif type(s) is BNode:
            result.passes = False
            info = (
                "an untyped BNode object has been used where "
                + p_domain_labels
                + " was expected. Please add object type."
            )
            result.add_info(info)
        elif type(s) is URIRef:
            result.passes = True
            info = (
                "a URI reference for an object of unknown type has been used (it may not be on this page) where "
                + p_domain_labels
                + " was expected. You should check the object at the end of the URI is of the right type. You could add its type here to stop seeing this warning "
            )
            result.add_info(info)
        else:
            result.passes = False
            result.add_info("subject type is not in expected domain of property")
        return result

    def predicate_object_check(self, p, o):
        result = CheckResult("object check", "object is in predicate's range", True)
        valid_object_types = []
        p_range_labels = ""
        for p_range in self.schema_graph.objects(p, SDO.rangeIncludes):
            valid_object_types.append(p_range)
            p_range_label = self.schema_label_string(p_range, "", ", ")
            p_range_labels = p_range_labels + p_range_label
        p_range_labels = p_range_labels[:-2]
        type_name, types = self.get_types(o)
        range_valid = False
        for t in types:
            if t in valid_object_types:
                range_valid = True
        result.add_info("property has expected range " + p_range_labels)
        result.add_info("points to object of type " + self.type_string(types))
        if range_valid:
            result.passes = True
        elif type(o) is Literal:
            result.passes = True
            warning = (
                "text has been used where "
                + p_range_labels
                + " was expected. This is not best practice "
            )
            result.warnings.append(warning)
        elif type(o) is BNode:
            result.passes = False
            warning = (
                "an untyped BNode object has been used where "
                + p_range_labels
                + " was expected. Please add object type "
            )
            result.warnings.append(warning)
        elif type(o) is URIRef:
            result.passes = True
            warning = (
                "a URI reference for an object of unknown type has been used (it may not be on this page) where "
                + p_range_labels
                + " was expected. You should check the object at the end of the URI is of the right type. You could add its type here to stop seeing this warning "
            )
            result.warnings.append(warning)
        else:
            result.passes = False
        return result

    def check_predicate(self, s, p, o):
        # checks predicate from single statement
        result = CheckResult(
            "predicate check for " + p,
            "subject and object are in expected domain and range",
            True,
        )
        result.add_info("predicate in statement " + " ".join([s, p, o]))
        result.results.append(self.subject_predicate_check(s, p))
        result.results.append(self.predicate_object_check(p, o))
        return result

    def check_all_predicates(self):
        results = {
            "name": "predicate checks",
            "description": "subjects are in predicates' domains and objects are in predicates' ranges",
            "passes": True,
            "info": [],
            "warnings": [],
            "results": [],
        }
        for s, p, o in self.graph.triples((None, None, None)):
            if p in self.schema_graph.subjects(RDF.type, RDF.Property):
                results["results"].append(self.check_predicate(s, p, o))
        self.results["predicate_checks"] = results

    def find_primary_entities(self, primary_types):
        entities = []
        primary_entities = {}
        primary_entities["info"] = []
        primary_entities["result"] = None
        for aType in primary_types:
            entities.extend(self.graph.subjects(RDF.type, aType))
        primary_entities["info"] = self.deduplicate(entities)
        if len(primary_entities["info"]) < 1:
            primary_entities["result"] = False
        else:
            primary_entities["result"] = True
        self.results["primary_entities"] = primary_entities

    def check_named_entities(self):
        self.results["entity_check"] = {}
        named_entities = []
        # find everything that has a type
        for e in self.graph.subjects(RDF.type, None):
            if type(e) != BNode:
                named_entities.append(e)
        named_entities = self.deduplicate(named_entities)
        for e in named_entities:
            uri = str(e)
            results = {}
            results["name"] = "Check named entities"
            results["description"] = "the named entities have key properties"
            results["entity_name_check"] = self.check_entity_name(e)
            results["entity_description_check"] = self.check_entity_description(e)
            results["type_check"] = self.check_entity_type(e)
            self.results["entity_check"][uri] = results
        # report_on_type(entity, ocx_graph)

    def check_entity_type(self, e):
        uri = str(e)
        passes = False
        warnings = []
        info = []
        name = "type check on " + uri
        descr = "entity has known RDF:type"
        for t in self.graph.objects(e, RDF.type):
            passes = True
            info.append("RDF type is " + t)
            if t in self.schema_graph.subjects(RDF.type, RDFS.Class):
                label = self.schema_graph.label(t)
                parent = self.schema_graph.value(t, SDO.isPartOf, None)
                if parent:
                    pass
                else:
                    parent = "oerschema.org"
                info.append("this type is known as " + label + " from " + parent)
            else:
                warnings.append("this type is unknown")
        if not passes:
            info.append("this entity is of unspecified type.")
        result = {
            "name": name,
            "descr": descr,
            "passes": passes,
            "info": info,
            "warnings": warnings,
        }
        return result

    def check_entity_description(self, e):
        c = 0
        passes = True
        info = []
        warnings = []
        literal = True
        for description in self.graph.objects(e, SDO.description):
            c += 1
            if type(description).__name__ == "Literal":
                passes = True
                info.append("Description = " + description[0:70])
            else:
                literal = False
                info.append("Description is not a literal")
        if c > 1:
            warnings.append(
                "Having more than one description may be ambiguous, consider using sdo:alternateName."
            )
        elif c < 1:
            warnings.append("No sdo.description. Descriptions are useful.")
        if not literal:
            passes = False
        result = {"passes": passes, "info": info, "warnings": warnings}
        return result

    def check_entity_name(self, e):
        c = 0
        passes = False
        info = []
        warnings = []
        literal = True
        for name in self.graph.objects(e, SDO.name):
            c += 1
            if type(name).__name__ == "Literal":
                passes = True
                info.append("Name = " + name)
            else:
                literal = False
                info.append("Name is not a literal")
        if c > 1:
            warnings.append(
                "Having more than one name may be ambiguous, consider using sdo:alternateName."
            )
        elif c < 1:
            warnings.append("No sdo.name found. Names are useful.")
        if not literal:
            passes = False
        result = {"passes": passes, "info": info, "warnings": warnings}
        return result
