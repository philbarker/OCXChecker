from flask import Flask, request
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


def create_app(test_config=None):
    # create and configure the app
    # from https://flask.palletsprojects.com/en/1.1.x/tutorial/factory/
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # a simple page that says hello
    @app.route("/hello")
    def hello():
        return "Hello, World!"

    @app.route("/")
    def checker():
        checker = Checker(request.args)
        result = checker.do_checks()
        report = checker.make_report(result)
        return report.html

    @app.route("/info")
    def info():
        info = "Usage <host>:8080?url=<url>&showTurtle=True\n"
        info = (
            info
            + "e.g. "
            + request.host_url
            + "?url=https://philbarker.github.io/OCXPhysVibWav/l1/\n"
        )
        info = info + "Running on python version" + version
        return escape(info)

    return app


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
        self.ocx_graph = OCXGraph(self.page_data.data, self.page_data.base_url)
        self.schema_graph = SchemaGraph()

    def do_checks(self):
        checks = DataChecks(self.ocx_graph, self.schema_graph)
        result = CheckResult(
            n="All checks",
            d="checks on findings primary entities, properties of names entities and subject and object of all predicates",
            p=True,
        )
        result.add_result(checks.find_primary_entities(primary_ocx_types))
        result.add_result(checks.check_all_ided_entities())
        result.add_result(checks.check_all_predicates())
        return result

    def make_report(self, result):
        report = Report(self.verbose)
        report.add_header(
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
