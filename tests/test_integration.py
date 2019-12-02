import pprint
from requests import get

pp = pprint.PrettyPrinter(indent=4)  # used for debugging


def test_integration(test_client):
    url = "https://pjjk.net/ldchecker/demo.html"
    response = test_client.get("/check?url=" + url)
    pp.pprint(response.data)
    assert False
