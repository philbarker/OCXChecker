from checker import CheckResult, DataChecks


def test_CheckResults():
    """test the workings of the CheckResult class and its methods"""
    cr = CheckResult(n="test", d="test results of a test", p=False)
    assert type(cr) == CheckResult
    assert cr["name"] == "test"
    assert cr["description"] == "test results of a test"
    assert not cr["passes"]
    cr.set_passes(True)
    assert cr["passes"]
    cr.set_passes(False)
    assert not cr["passes"]
    cr.add_info("info")
    cr.add_warning("warn")
    assert cr["info"] == ["info"]
    assert cr["warnings"] == ["warn"]
    cr.add_info(["info", "info"])
    cr.add_warning(["warn", "warn"])
    assert cr["info"] == ["info", "info", "info"]
    assert cr["warnings"] == ["warn", "warn", "warn"]
    cr.add_info([])
    cr.add_warning([])
    assert cr["info"] == ["info", "info", "info"]
    assert cr["warnings"] == ["warn", "warn", "warn"]
    cr.add_info(None)
    cr.add_warning(None)
    assert cr["info"] == ["info", "info", "info"]
    assert cr["warnings"] == ["warn", "warn", "warn"]
    cr.add_result(cr)  # results all the way down
    assert cr["results"][0]["name"] == "test"
    assert cr["results"][0]["description"] == "test results of a test"
    assert not cr["results"][0]["passes"]
    assert cr["results"][0]["info"] == ["info", "info", "info"]
    assert cr["results"][0]["warnings"] == ["warn", "warn", "warn"]


from rdflib import Graph, URIRef

sg = Graph()  # use OCX RDFS as schema graph b/c it is small
sg.parse(location="tests/input/schema.ttl", format="turtle")
dg = Graph()  # a data graph for tests
dg.parse(location="tests/input/data.ttl", format="turtle")
dc = DataChecks(dg, sg)


def test_init():
    assert type(dc) == DataChecks
    assert len(dc.graph) == len(dg)
    assert dc.schema_graph.isomorphic(sg)  # will fail if BNodes in sg


def test_find_primary_entities():
    results = dc.find_primary_entities([])
    assert results["name"] == "primary entities present"
    assert results["description"] == "check that there is at least one primary entity"
    assert results["info"] == []
    assert not results["passes"]
    primary_types = [URIRef(u"http://schema.org/BusTrip")]
    results = dc.find_primary_entities(primary_types)
    assert results["info"] == []
    assert not results["passes"]
    primary_types = [URIRef(u"http://oerschema.org/Lesson")]
    lesson = URIRef(u"http://example.org/#Lesson")
    results = dc.find_primary_entities(primary_types)
    assert results["passes"]
    assert lesson in results["info"]


def test_subject_predicate_check():
    s = None
    p = None
    results = dc.subject_predicate_check(s, p)
    assert not results["passes"]
    assert results["info"][0] == "predicate must be a URI"
    assert results["info"][1] == "subject must be a URI or BNode"
    s = URIRef(u"http://example.org/nothing")
    p = URIRef(u"http://example.org/nonsense")
    results = dc.subject_predicate_check(s, p)
    assert results["passes"]
    expected_warning = "not checked: predicate not in schema graph"
    assert results["warnings"][0] == expected_warning
    s = URIRef(u"http://example.org/#NoType")
    p = URIRef(u"http://schema.org/name")
    results = dc.subject_predicate_check(s, p)
    assert results["passes"]
    assert results["info"] == [
        "used on subject named  atypical",
        "subject is of type [no label]",
        "property has expected domain Thing",
    ]
    assert results["warnings"][0][:20] == "a URI reference for "
    s = URIRef(u"http://example.org/#Lesson")
    p = URIRef(u"http://schema.org/about")
    results = dc.subject_predicate_check(s, p)
    assert results["passes"]
    assert results["warnings"] == []
    s = URIRef(u"http://example.org/#Lesson")
    p = URIRef(u"http://schema.org/foundingDate")
    results = dc.subject_predicate_check(s, p)
    assert not results["passes"]
    assert results["warnings"] == []
    expected0 = "used on subject named  Lecture 1: Per..."
    expected1 = "subject is of type..." # order of types listed will vary
    expected2 =  "property has expected domain Organization"
    expected3 = "subject is of type that is not in predicate's domain"
    assert results["info"][0][:25] == expected0[:25]
    assert results["info"][1][:15] == expected1[:15]
    assert results["info"][2] == expected2
    assert results["info"][3] == expected3
    s = URIRef(u"http://example.org/#Lesson")
    p = URIRef(u"http://schema.org/name")
    results = dc.subject_predicate_check(s, p)
    assert results["passes"]
    assert results["warnings"] == []
