from urllib.parse import urlparse
from requests import get
from w3lib.html import get_base_url
from extruct.jsonld import JsonLdExtractor
from json import dumps

def is_http_url(url):
    # utility function to check urls
    # from https://stackoverflow.com/questions/7160737
  try:
    result = urlparse(url)
    if result.scheme in ['http', 'https']:
        return all([result.scheme, result.netloc])
    else:
        raise ValueError
  except ValueError:
    return False

class PageData:
    """Fetch a webpage referenced by a url and store any JSON-LD found in
    along with information about where the data came from.

    Methods: (all these are called by __init__() if passed valid URL)
    . set_request_url(url: str): if the input is a valid URL, set the
         request_url property to it, else will raise error.
    . retrieve_page(): retrieve a webpage from the request_url;
         store response text as page, response code as status_code, and the url from which the response came as base_url
    . set_data():
    Properties:
    .  request_url: the URL from which data was requested
    .  status_code: the HTTP status code returned
    .  base_url: the URL from which data was returned (if any)
    .  page: the text of the page returned (if any)
    .  data: JSON extracted from the page as a string (if any, '[]' if none)
    """

    def __init__(self, url: str =''):
        """"If passed a valid url retrieve page from it, extract and store and JSON-LD as self.data along with information about where data came from. If no url, instance has data (used for unit testing)."""
        if url is not '':
            self.set_request_url(url)
            self.retrieve_page()
            self.set_data()
        else:
            pass

    def set_request_url(self, url: str):
        """If passed a valid URL, set the request_url property to it and return True, or else raise a RuntimeError."""
        if is_http_url(url):
            self.request_url = url
        else:
            msg = "Not a valid url. Request url not set."
            raise RuntimeError(msg)
        return True

    def retrieve_page(self):
        """ Retrieve a webpage from the request_url; store response text as page, response code as status_code, and the url from which the response came as base_url. Return True if successful, raise RuntimeError if request_url not set or if page not found."""
        response = get(self.request_url)
        if response.status_code < 300:
            self.status_code = str(response.status_code)
        else:
            msg = "Error retrieving URL. HTTP status code: " + str(response.status_code)
            raise RuntimeError(msg)
        if response.text:
            self.page = response.text
            self.base_url = get_base_url(response.text, response.url)
            return True
        else:
            msg = "No text found at URL " + self.request_url
            raise RuntimeError(msg)

    def set_data(self):
        """ Extract JSON-LD data from self.page and store as a string in self.data. Return True if data is present, False if not. Raise RuntimeError if JSON-LD cannot be extracted (e.g. if it is malformed)."""
        jslde = JsonLdExtractor()
        try:
            self.data = dumps(jslde.extract(self.page, base_url=self.base_url))
            if self.data == '[]':
                return False
            else:
                return True
        except:
            msg = "Error extracting data from page"
            raise RuntimeError(msg)
