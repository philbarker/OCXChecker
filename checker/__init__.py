from sys import version
from cgi import escape
from sys import path
from rdflib import Namespace, Literal, URIRef, BNode
from rdflib.namespace import RDF, RDFS
from .pagedata import PageData
from .ocxgraph import OCXGraph
from .schemagraph import SchemaGraph

SDO = Namespace("http://schema.org/")
OER = Namespace("http://oerschema.org/")
OCX = Namespace("https://github.com/K12OCX/k12ocx-specs/")

class OCXdata:
    """ A class to comprise the page retrieved from the request url,
        the Graph of JSON-LD extracted from that page, a Graph of
        the RDFS for vocabularies used, plus various parameters and
        properties such as namespace URIs.
    """

    def __init__(self, query_parameters, *args, **kwargs):
        self.set_output_params(query_parameters)
        page_data = PageData(query_parameters.get("url"))
        ocx_graph = OCXGraph(page_data)
        schema_graph = SchemaGraph()
        self.define_consts()
        self.page_data = page_data # temp fix to get data to report from main
        self.ocx_graph = ocx_graph # also temp fix
        self.schema_graph = schema_graph

    def define_consts(self):
        self.primary_ocx_types = [
            SDO.Course,
            OER.Course,
            OER.Module,
            OER.Unit,
            OER.Lesson,
            OER.Activty,
            OER.Assessment,
            OER.SupportingMaterial,
            OER.SupplementalMaterial,
            OER.ReferencedMaterial,
            OCX.SupplementalMaterial,
            OCX.ReferencedMaterial,
        ]


    def set_output_params(self, query_parameters):
        try:
            if query_parameters.get("showTurtle") == "1":
                self.showTurtle = True
            else:
                self.showTurtle = False
        except:
            self.showTurtle = False
        try:
            if query_parameters.get("verbose") == "1":
                self.verbose = True
            else:
                self.verbose = False
        except:
            self.verbose = True



    def deduplicate(self, mylist):
        return list(dict.fromkeys(mylist))

    def find_parent_classes(self, aClass, parent_classes=[]):
        for parent_class in self.schema_graph.objects(aClass, RDFS.subClassOf):
            parent_classes.extend(parent_class)
            self.find_parent_classes(parent_class, parent_classes)
        return parent_classes

    def check_domain(self, s, p, ocx_graph):
        # totally borked
        # checks that s or superClass of s is in expected domain of p
        # return True if it is, False if not.
        expected_classes = self.schema_graph.objects(p, SDO.domainIncludes)
        subject_class = ocx_graph.objects(s, RDF.type)
        subject_class_path = [RDF.resource, subject_class]
        subject_class_path = subject_class_path.extend(
            self.find_parent_classes(subject_class)
        )
        for s_class in subject_class_path:
            if subject_class in expected_classes:
                return True
            else:
                pass
        return False

    def list_OCX_entities(self, ocx_graph):
        ocx_entities = []
        for aType in self.primary_ocx_types:
            ocx_entities.extend(ocx_graph.subjects(RDF.type, aType))
        return self.deduplicate(ocx_entities)

    def report_on_name(self, entity, ocx_graph):
        verbose = self.verbose
        name_report = ""
        c = 0
        for name in ocx_graph.objects(entity, SDO.name):
            if verbose:
                name_report = name_report + "PASS: Name exists.\n"
            if type(name).__name__ == "Literal":
                if verbose:
                    msg = "PASS: Name: is Literal.\n"
                    name_report = name_report + msg
                    name_report = name_report + "INFO: Name = " + name + "\n"
            else:
                msg = "WARNING: name is not a literal.\n"
            c += 1
        if c > 1:
            msg = "WARNING: having more than one name may be ambiguous, consider using sdo:alternateName\n"
            name_report = name_report + msg
        elif c < 1:
            msg = "WARNING no sdo.name found. Names are useful.\n"
            name_report = name_report + msg
        return name_report

    def report_on_desc(self, entity, ocx_graph):
        verbose = self.verbose
        desc_report = ""
        c = 0
        for desc in ocx_graph.objects(entity, SDO.description):
            if verbose:
                desc_report = desc_report + "PASS: Description exists.\n"
            if type(desc).__name__ == "Literal":
                if verbose:
                    msg = "PASS: Description is Literal.\n"
                    desc_report = desc_report + msg
                    desc_report = (
                        desc_report + "INFO: Description = " + desc[0:70] + "...\n"
                    )
            else:
                msg = "WARNING: description is not a literal.\n"
            c += 1
        if c > 1:
            msg = "WARNING: having more than one description may be ambiguous\n"
            desc_report = desc_report + msg
        elif c < 1:
            msg = "WARNING: no sdo.description found. Descriptions are useful but not essential.\n"
            desc_report = desc_report + msg
        return desc_report

    def report_on_type(self, entity, ocx_graph):
        verbose = self.verbose
        type_report = ""
        c = 0
        for t in ocx_graph.objects(entity, RDF.type):
            type_report = "INFO: RDF type: " + t + "\n"
            c += 1
            if t in self.schema_graph.subjects(RDF.type, RDFS.Class):
                label = self.schema_graph.label(t)
                parent = self.schema_graph.value(t, SDO.isPartOf, None)
                if parent:
                    pass
                else:
                    parent = "schema.org"
                if verbose:
                    msg = (
                        "PASS: This type is known to OCX as "
                        + label
                        + " from "
                        + parent
                        + "\n"
                    )
                    type_report = type_report + msg
            else:
                msg = "WARNING: This type is not known to OCX."
        if c == 0:
            msg = "WARNING: entity is of unspecified type.\n"
            type_report = type_report + msg
        return type_report

    def entity_report(self, entity, ocx_graph):
        entity_report = "\nReport on " + entity + "\n"
        entity_report = entity_report + self.report_on_name(entity, ocx_graph)
        entity_report = entity_report + self.report_on_desc(entity, ocx_graph)
        entity_report = entity_report + self.report_on_type(entity, ocx_graph)
        return entity_report

    def schema_label_string(self, entity, before="", after=""):
        label_string = ""
        for label_p_val in self.schema_graph.preferredLabel(entity):
            label_string = before + label_p_val[1] + after
        return label_string

    def get_parent_classes(self, t, parents):
        # given a class of type t, and optionally a list, it will append
        # the class of which t is a subClass to the list
        parents.append(t)
        for parent in self.schema_graph.objects(t, RDFS.subClassOf):
            parents = self.get_parent_classes(parent, parents)
        return parents

    def type_string(self, types: list):
        if len(types) == 0:
            return "[no known type]"
        types_string = ""
        for t in types:
            types_string = types_string + self.schema_label_string(t, "", ", ")
        types_string = types_string[:-2]
        return types_string

    def get_types(self, s, ocx_graph):
        type_name = ""
        types = []
        if type(s) is URIRef:
            for a_type in ocx_graph.objects(s, RDF.type):
                type_name = type_name + self.schema_label_string(a_type, "", ", ")
                types = self.get_parent_classes(a_type, types)
            types = self.deduplicate(types)
            if type_name == "":
                types = [SDO.URL]
                type_name = "URIRef"
        elif type(s) is BNode:
            for a_type in ocx_graph.objects(s, RDF.type):
                type_name = type_name + self.schema_label_string(a_type, "", ", ")
                types = self.get_parent_classes(a_type, types)
            types = self.deduplicate(types)
            if type_name == "":
                types = []
                type_name = "Untyped BNode"
        elif type(s) is Literal:
            types = [SDO.Text]
            type_string = "Text"
        else:
            types = []
            type_name = "failed to determine type"
            pass

        return type_name, types

    def subject_predicate_report(self, s, p, ocx_graph):
        valid_subject_types = []
        p_domain_labels = ""
        for p_domain in self.schema_graph.objects(p, SDO.domainIncludes):
            valid_subject_types.append(p_domain)
            p_domain_label = self.schema_label_string(p_domain, "", ", ")
            p_domain_labels = p_domain_labels + p_domain_label
        p_domain_labels = p_domain_labels[:-2]
        type_name, types = self.get_types(s, ocx_graph)
        types_string = self.type_string(types)
        s_name = ""
        for name in ocx_graph.objects(s, SDO.name):
            s_name = s_name + " " + name
        if s_name == "":
            s_name = "with no name"
        report = ""
        report = report + "INFO: used on object named " + s_name + "\n"
        report = report + "\t which is of type(s): " + types_string + "\n"
        report = report + "\t property has expected domain " + p_domain_labels + "\n"
        domain_valid = False
        for t in types:
            if t in valid_subject_types:
                domain_valid = True
        if domain_valid:
            if self.verbose:
                report = (
                    report + "PASS: subject type is in expected domain of property\n"
                )
        elif type(s) is BNode:
            report = (
                report
                + "FAIL: An untyped BNode object has been used where "
                + p_domain_labels
                + " was expected.\n\tPlease add object type.\n"
            )
        elif type(s) is URIRef:
            report = (
                report
                + "WARNING:  A URI reference for an object of unknown type has been used (it may not be on this page) where "
                + p_domain_labels
                + " was expected.\n\tYou should check the object at the end of the URI is of the right type.\n\tYou could add its type here to stop seeing this warning.\n"
            )
        else:
            report = (
                report + "FAIL: subject type is not in expected domain of property\n"
            )
        return report

    def predicate_object_report(self, p, o, ocx_graph):
        valid_object_types = []
        p_range_labels = ""
        for p_range in self.schema_graph.objects(p, SDO.rangeIncludes):
            valid_object_types.append(p_range)
            p_range_label = self.schema_label_string(p_range, "", ", ")
            p_range_labels = p_range_labels + p_range_label
        p_range_labels = p_range_labels[:-2]
        type_name, types = self.get_types(o, ocx_graph)
        range_valid = False
        for t in types:
            if t in valid_object_types:
                range_valid = True
        report = "INFO: points to object of type " + self.type_string(types) + "\n"
        report = report + "\t property has expected range " + p_range_labels
        report = report + "\n"
        if range_valid:
            if self.verbose:
                report = report + "PASS: object type is in expected range of property\n"
        elif type(o) is Literal:
            report = (
                report
                + "WARNING: Text has been used where "
                + p_range_labels
                + " was expected. This is not best practice.\n"
            )
        elif type(o) is BNode:
            report = (
                report
                + "FAIL: An untyped BNode object has been used where "
                + p_range_labels
                + " was expected.\n\tPlease add object type.\n"
            )
        elif type(o) is URIRef:
            report = (
                report
                + "WARNING: A URI reference for an object of unknown type has been used (it may not be on this page) where "
                + p_range_labels
                + " was expected.\n\tYou should check the object at the end of the URI is of the right type.\n\tYou could add its type here to stop seeing this warning.\n"
            )
        else:
            report = report + "FAIL: object type is not in expected range of property\n"
        return report

    def predicate_report(self, ocx_graph):
        report = "\n\n==Report on OCX predicates found:==\n"
        nsm = ocx_graph.namespace_manager
        for s, p, o in ocx_graph.triples((None, None, None)):
            if p in self.schema_graph.subjects(RDF.type, RDF.Property):
                p_name = self.schema_label_string(p, "", "")
                report = report + "\nReport on predicate in "
                report = (
                    report
                    + escape(s.n3(nsm))
                    + " "
                    + escape(p.n3(nsm))
                    + " "
                    + escape(o.n3(nsm))
                    + "\n"
                )
                report = report + self.subject_predicate_report(s, p, ocx_graph)
                report = report + self.predicate_object_report(p, o, ocx_graph)
        return report

    def make_report(self):
        page_data = self.page_data
        ocx_graph = self.ocx_graph
        self.report = "<pre><code>"
        self.report = self.report + "Requested URL:\t" + page_data.request_url + "\n"
        self.report = self.report + "Base URL:\t" + page_data.base_url + "\n"
        self.report = self.report + "Status code:\t" + page_data.status_code + "\n"
        self.report = (
            self.report
            + "\n=Reporting on Primary OCX Entities and all OCX predicates=\n"
        )
        if self.verbose:
            msg = "Verbose report. Add &verbose=0 URL parameter to show only errors and warnings.\n"
        else:
            msg = "Non-verbose report. Add &verbose=1 URL parameter to surpress info about tests passed.\n"
        self.report = self.report + msg
        primary_entities = self.list_OCX_entities(ocx_graph)
        self.report = (
            self.report
            + "\n==Primary OCX Entities found:==\n"
            + "\n\t".join(primary_entities)
            + "\n\n"
        )
        for entity in primary_entities:
            self.report = self.report + self.entity_report(entity, ocx_graph)
        self.report = self.report + self.predicate_report(ocx_graph)
        if self.showTurtle:
            turtle = ocx_graph.serialize(format="turtle").decode("utf-8")
            self.report = self.report + "Data:\n-----\n" + escape(turtle)
        self.report = self.report + "</code></pre>"
        return self.report
