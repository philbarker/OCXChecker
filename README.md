Tests JSON-LD found in web pages for conformance with K12-OCX.

Tests include
- showing what entities from the OCX domain model are present
- checking that those entities have key properties such as name and description
- checking that the subject and object of every predicate is in its domain/range.

Runs a flask web service

Run this in a python 3.7 virtual environment
```
$ git clone https://github.com/philbarker/OCXChecker.git
$ pip install -r requirements.txt
$ python main.py
```
open http://127.0.0.1:8080/?url=<url of page to check>&showTurtle=True in a browser.
