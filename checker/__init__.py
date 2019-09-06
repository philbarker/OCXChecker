from rdflib import Namespace
from .pagedata import PageData
from .ocxgraph import OCXGraph
from .schemagraph import SchemaGraph
from .datachecks import DataChecks, CheckResult
from .reports import Report

SDO = Namespace("http://schema.org/")
OER = Namespace("http://oerschema.org/")
OCX = Namespace("https://github.com/K12OCX/k12ocx-specs/")

primary_ocx_types = [
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


class Checker:
    """ Comprises the page retrieved from the request url,
        the Graph of JSON-LD extracted from that page, a Graph of
        the RDFS for vocabularies used, plus various parameters and
        properties such as namespace URIs, with methods for checking
        these & reporting on the checks.
    """

    def __init__(self, query_parameters, *args, **kwargs):
        self.set_output_params(query_parameters)
        self.page_data = PageData(query_parameters.get("url"))
        self.ocx_graph = OCXGraph(self.page_data)
        self.schema_graph = SchemaGraph()

    def do_checks(self):
        checks = DataChecks(self.ocx_graph, self.schema_graph)
        result = CheckResult(
            n="All checks",
            d="checks on findings primary entities, properties of names entities and subject and object of all predicates",
            p=True,
        )
        result.add_result(checks.find_primary_entities(primary_ocx_types))
        result.add_result(checks.check_all_named_entities())
        result.add_result(checks.check_all_predicates())
        return result

    def make_report(self, result):
        report = Report(self.verbose)
        report.header(
            self.page_data.request_url,
            self.page_data.base_url,
            self.page_data.status_code,
        )
        report.sections(result)
        report.turtle(self.ocx_graph)
        report.end_report
        return report

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
