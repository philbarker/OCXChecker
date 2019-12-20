import pprint
from requests import get

pp = pprint.PrettyPrinter(indent=4)  # used for debugging


def test_integration(test_client):
    url = "https://pjjk.net/ldchecker/demo.html"
    response = test_client.get("/check?url=" + url)
    # many lines in output are not stable (results order is not fixed),
    # here are some to check that are fixed.
    expected_response_snippets = [
        "<title>OCXChecker alpha</title>",
        "<li><strong>Returned URL:</strong> https://pjjk.net/ldchecker/demo.html </li>",
        "<li><strong>Status code:</strong>  200 </li>",
        "<li><strong>Returned URL:</strong> https://pjjk.net/ldchecker/demo.html </li>",
        '<em class="fail">FAIL:</em> check entity http://example.org/L2',
        '<em class="pass">PASS:</em> entity http://example.org/L1#video has name, description and type',
        '<em class="warning">WARNING:</em> No sdo.description found. Descriptions are useful. <br />',
        '<em class="fail">FAIL:</em> check entity http://example.org/L2',
        '<em class="info">INFO:</em> used on subject named  Lesson 2, An error',
        '<em class="info">INFO:</em> subject is of type [no label], Resource',
        '<em class="warning">WARNING:</em> not checked: object type not known',
        "<h2>Retrieved graph in Turtle</h2>",
        "@prefix ocx: &lt;https://github.com/K12OCX/k12ocx-specs/&gt; .",
    ]
    # the order of the test results in the report is not fixed
    for line in expected_response_snippets:
        assert line in response.data.decode("UTF8")
