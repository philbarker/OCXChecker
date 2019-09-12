from rdflib import Namespace, Literal, URIRef, BNode
from rdflib.namespace import RDF, RDFS
from cgi import escape

SDO = Namespace("http://schema.org/")


class CheckResult(dict):
    def __init__(self, n, d, p=False):
        self["name"] = n
        self["description"] = d
        self["passes"] = p
        self["info"] = []
        self["warnings"] = []
        self["results"] = []

    def add_info(self, i):
        if type(i) is str:
            self["info"].append(i)
        elif type(i) is list:
            self["info"] = self["info"] + i
        else:
            pass  # to do: exception handling

    def add_warning(self, w):
        if type(w) is str:
            self["warnings"].append(w)
        elif type(w) is list:
            self["warnings"] = self["warnings"] + w
        else:
            pass  # to do: exception handling

    def add_result(self, r):
        if type(r) is CheckResult:
            self["results"].append(r)
        elif type(r) is list:
            self["results"] = self["results"] + r
        else:
            pass  # to do: exception handling

    def set_passes(self, p: bool):
        self["passes"] = p


from .checkutils import deduplicate, schema_label_string, labels_string, get_types


class DataChecks:
    def __init__(self, graph, schema_graph):
        self.graph = graph
        self.schema_graph = schema_graph

    def find_primary_entities(self, primary_types):
        result = CheckResult(
            n="primary entities present",
            d="check that there is at least one primary entity",
            p=False,
        )
        entities = []
        for aType in primary_types:
            entities.extend(self.graph.subjects(RDF.type, aType))
        result.add_info(deduplicate(entities))
        if len(result["info"]) < 1:
            result.set_passes(False)
            result.add_info("no primary entities were found")
        else:
            result.set_passes(True)
        return result

    def subject_predicate_check(self, s, p):
        result = CheckResult("subject check", "subject is in predicate's domain", True)
        valid_subject_types = []
        p_domain_labels = ""
        for p_domain in self.schema_graph.objects(p, SDO.domainIncludes):
            valid_subject_types.append(p_domain)
            p_domain_label = schema_label_string(self.schema_graph, p_domain, "", ", ")
            p_domain_labels = p_domain_labels + p_domain_label
        p_domain_labels = p_domain_labels[:-2]
        type_name, types = get_types(self.graph, self.schema_graph, s)
        types_string = labels_string(self.schema_graph, types)
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
            result.set_passes(True)
        elif type(s) is BNode:
            result.set_passes(False)
            info = (
                "an untyped BNode object has been used where "
                + p_domain_labels
                + " was expected. Please add object type."
            )
            result.add_info(info)
        elif type(s) is URIRef:
            result.set_passes(True)
            info = (
                "a URI reference for an object of unknown type has been used (it may not be on this page) where "
                + p_domain_labels
                + " was expected. You should check the object at the end of the URI is of the right type. You could add its type here to stop seeing this warning "
            )
            result.add_info(info)
        else:
            result.set_passes(False)
            result.add_info("subject type is not in expected domain of property")
        return result

    def predicate_object_check(self, p, o):
        result = CheckResult(
            "object range check", "object is in predicate's range", True
        )
        valid_object_types = []
        p_range_labels = ""
        for p_range in self.schema_graph.objects(p, SDO.rangeIncludes):
            valid_object_types.append(p_range)
            p_range_label = schema_label_string(self.schema_graph, p_range, "", ", ")
            p_range_labels = p_range_labels + p_range_label
        p_range_labels = p_range_labels[:-2]
        type_name, types = get_types(self.graph, self.schema_graph, o)
        range_valid = False
        for t in types:
            if t in valid_object_types:
                range_valid = True
        result.add_info("property has expected range " + p_range_labels)
        result.add_info(
            "points to object of type " + labels_string(self.schema_graph, types)
        )
        if range_valid:
            result.set_passes(True)
        elif type(o) is Literal:
            result.set_passes(True)
            warning = (
                "text has been used where "
                + p_range_labels
                + " was expected. This is not best practice "
            )
            result.add_warning(warning)
        elif type(o) is BNode:
            result.set_passes(False)
            warning = (
                "an untyped BNode object has been used where "
                + p_range_labels
                + " was expected. Please add object type "
            )
            result.add_warning(warning)
        elif type(o) is URIRef:
            result.set_passes(True)
            warning = (
                "a URI reference for an object of unknown type has been used (it may not be on this page) where "
                + p_range_labels
                + " was expected. You should check the object at the end of the URI is of the right type. You could add its type here to stop seeing this warning "
            )
            result.add_warning(warning)
        else:
            result.set_passes(False)
        return result

    def check_predicate(self, s, p, o):
        # checks predicate from single statement
        result = CheckResult(
            "predicate check for " + p,
            "subject and object are in expected domain and range",
            True,
        )
        result.add_info("predicate in statement " + " ".join([s, p, o]))
        result["results"].append(self.subject_predicate_check(s, p))
        result["results"].append(self.predicate_object_check(p, o))
        return result

    def check_all_predicates(self):
        result = CheckResult(
            n="predicate checks",
            d="subjects are in predicates' domains, and objects are in predicates' ranges for all statements",
            p=True,
        )
        for s, p, o in self.graph.triples((None, None, None)):
            if p in self.schema_graph.subjects(RDF.type, RDF.Property):
                result["results"].append(self.check_predicate(s, p, o))
        return result

    def check_named_entity(self, e):
        uri = str(e)
        result = CheckResult(
            n="check entity " + uri,
            d="entity " + uri + " has name, description and type",
            p=True,
        )
        result.add_result(self.check_entity_name(e))
        result.add_result(self.check_entity_description(e))
        result.add_result(self.check_entity_type(e))
        for r in result["results"]:
            # set passes to true if all sub-result passes are true
            result.set_passes(result["passes"] and r["passes"])
        return result

    def check_all_named_entities(self):
        named_entities = []
        result = CheckResult(
            n="all named entity checks",
            d="entities with URI have name, description and type",
            p=True,
        )
        # find everything that has a type and is not a blank node
        for e in self.graph.subjects(RDF.type, None):
            if type(e) != BNode:
                named_entities.append(e)
        named_entities = deduplicate(named_entities)
        for e in named_entities:
            uri = str(e)
            result.add_result(self.check_named_entity(e))
        return result

    def check_entity_type(self, e):
        uri = str(e)
        result = CheckResult(
            n="check entity type", d="entity has known RDF:type", p=False
        )
        for t in self.graph.objects(e, RDF.type):
            result.set_passes(True)
            result.add_info("RDF type is " + t)
            if t in self.schema_graph.subjects(RDF.type, RDFS.Class):
                label = self.schema_graph.label(t)
                parent = self.schema_graph.value(t, SDO.isPartOf, None)
                if parent:
                    pass
                else:
                    parent = "oerschema.org"
                msg = "this type is known as " + label + " from " + parent
                result.add_info(msg)
            else:
                result.add_warning("this type is unknown")
        if not result["passes"]:
            result.set_passes(False)
            result.add_info("this entity is of unspecified type.")
        return result

    def check_entity_description(self, e):
        c = 0
        literal = True
        result = CheckResult(
            n="check entity description", d="description is string or absent", p=True
        )
        for description in self.graph.objects(e, SDO.description):
            c += 1
            if type(description).__name__ == "Literal":
                result.set_passes(True)
                result.add_info("Description = " + description[0:70])
            else:
                literal = False
                result.add_info("Description is not a literal")
                result.set_passes(False)
        if c > 1:
            msg = "Having more than one description may be ambiguous."
            result.add_warning(msg)
        elif c < 1:
            msg = "No sdo.description. Descriptions are useful."
            result.add_warning(msg)
        if not literal:
            result.set_passes(False)
        return result

    def check_entity_name(self, e):
        c = 0
        literal = True
        result = CheckResult(
            n="Check entity name",
            d="entity has at least one name property, name is a string",
            p=False,
        )
        for name in self.graph.objects(e, SDO.name):
            c += 1
            if type(name).__name__ == "Literal":
                result.add_info("Name = " + name)
                result.set_passes(True)
            else:
                literal = False
                result.add_info("name is not a literal")
        if c > 1:
            msg = "Having more than one name may be ambiguous, consider using sdo:alternateName."
            result.add_warning(msg)
        elif c < 1:
            msg = "No sdo.name found. Names are useful."
            result.set_passes(False)
            result.add_warning(msg)
        if not literal:
            passes = False
            result.set_passes(False)
        return result
