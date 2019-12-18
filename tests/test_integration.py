import pprint
from requests import get

pp = pprint.PrettyPrinter(indent=4)  # used for debugging


def test_integration(test_client):
    url = "https://pjjk.net/ldchecker/demo.html"
    response = test_client.get("/check?url=" + url)
    # uncomment this block to write new expected results if you
    # change any checks or the file tested
    # with open('tests/output/response.html', 'w') as o_file:
    #    o_file.write(response.data.decode('UTF8'))
    #    o_file.close
    expected_response = open("tests/output/response.html", "r")
    # the order of the test results in the report is not fixed
    for line in expected_response.readlines():
        print(line)
        assert line in response.data.decode("UTF8")
    assert false
