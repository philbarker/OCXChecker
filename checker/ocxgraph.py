from rdflib import Graph, Namespace
from rdflib.namespace import NamespaceManager

SDO = Namespace("http://schema.org/")
OER = Namespace("http://oerschema.org/")
OCX = Namespace("https://github.com/K12OCX/k12ocx-specs/")


class OCXGraph(Graph):
    """Create a rdflib.Graph from a JSON-LD string."""

    def __init__(self, data: str, url: str):
        """Create a rdflib.Graph from a JSON-LD string."""
        super().__init__()
        if type(url) is str:
            context = {
                "@context": {
                    "@base": url,
                    "sdo": "http://schema.org/",
                    "oer": "http://oerschema.org/",
                }
            }
        else:
            msg = "URL was not a string."
            raise RuntimeError(msg)
        if type(data) is str and data != "[]":
            self.parse(data=data, format="json-ld", context=context)
            self.bind("sdo", SDO)
            self.bind("oer", OER)
            self.bind("ocx", OCX)
        else:
            msg = "No data extracted from page" + url
            raise RuntimeError(msg)
