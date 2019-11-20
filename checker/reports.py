from flask import render_template


class Report:
    def __init__(self, verbose):
        self.verbose = verbose
        self.html = render_template("head.html")

    def add_header(self, request_url, base_url, status_code):
        self.html = self.html + render_template(
            "header.html",
            request_url=request_url,
            base_url=base_url,
            status_code=status_code,
        )

    def end_report(self):
        self.html = self.html + render_template("foot.html")

    def sections(self, result):
        v = self.verbose
        for r in result["results"]:
            t = r["name"].replace(" ", "_") + ".html"
            self.html = self.html + render_template(t, results=r, verbose=v)

    def turtle(self, graph):
        t = "turtle.html"
        turtle = graph.serialize(format="turtle").decode("utf-8")
        turtle_report = render_template(t, turtle=turtle)
        self.html = self.html + turtle_report
