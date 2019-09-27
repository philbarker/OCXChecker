from checker import CheckResult, DataChecks
from pprint import PrettyPrinter  # used for debugging tests

pp = PrettyPrinter(indent=4)


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


from rdflib import Graph, URIRef, Literal, BNode

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
    result = dc.find_primary_entities([])
    assert result["name"] == "primary entities present"
    assert result["description"] == "check that there is at least one primary entity"
    assert result["info"] == []
    assert not result["passes"]
    primary_types = [URIRef(u"http://schema.org/BusTrip")]
    result = dc.find_primary_entities(primary_types)
    assert result["info"] == []
    assert not result["passes"]
    primary_types = [URIRef(u"http://oerschema.org/Lesson")]
    lesson = URIRef(u"http://example.org/#Lesson")
    result = dc.find_primary_entities(primary_types)
    assert result["passes"]
    assert lesson in result["info"]


def test_subject_predicate_check():
    # test for no subject and no predicate passed to checker
    s = None
    p = None
    result = dc.subject_predicate_check(s, p)
    assert not result["passes"]
    assert result["info"][0] == "predicate must be a URI"
    assert result["info"][1] == "subject must be a URI or BNode"
    # test for subject and predicate not in schema graph
    s = URIRef(u"http://example.org/nothing")
    p = URIRef(u"http://example.org/nonsense")
    result = dc.subject_predicate_check(s, p)
    assert result["passes"]
    w = "not checked: predicate not in schema graph"
    assert result["warnings"][0] == w
    # test for predicate used on subject of unknown type
    s = URIRef(u"http://example.org/#NoType")
    p = URIRef(u"http://schema.org/name")
    result = dc.subject_predicate_check(s, p)
    assert result["passes"]
    assert result["info"] == [
        "used on subject named  atypical",
        "subject is of type [no label]",
        "property has expected domain Thing",
    ]
    assert result["warnings"][0][:20] == "a URI reference for "
    # test for predicate used on subject of known invalid type
    s = URIRef(u"http://example.org/#Lesson")
    p = URIRef(u"http://schema.org/foundingDate")
    result = dc.subject_predicate_check(s, p)
    assert not result["passes"]
    assert result["warnings"] == []
    expected0 = "used on subject named  Lecture 1: Per..."
    expected1 = "subject is of type..."  # order of types listed will vary
    expected2 = "property has expected domain Organization"
    expected3 = "subject is of type that is not in predicate's domain"
    assert result["info"][0][:25] == expected0[:25]
    assert result["info"][1][:15] == expected1[:15]
    assert result["info"][2] == expected2
    assert result["info"][3] == expected3
    # test for predicate used on subject of known invalid type
    s = URIRef(u"http://example.org/#Douglas")
    p = URIRef(u"http://schema.org/hasPart")
    result = dc.subject_predicate_check(s, p)
    assert not result["passes"]

    # tests for predicate used on subject of known valid type
    s = URIRef(u"http://example.org/#Lesson")
    p = URIRef(u"http://schema.org/about")
    result = dc.subject_predicate_check(s, p)
    assert result["passes"]
    assert result["warnings"] == []
    s = URIRef(u"http://example.org/#Lesson")
    p = URIRef(u"http://schema.org/name")
    result = dc.subject_predicate_check(s, p)
    assert result["passes"]
    assert result["warnings"] == []


def test_predicate_object_check():
    # test for no predicate and object
    p = None
    o = None
    result = dc.predicate_object_check(p, o)
    assert not result["passes"]
    assert result["warnings"] == ["object type not known"]
    assert result["info"][0] == "predicate must be a URI"
    assert result["info"][1] == "object must be a URI, BNode or Literal"
    # tests for predicate used with object of known valid type
    p = URIRef(u"http://schema.org/hasPart")
    o = URIRef(u"http://example.org/#Lesson")
    result = dc.predicate_object_check(p, o)
    assert result["passes"]
    assert result["warnings"] == []
    assert result["info"][0] == "property has expected range CreativeWork"
    # tests for predicate used with valid Literal object
    p = URIRef(u"http://schema.org/name")
    o = Literal(u"Douglas")
    result = dc.predicate_object_check(p, o)
    assert result["passes"]
    assert result["warnings"] == []
    assert result["info"][0] == "property has expected range Text"
    # tests for predicate used with valid BNode object, but unknown type
    p = URIRef(u"http://schema.org/hasPart")
    o = BNode()
    result = dc.predicate_object_check(p, o)
    assert result["passes"]
    assert result["info"][0] == "property has expected range CreativeWork"
    assert result["warnings"][0] == "object type not known"
    # tests for predicate used with valid URIRef object, but unknown type
    p = URIRef(u"http://schema.org/hasPart")
    o = URIRef(u"http://example.org/part")
    result = dc.predicate_object_check(p, o)
    assert result["passes"]
    assert result["info"][0] == "property has expected range CreativeWork"
    assert result["warnings"][0] == "object type not known"
    # tests for predicate used with object of invalid type
    p = URIRef(u"http://schema.org/name")
    o = URIRef(u"http://example.org/#LectureVideo")
    result = dc.predicate_object_check(p, o)
    assert not result["passes"]
    assert result["info"][0] == "property has expected range Text"
    assert result["info"][1][:25] == "points to object of type "
    assert result["warnings"] == []
    # tests for predicate used with literal object when expecting some type
    p = URIRef(u"http://schema.org/hasPart")
    o = Literal(u"Douglas")
    result = dc.predicate_object_check(p, o)
    assert result["passes"]
    assert result["info"] == [
        "property has expected range CreativeWork",
        "points to object of type Text",
    ]
    assert result["warnings"] == [
        "text has been used where CreativeWork was expected. This is not best practice"
    ]


def test_check_predicate():
    # most of the detailed tests have been done for testing predicate_object and subject_predicate checks, so here only test that these get called  & returned correctly
    # all pass
    (s, p, o) = (
        URIRef(u"http://example.org/#Lesson"),
        URIRef(u"http://schema.org/hasPart"),
        URIRef(u"http://example.org/#LectureVideo"),
    )
    result = dc.check_predicate(s, p, o)
    assert result["name"] == "predicate check for " + p
    assert (
        result["description"] == "subject and object are in expected domain and range"
    )
    assert result["results"][0]["passes"]
    assert result["results"][1]["passes"]
    assert result["passes"]
    # s - p fails
    (s, p, o) = (
        URIRef(u"http://example.org/#Douglas"),
        URIRef(u"http://schema.org/hasPart"),
        URIRef(u"http://example.org/#LectureVideo"),
    )
    result = dc.check_predicate(s, p, o)
    assert not result["results"][0]["passes"]
    assert result["results"][1]["passes"]
    assert not result["passes"]
    # p - o fails
    (s, p, o) = (
        URIRef(u"http://example.org/#Lesson"),
        URIRef(u"http://schema.org/hasPart"),
        URIRef(u"http://example.org/#Douglas"),
    )
    result = dc.check_predicate(s, p, o)
    assert result["results"][0]["passes"]
    assert not result["results"][1]["passes"]
    assert not result["passes"]
    # all fails
    (s, p, o) = (
        URIRef(u"http://example.org/#Douglas"),
        URIRef(u"http://schema.org/hasPart"),
        URIRef(u"http://example.org/#Douglas"),
    )
    result = dc.check_predicate(s, p, o)
    assert not result["results"][0]["passes"]
    assert not result["results"][1]["passes"]
    assert not result["passes"]


def test_check_all_predicates():
    result = dc.check_all_predicates()
    d = "subjects are in predicates' domains, and objects are in predicates' ranges for all statements"
    assert not result["passes"]
    assert result["name"] == "predicate checks"
    assert result["description"] == d
    assert result["info"] == []
    assert result["warnings"] == ["warnings were generated"]


def test_check_entity_name():
    # passes
    e = URIRef("http://example.org/#Douglas")
    result = dc.check_entity_name(e)
    d = "entity has at least one name property, name is a string"
    assert result["passes"]
    assert result["name"] == "Check entity name"
    assert result["description"] == d
    assert result["info"] == ["Name = Douglas"]
    assert result["warnings"] == []
    # no entity
    e = None
    result = dc.check_entity_name(e)
    assert not result["passes"]
    assert result["info"] == ["entity variable not URIRef or BNode"]
    assert result["warnings"] == []
    # no name
    e = URIRef("http://example.org/#Ref")
    result = dc.check_entity_name(e)
    assert not result["passes"]
    assert result["info"] == ["No sdo.name found. Names are useful."]
    assert result["warnings"] == []
    # two names
    e = URIRef("http://example.org/#Ref2")
    result = dc.check_entity_name(e)
    w = "Having more than one name may be ambiguous, consider using sdo:alternateName."
    assert result["passes"]
    assert "Name = reference material" in result["info"]
    assert "Name = with 2 names" in result["info"]
    assert result["warnings"] == [w]
    # non-literal name
    e = URIRef("http://example.org/#Ref3")
    result = dc.check_entity_name(e)
    assert not result["passes"]
    assert "name is not a literal" in result["info"]
    assert result["warnings"] == []


def test_check_entity_description():
    # passes
    e = URIRef("http://example.org/#Douglas")
    result = dc.check_entity_description(e)
    d = "description is string or absent"
    assert result["passes"]
    assert result["name"] == "check entity description"
    assert result["description"] == d
    assert result["info"] == ["Description = in the jungle"]
    assert result["warnings"] == []
    # no entity
    e = None
    result = dc.check_entity_description(e)
    assert not result["passes"]
    assert result["info"] == ["entity variable not URIRef or BNode"]
    assert result["warnings"] == []
    # no description
    e = URIRef("http://example.org/#Ref")
    result = dc.check_entity_description(e)
    assert result["passes"]
    assert result["info"] == []
    assert result["warnings"] == ["No sdo.description found. Descriptions are useful."]
    # two descriptions
    e = URIRef("http://example.org/#Ref2")
    result = dc.check_entity_description(e)
    assert result["passes"]
    assert "Description = reference material" in result["info"]
    assert "Description = with 2 descriptions" in result["info"]
    assert result["warnings"] == ["Having more than one description may be ambiguous."]
    # non-literal description
    e = URIRef("http://example.org/#Ref3")
    result = dc.check_entity_description(e)
    assert not result["passes"]
    assert result["info"] == ["Description is not a literal"]
    assert result["warnings"] == []


def test_check_entity_type():
    # passes
    e = URIRef("http://example.org/#Lesson")
    result = dc.check_entity_type(e)
    assert result["passes"]
    i1 = "this type is known as Course from oerschema.org"
    i2 = "this type is known as Lesson from oerschema.org"
    assert result["name"] == "check entity type"
    assert result["description"] == "entity has known RDF:type"
    assert i1 in result["info"]
    assert i2 in result["info"]
    assert result["warnings"] == []
    # no entity
    e = None
    result = dc.check_entity_type(e)
    assert not result["passes"]
    assert result["info"] == ["entity variable not URIRef or BNode"]
    assert result["warnings"] == []
    # no type
    e = URIRef("http://example.org/#NoType")
    result = dc.check_entity_type(e)
    assert not result["passes"]
    assert result["info"] == ["this entity is of unspecified type."]
    assert result["warnings"] == []
    # unknown type
    e = URIRef("http://example.org/#Ref4")
    result = dc.check_entity_type(e)
    assert result["passes"]
    assert result["info"] == []
    assert result["warnings"] == ["this type is unknown"]


def test_check_entity_ndt():
    # the checks for name, description and test have been tested, test here that they are called correctly and results returned.
    # no entity
    e = None
    result = dc.check_entity_ndt(e)
    d = "entity None has name, description and type"
    assert not result["passes"]
    assert result["name"] == "check entity None"
    assert result["description"] == d
    assert result["info"] == ["entity variable not URIRef or BNode"]
    # passing entity
    e = URIRef(u"http://example.org/#Lesson")
    result = dc.check_entity_ndt(e)
    d = "entity http://example.org/#Lesson has name, description and type"
    assert result["name"] == "check entity http://example.org/#Lesson"
    assert result["description"] == d
    assert result["passes"]
    assert result["warnings"] == []
    assert result["info"] == []
    # failing entity
    e = URIRef(u"http://example.org/#Ref3")
    result = dc.check_entity_ndt(e)
    assert not result["passes"]


def test_check_all_ided_entities():
    # this calls check_entity_ndt which has alread been checked.
    result = dc.check_all_ided_entities()
    n = "check of all indentified entities"
    d = "entities with URI have name, description and type"
    assert result["name"] == n
    assert result["description"] == d
    assert len(result["results"]) == 7
    assert result["info"] == []
    assert result["warnings"] == ["warnings were generated"]
