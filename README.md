Checks JSON-LD found in web pages for conformance with K12-OCX.

Checks include
- showing what entities from the OCX domain model are present
- checking that those entities have key properties such as name and description
- checking that the subject and object of every predicate is in its domain/range.

Runs as a flask web service.

Run this in a python 3.7 virtual environment:
```
$ git clone https://github.com/philbarker/OCXChecker.git
$ cd OCXChecker
$ pip install -r requirements.txt
$ python main.py
```
Open http://127.0.0.1:8080/?urlYouWantToCheck in a browser.

If you want to test or develop you also need
```
$ pip install -r dev-reqs.txt
$ python setup.py develop
$ pytest
```
