from flask import Flask, request
from checker import Checker

app = Flask(__name__)


@app.route("/")
def checker():
    checker = Checker(request.args)
    #    return checker.make_report_0()
    results = checker.do_checks()
    report = checker.make_report(results)
    return report


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


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
