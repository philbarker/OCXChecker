from checker import Report, CheckResult, create_app
import pytest, pprint

pp = pprint.PrettyPrinter(indent=4)  # used for debugging


@pytest.fixture(scope="module")
def test_client():
    config = {"TESTING": True}
    app = create_app(config)
    testing_client = app.test_client()
    ctx = app.app_context()
    ctx.push()
    yield testing_client
    ctx.pop()


@pytest.fixture(scope="module")
def report():
    r = Report(True)
    return r


@pytest.fixture(scope="module")
def result():
    r = CheckResult(
        n="dummy results",
        d="dummy results for primary entities, properties of names entities and subject and object of all predicates",
        p=False,
    )
    r.add_info("some dummy information")
    r.add_warning("a dummy warning")
    r1 = CheckResult(
        n="primary entities present",
        d="check that there is at least one primary entity",
        p=False,
    )
    r1.add_info("set up to fail")
    r2 = CheckResult(
        n="check of all indentified entities",
        d="entities with URI have name, description and type",
        p=True,
    )
    r2.add_info("a winner from the start")
    r3 = CheckResult(
        n="predicate checks",
        d="subjects are in predicates' domains, and objects are in predicates' ranges for all statements",
        p=True,
    )
    r3.add_warning("none of this is real")
    r.add_result([r1, r2, r3])
    return r


def test_init(test_client, report):
    assert report.verbose
    assert "<html>\n" in report.html
    assert "<head>\n" in report.html
    assert "</head>\n" in report.html
    assert "<body>\n" in report.html


def test_add_header(test_client, report):
    report.add_header(
        request_url="http://example.org/",
        base_url="http://example.org/index.html",
        status_code="200",
    )
    expected_input_summary = """
    <li><strong>Requested URL:</strong> http://example.org/ </li>
    <li><strong>Returned URL:</strong> http://example.org/index.html </li>
    <li><strong>Status code:</strong>  200 </li>"""
    assert "<body>\n" in report.html
    assert expected_input_summary in report.html


def test_sections(test_client, report, result):
    # this will only test the very basics of getting the right
    # template and generating sections.  Testing a full report
    # is in functional / integration testing.
    report.sections(result)
    expected_entity_section = """<section id="primary_entities">\n  <h2>Report on primary entities present</h2>\n  <p>\n  <em class="fail">FAIL</em> primary entities present\n    set up to fail"""
    expected_entity_check_section = """<section id="enitity-check">\n  <h2>Report on check of all indentified entities</h2> \n  <p>Check that entities with URI have name, description and type.</p>\n  \n</section>"""
    expected_predicate_checks_section = """<section id="predicate-checks">\n  <h2>Report on predicate checks</h2> \n  <p>Check that subjects are in predicates&#39; domains, and objects are in predicates&#39; ranges for all statements.</p>\n  \n</section>"""
    assert expected_entity_section in report.html
    assert expected_entity_check_section in report.html
    assert expected_predicate_checks_section in report.html


def test_end_report(test_client, report):
    report.end_report()
    pp.pprint(report.html)
    assert report.html[-14:] == "</main></body>"
