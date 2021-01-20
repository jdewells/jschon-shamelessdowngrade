import datetime
import re

import dateutil.parser
import email_validator
import rfc3986.exceptions
import rfc3986.validators
from hypothesis import given, strategies as hs, provisional as hp

from jschon.evaluation import EvaluationNode
from jschon.exceptions import JSONPointerError
from jschon.json import JSONString
from jschon.jsonpointer import JSONPointer
from jschon.jsonschema import JSONSchema
from jschon.keywords import FormatKeyword
from tests import metaschema_uri
from tests.strategies import jsonpointer


def evaluate(format_attr, instval):
    return EvaluationNode(
        evaluator=FormatKeyword(format_attr, superschema=JSONSchema(True, metaschema_uri=metaschema_uri)),
        json=JSONString(instval),
    )


@given(hs.datetimes())
def test_datetime_valid(instval):
    result = evaluate("date-time", datetime.datetime.isoformat(instval))
    assert result.valid is True


@given(hs.text())
def test_datetime_invalid(instval):
    result = evaluate("date-time", instval)
    try:
        dateutil.parser.isoparse(instval)
        assert result.valid is True
    except ValueError:
        assert result.valid is False


@given(hs.dates())
def test_date_valid(instval):
    result = evaluate("date", datetime.date.isoformat(instval))
    assert result.valid is True


@given(hs.text())
def test_date_invalid(instval):
    result = evaluate("date", instval)
    try:
        dateutil.parser.isoparser().parse_isodate(instval)
        assert result.valid is True
    except ValueError:
        assert result.valid is False


@given(hs.times())
def test_time_valid(instval):
    result = evaluate("time", datetime.time.isoformat(instval))
    assert result.valid is True


@given(hs.text())
def test_time_invalid(instval):
    result = evaluate("time", instval)
    try:
        dateutil.parser.isoparser().parse_isotime(instval)
        assert result.valid is True
    except ValueError:
        assert result.valid is False


@given(hs.emails() | hs.text())
def test_email(instval):
    result = evaluate("email", instval)
    try:
        email_validator.validate_email(instval, allow_smtputf8=False, check_deliverability=False)
        assert result.valid is True
    except email_validator.EmailNotValidError:
        assert result.valid is False


@given(hs.emails() | hs.text())
def test_idnemail(instval):
    result = evaluate("idn-email", instval)
    try:
        email_validator.validate_email(instval, allow_smtputf8=True, check_deliverability=False)
        assert result.valid is True
    except email_validator.EmailNotValidError:
        assert result.valid is False


@given(hp.urls())
def test_uri_valid(instval):
    result = evaluate("uri", instval)
    assert result.valid is True


@given(hs.text())
def test_uri_invalid(instval):
    result = evaluate("uri", instval)
    validator = rfc3986.validators.Validator().require_presence_of('scheme')
    try:
        validator.validate(rfc3986.uri_reference(instval))
        assert result.valid is True
    except rfc3986.exceptions.ValidationError:
        assert result.valid is False


@given(hp.urls() | jsonpointer)
def test_urireference_valid(instval):
    result = evaluate("uri-reference", instval)
    assert result.valid is True


@given(hs.text())
def test_urireference_invalid(instval):
    result = evaluate("uri-reference", instval)
    validator = rfc3986.validators.Validator()
    try:
        validator.validate(rfc3986.uri_reference(instval))
        assert result.valid is True
    except rfc3986.exceptions.ValidationError:
        assert result.valid is False


@given(jsonpointer)
def test_jsonpointer_valid(instval):
    result = evaluate("json-pointer", instval)
    assert result.valid is True


@given(hs.text())
def test_jsonpointer_invalid(instval):
    result = evaluate("json-pointer", instval)
    try:
        JSONPointer(instval)
        assert result.valid is True
    except JSONPointerError:
        assert result.valid is False


@given(hs.text(hs.from_regex(r'[0-9\[\]\-^+*?{},$()|]')))
def test_regex(instval):
    result = evaluate("regex", instval)
    try:
        re.compile(instval)
        assert result.valid is True
    except re.error:
        assert result.valid is False
