from requests import get
from w3lib.html import get_base_url
from extruct.jsonld import JsonLdExtractor
from json import dumps


class PageData():
    """Data returned from a web page.
    Has properties:
       request_url: the URL from which data was requested
       status_code: the HTTP status code returned
       base_url: the URL from which data was returned (if any)
       page: the text of the page returned (if any)
       data: JSON extracted from the page (if any)
    Check the status code before trying to read any retrieved data.
    """
    def __init__(self, url, *args, **kwargs):
        self.set_request_url(url)
        self.retrieve_page()
        self.set_data()

    def set_request_url(self, url):
        if url:
            self.request_url = url
        else:
            msg = "Request url not set.\n"
            msg = (
                msg
                + "Try e.g. "
                + request.host_url
                + "?url=https://philbarker.github.io/OCXPhysVibWav/l1/\n"
            )
            msg = msg + "see " + request.host_url + "/info for more info."
            raise RuntimeError(msg)

    def retrieve_page(self):
        response = get(self.request_url)
        if response.status_code < 300:
            self.status_code = str(response.status_code)
        else:
            msg = "error retrieving URL. HTTP status code: " + str(response.status_code)
            raise RuntimeError(msg)
        if response.text:
            self.page = response.text
            self.base_url = get_base_url(response.text, response.url)
        else:
            msg = "No text found at URL " + self.request_url
            raise RuntimeError(msg)

    def set_data(self):
        jslde = JsonLdExtractor()
        try:
            self.data = dumps(jslde.extract(self.page, base_url=self.base_url))
        except:
            msg = "Error extracting data page at " + self.request_url
            raise RuntimeError(msg)
