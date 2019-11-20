import pytest, pprint
from checker import PageData


def test_init():
    pd = PageData()
    assert type(pd) == PageData


def test_set_request_url():
    url = "HtTp://example.org/test.html"
    pd = PageData()
    with pytest.raises(RuntimeError):  # first test with no url set
        pd.set_request_url("")
    with pytest.raises(RuntimeError):  # then test with invalid url set
        pd.set_request_url("not a url")
    pd.set_request_url(url)  # test correct url is set
    assert pd.request_url == url


def test_retrieve_page():
    fake_url = "http://example.org/test.html"
    real_url = "https://www.bbc.co.uk/"
    redir_url = "https://google.com/"
    found_url = "https://www.google.com/"
    pd = PageData()
    pd.set_request_url(fake_url)  # this url won't be found
    with pytest.raises(RuntimeError):
        pd.retrieve_page()
    pd.set_request_url(real_url)  # this url will be returned
    pd.retrieve_page()
    assert pd.status_code == "200"
    assert pd.base_url == real_url
    pd.set_request_url(redir_url)  # this url will be found elsewhere
    pd.retrieve_page()
    assert pd.status_code == "200"
    assert pd.base_url == found_url


def test_set_data():
    pp = pprint.PrettyPrinter()
    pd = PageData()
    pd.base_url = "http://example.org/"
    pd.request_url = "http://example.org/"
    found_data = False
    with open("tests/input/no_json.html") as file:
        pd.page = file.read()
    pd.base_url = "http://example.org/"
    found_data = pd.set_data()
    assert not found_data
    assert pd.data == "[]"
    with open("tests/input/bad_json.html") as file:
        pd.page = file.read()
    with pytest.raises(RuntimeError):
        found_data = pd.set_data()
    assert not found_data
    with open("tests/input/good_json.html") as file:
        pd.page = file.read()
    found_data = pd.set_data()
    data_expected = (
        '[{"@context": "http://schema.org/", "@type": "Thing", "name": "Something"}]'
    )
    assert found_data
    assert pd.data == data_expected
    with open("tests/input/more_json.html") as file:
        pd.page = file.read()
    found_data = pd.set_data()
    data_expected = '[{"@context": "http://schema.org/", "@type": "Thing", "name": "Something"}, {"@context": "http://schema.org/", "@type": "Thing", "name": "Another thing"}]'
    pp.pprint(pd.data)
    assert found_data
    assert pd.data == data_expected
