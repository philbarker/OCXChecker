import pprint
from requests import get

pp = pprint.PrettyPrinter(indent=4)  # used for debugging

def test_integration(test_client):
    url = "http://127.0.0.1:8080/static/demo.html"
    response = test_client.get("?url="+url)
    pp.pprint(response.data)
    assert False
