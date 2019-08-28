from rdflib import Graph

sdo_schema_location = "./schemas/schema_all.ttl"
sdo_schema_format = "turtle"
oer_schema_location = "./schemas/oerschema.ttl"
oer_schema_format = "turtle"
ocx_schema_location = "./schemas/ocx.ttl"
ocx_schema_format = "turtle"

class SchemaGraph(Graph):
    def __init__(self):
        super().__init__()
        try:
            self.parse(location=sdo_schema_location, format=sdo_schema_format)
        except:
            raise RuntimeError("cannot make graph of schema.org rdfs")
        try:
            self.parse(location=oer_schema_location, format=oer_schema_format)
        except:
            raise RuntimeError("cannot make graph of OERSchema rdfs")
        try:
            self.parse(location=ocx_schema_location, format=ocx_schema_format)
        except:
            raise RuntimeError("cannot make graph of OCX rdfs")
