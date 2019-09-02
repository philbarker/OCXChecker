# utility functions used by DataChecks kept here to declutter
from rdflib import Namespace, Literal, URIRef, BNode
from rdflib.namespace import RDF, RDFS

SDO = Namespace("http://schema.org/")


def deduplicate(self, mylist):
    return list(dict.fromkeys(mylist))


def schema_label_string(self, entity, before="", after=""):
    label_string = ""
    for label_p_val in self.schema_graph.preferredLabel(entity):
        label_string = before + label_p_val[1] + after
    return label_string


def type_string(self, types: list):
    if len(types) == 0:
        return "[no known type]"
    types_string = ""
    for t in types:
        types_string = types_string + self.schema_label_string(t, "", ", ")
    types_string = types_string[:-2]
    return types_string


def get_parent_classes(self, t, parents):
    # given a class of type t, and optionally a list, it will append
    # the class of which t is a subClass to the list it was given
    # and return the list
    parents.append(t)
    for parent in self.schema_graph.objects(t, RDFS.subClassOf):
        parents = self.get_parent_classes(parent, parents)
    return parents


def get_types(self, s):
    type_name = ""
    types = []
    if type(s) is URIRef:
        for a_type in self.graph.objects(s, RDF.type):
            type_name = type_name + self.schema_label_string(a_type, "", ", ")
            types = self.get_parent_classes(a_type, types)
        types = self.deduplicate(types)
        if type_name == "":
            types = [SDO.URL]
            type_name = "URIRef"
    elif type(s) is BNode:
        for a_type in self.graph.objects(s, RDF.type):
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
