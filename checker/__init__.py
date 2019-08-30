from rdflib import Namespace
from .pagedata import PageData
from .ocxgraph import OCXGraph
from .schemagraph import SchemaGraph

SDO = Namespace("http://schema.org/")
OER = Namespace("http://oerschema.org/")
OCX = Namespace("https://github.com/K12OCX/k12ocx-specs/")


class Checker:
    """ Comprises the page retrieved from the request url,
        the Graph of JSON-LD extracted from that page, a Graph of
        the RDFS for vocabularies used, plus various parameters and
        properties such as namespace URIs, with methods for checking
        these & reporting on the checks.
    """

    from .datachecks import DataChecks, do_checks
    from .reports import Reports, make_report

    def __init__(self, query_parameters, *args, **kwargs):
        self.set_output_params(query_parameters)
        self.page_data = PageData(query_parameters.get("url"))
        self.ocx_graph = OCXGraph(self.page_data)
        self.define_consts()
        self.schema_graph = SchemaGraph()

    def define_consts(self):
        self.primary_ocx_types = [
            SDO.Course,
            OER.Course,
            OER.Module,
            OER.Unit,
            OER.Lesson,
            OER.Activty,
            OER.Assessment,
            OER.SupportingMaterial,
            OER.SupplementalMaterial,
            OER.ReferencedMaterial,
            OCX.SupplementalMaterial,
            OCX.ReferencedMaterial,
        ]

    def set_output_params(self, query_parameters):
        try:
            if query_parameters.get("showTurtle") == "1":
                self.showTurtle = True
            else:
                self.showTurtle = False
        except:
            self.showTurtle = False
        try:
            if query_parameters.get("verbose") == "1":
                self.verbose = True
            else:
                self.verbose = False
        except:
            self.verbose = True
