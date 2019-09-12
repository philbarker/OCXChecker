from checker.checkutils import *
from rdflib import Graph, URIRef, BNode, Literal

sg = Graph()  # use OCX RDFS as schema graph b/c it is small
sg.parse(location="tests/input/ocx.ttl", format="turtle")
dg = Graph()  # a data graph for tests
dg.parse(location="tests/input/data.ttl", format="turtle")


def test_deduplicate():
    a_list = ["a", "a", "b", "c"]
    expected = ["a", "b", "c"]
    assert deduplicate(a_list) == expected


def test_schema_label_string():
    e = URIRef(u"https://github.com/K12OCX/k12ocx-specs/ReferencedMaterial")
    l = schema_label_string(sg, e, before="^", after="$")
    assert l == "^ReferencedMaterial$"
    e = URIRef(u"https://schema.org/name")  # not in g
    l = schema_label_string(sg, e, before="^", after="$")
    assert l == "^[no label]$"


def test_labels_string():
    t1 = URIRef(u"https://github.com/K12OCX/k12ocx-specs/ReferencedMaterial")
    t2 = URIRef(u"https://github.com/K12OCX/k12ocx-specs/SupplementalMaterial")
    s = labels_string(sg, [t1, t2])
    assert s == "ReferencedMaterial, SupplementalMaterial"
    s = labels_string(sg, [])
    assert s == "[no known type]"
    t = URIRef(u"https://schema.org/name")  # not in g
    s = labels_string(sg, [t, t1])
    assert s == "[no label], ReferencedMaterial"


def test_get_parent_classes():
    t = URIRef(u"https://github.com/K12OCX/k12ocx-specs/ReferencedMaterial")
    parents = get_parent_classes(sg, t, [])
    expected_parents = [
        URIRef(u"http://oerschema.org/AssociatedMaterial"),
        URIRef(u"http://oerschema.org/LearningComponent"),
        URIRef(u"http://schema.org/CreativeWork"),
    ]
    for p in expected_parents:
        assert p in parents
    t = URIRef(u"https://schema.org/name")  # not in g
    parents = get_parent_classes(sg, t, [])
    assert parents == [t]


def test_get_types():
    s = URIRef(u"http://example.org/#Ref")
    (type_name, types) = get_types(dg, sg, s)
    expected_types = [
        URIRef("http://schema.org/CreativeWork"),
        URIRef("https://github.com/K12OCX/k12ocx-specs/ReferencedMaterial"),
        URIRef("http://oerschema.org/AssociatedMaterial"),
    ]
    assert type_name == "ReferencedMaterial"
    for t in expected_types:
        assert t in types
    s = URIRef(u"http://example.org/#NoType")
    (type_name, types) = get_types(dg, sg, s)
    assert type_name == "URIRef"
    assert [URIRef("http://schema.org/URL")] == types
    s = BNode("blank")
    (type_name, types) = get_types(dg, sg, s)
    assert type_name == "Untyped BNode"
    assert [] == types
    s = Literal("literally just text")
    (type_name, types) = get_types(dg, sg, s)
    assert type_name == "Text"
    assert [URIRef("http://schema.org/Text")] == types
    s = "Nonesense"
    (type_name, types) = get_types(dg, sg, s)
    assert type_name == "failed to determine type"
    assert [] == types
