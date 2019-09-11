from checker import SchemaGraph
from rdflib import Graph, URIRef, Namespace, Literal
from rdflib.namespace import RDF, RDFS

SDO = Namespace("http://schema.org/")
OER = Namespace("http://oerschema.org/")
OCX = Namespace("https://github.com/K12OCX/k12ocx-specs/")

def test_init():
    g = SchemaGraph()
    assert type(g) == SchemaGraph
    assert isinstance(g, Graph) # we got a graph!
    expected_labels = [(RDFS.label, Literal('CreativeWork'))]
    # graph has schema.org info in it
    assert g.preferredLabel(SDO.CreativeWork) == expected_labels
    classes = []
    # graph has oerschema info in it
    for c in g.objects(OER.Assessment, RDFS.subClassOf):
        classes.append(c)
    for c in [SDO.Action, OER.InstructionalPattern]:
        assert c in classes
    # graph has ocx info in it
    c = g.value(OCX.SupplementalMaterial, RDFS.subClassOf, None)
    assert OER.AssociatedMaterial == c
