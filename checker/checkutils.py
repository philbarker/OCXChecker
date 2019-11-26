# utility functions used by DataChecks kept here to declutter
from rdflib import Namespace, Literal, URIRef, BNode
from rdflib.namespace import RDF, RDFS, OWL

SDO = Namespace("http://schema.org/")


def deduplicate(mylist):
    """Remove duplicate items from a list."""
    return list(dict.fromkeys(mylist))


def schema_label_string(graph, entity, before="", after=""):
    """Return a preferred label of an entity in a graph.

       Given a graph with labels in RDFS or SKOS return the preferred label
       of that entity, optionally with some text before and/or after. If >1
       preferred label is present return the first one. If no label will
       use '[no label]' instead
    """
    label_string = ""
    try:
        (prop, label) = graph.preferredLabel(entity)[0]
        label_string = before + label + after
    except:
        label_string = before + '[no label]' + after
    return label_string


def labels_string(graph, entities: list):
    """Return a string of comma separated labels when given a list of entities in a graph."""
    if len(entities) == 0:
        return "[no known type]"
    labels_string = ""
    for t in entities:
        labels_string = labels_string + schema_label_string(graph, t, "", ", ")
    labels_string = labels_string[:-2]  # remove trailing ', '
    return labels_string


def get_parent_classes(graph, t, p):
    """Return a list of the classes of which a class is a subtype.

       Given a class t, and a list, it will append the class
       of which t is a subClass to the list it was given and then recursively
       call itself for each of the parent classes of t until it reaches
       a class with no parent. Oddly, the list of 'parents' will always include
       the initial child class.
    """
    parents = p
    parents.append(t)
    for parent in graph.objects(t, RDFS.subClassOf):
        parents = get_parent_classes(graph, parent, parents)
    sib_rels = [OWL.equivalentClass, OWL.sameAs]
    sibs = []
    for rel in sib_rels:
        for sib in graph.subjects(rel, t):
            sibs.append(sib)
        for sib in graph.subjects(t, rel):
            sibs.append(sib)
    for sibling in sibs:
        parents.append(sibling)
        for parent in graph.objects(sibling, RDFS.subClassOf):
            parents = get_parent_classes(graph, parent, parents)
    return parents


def get_types(data_graph, schema_graph, e):
    """Return a list of the types of an entity and their parent-types, and string with the names of those types."""
    type_labels = ""
    types = []
    if type(e) is URIRef:
        for a_type in schema_graph.objects(e, RDF.type):
            type_labels = type_labels + schema_label_string(
                schema_graph, a_type, "", ", "
            )
            types = get_parent_classes(schema_graph, a_type, types)
        for a_type in data_graph.objects(e, RDF.type):
            type_labels = type_labels + schema_label_string(
                schema_graph, a_type, "", ", "
            )
            types = get_parent_classes(schema_graph, a_type, types)
        types = deduplicate(types)
        if type_labels == "":
            types = [RDFS.Resource, SDO.Thing]
            type_labels = "untyped URIRef"
        else:
            types.append(RDFS.Resource)
            type_labels = type_labels[:-2]
    elif type(e) is BNode:
        for a_type in schema_graph.objects(e, RDF.type):
            type_labels = type_labels + schema_label_string(
                schema_graph, a_type, "", ", "
            )
            types = get_parent_classes(schema_graph, a_type, types)
        for a_type in data_graph.objects(e, RDF.type):
            type_labels = type_labels + schema_label_string(
                schema_graph, a_type, "", ", "
            )
            types = get_parent_classes(schema_graph, a_type, types)
        types = deduplicate(types)
        if type_labels == "":
            types = [RDFS.Resource, SDO.Thing]
            type_labels = "untyped BNode"
        else:
            types.append(RDFS.Resource)
            type_labels = type_labels[:-2]
    elif type(e) is Literal:
        types = [SDO.Text]
        type_labels = "Text"
    else:
        types = []
        type_labels = "untyped: failed to determine type"
    return type_labels, types
