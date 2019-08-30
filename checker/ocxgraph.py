from rdflib import Graph, Namespace
from rdflib.namespace import NamespaceManager

SDO = Namespace("http://schema.org/")
OER = Namespace("http://oerschema.org/")
OCX = Namespace("https://github.com/K12OCX/k12ocx-specs/")


class OCXGraph(Graph):
    def __init__(self, page_data):
        super().__init__()
        context = {
            "@context": {
                "@base": page_data.base_url,
                "sdo": "http://schema.org/",
                "oer": "http://oerschema.org/",
            }
        }
        data = page_data.data
        if data != "[]":
            self.parse(data=data, format="json-ld", context=context)
            self.bind("sdo", SDO)
            self.bind("oer", OER)
            self.bind("ocx", OCX)
        else:
            msg = "No data extracted from page at " + page_data.request_url
            raise RuntimeError(msg)
