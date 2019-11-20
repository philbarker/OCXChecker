from rdflib import Graph
from glob import glob

schema_location = "./schemas/"


class SchemaGraph(Graph):
    """read in the RDFschema from hard coded file locations and build graph"""

    def __init__(self):
        """read in the schema files from the hard coded file location and build graph"""
        super().__init__()
        ttl_schema_files = glob(schema_location + "*.ttl")
        for ttl_file in ttl_schema_files:
            try:
                self.parse(location=ttl_file, format="turtle")
            except:
                raise RuntimeError("cannot make graph of " + ttl_file)
