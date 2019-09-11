import pytest, pprint
from rdflib import URIRef, Namespace, Literal
from rdflib.namespace import RDF
from checker import OCXGraph
from json.decoder import JSONDecodeError

SDO = Namespace("http://schema.org/")

def test_init():
    data = '[]'
    url = 121
    with pytest.raises(RuntimeError):
        g = OCXGraph(data, url)
    url = 'http://example.org/'
    with pytest.raises(RuntimeError):
        g = OCXGraph(data, url)
    data = None
    with pytest.raises(RuntimeError):
        g = OCXGraph(data, url)
    data = '[{"@context": "http://schema.org/", "@id": "http://example.org/1", "@type": "Thing", "name": "Something"} {"@context": "http://schema.org/", "@id": "http://example.org/2", "@type": "Thing"} {"@context": "http://schema.org/", "@id": "http://example.org/2", "name": "Another thing"}]'
    with pytest.raises(JSONDecodeError):
        g = OCXGraph(data, url)
    data = '[{"@context": "http://schema.org/", "@id": "http://example.org/1", "@type": "Thing", "name": "Something"}, {"@context": "http://schema.org/", "@id": "http://example.org/2", "@type": "Thing"}, {"@id": "http://example.org/2", "http://schema.org/name": "Another thing"}]'
    g = OCXGraph(data, url)
    s1 = URIRef(u'http://example.org/1')
    s2 = URIRef(u'http://example.org/2')
    assert SDO.Thing == g.value(s1, RDF.type, None)
    assert Literal(u'Something') == g.value(s1, SDO.name, None)
    assert SDO.Thing == g.value(s2, RDF.type, None)
    assert Literal(u'Another thing') == g.value(s2, SDO.name, None)
