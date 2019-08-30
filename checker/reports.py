from flask import render_template


def make_report(self, results):
    # refactor this into reports.py to set report of Reports
    report = Reports(self.verbose)
    report.header(
        self.page_data.request_url, self.page_data.base_url, self.page_data.status_code
    )
    report.sections(results)
    report.turtle(self.ocx_graph)
    report.end_report
    return report.report


class Reports:
    def __init__(self, verbose):
        self.verbose = verbose
        self.report = render_template("head.html")

    def header(self, request_url, base_url, status_code):
        self.report = render_template(
            "header.html",
            request_url=request_url,
            base_url=base_url,
            status_code=status_code,
        )

    def end_report(self):
        self.report = self.report + render_template("foot.html")

    def sections(self, results):
        v = self.verbose
        for key in results:
            t = key + ".html"
            data = results[key]
            self.report = self.report + render_template(t, results=data, verbose=v)

    def turtle(self, graph):
        t = "turtle.html"
        turtle = graph.serialize(format="turtle").decode("utf-8")
        turtle_report = render_template(t, turtle=turtle)
        self.report = self.report + turtle_report
