from flask import render_template


class Reports:
    def __init__(self, verbose):
        self.verbose = verbose
        self.report = render_template("head.html")

    def header(self, request_url, base_url, status_code):
        self.report = self.report + render_template(
            "header.html",
            request_url=request_url,
            base_url=base_url,
            status_code=status_code,
        )

    def end_report(self):
        self.report = self.report + render_template("foot.html")

    def sections(self, result):
        v = self.verbose
        for r in result["results"]:
            t = r["name"].replace(" ", "_") + ".html"
            self.report = self.report + render_template(t, results=r, verbose=v)

    def turtle(self, graph):
        t = "turtle.html"
        turtle = graph.serialize(format="turtle").decode("utf-8")
        turtle_report = render_template(t, turtle=turtle)
        self.report = self.report + turtle_report
