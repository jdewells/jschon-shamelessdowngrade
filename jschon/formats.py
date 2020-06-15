import email_validator
import rfc3986.exceptions
import rfc3986.validators

from jschon.exceptions import JSONPointerError
from jschon.json import JSONString, JSONPointer
from jschon.schema import Format, FormatResult

__all__ = [
    'DateTimeFormat',
    'DateFormat',
    'TimeFormat',
    'DurationFormat',
    'EmailFormat',
    'IDNEmailFormat',
    'HostnameFormat',
    'IDNHostnameFormat',
    'IPv4Format',
    'IPv6Format',
    'URIFormat',
    'URIReferenceFormat',
    'IRIFormat',
    'IRIReferenceFormat',
    'UUIDFormat',
    'URITemplateFormat',
    'JSONPointerFormat',
    'RelativeJSONPointerFormat',
    'RegexFormat',
]


class DateTimeFormat(Format):
    __attr__ = "date-time"

    def evaluate(self, instance: JSONString) -> FormatResult:
        raise NotImplementedError


class DateFormat(Format):
    __attr__ = "date"

    def evaluate(self, instance: JSONString) -> FormatResult:
        raise NotImplementedError


class TimeFormat(Format):
    __attr__ = "time"

    def evaluate(self, instance: JSONString) -> FormatResult:
        raise NotImplementedError


class DurationFormat(Format):
    __attr__ = "duration"

    def evaluate(self, instance: JSONString) -> FormatResult:
        raise NotImplementedError


class EmailFormat(Format):
    __attr__ = "email"

    def evaluate(self, instance: JSONString) -> FormatResult:
        try:
            email_validator.validate_email(instance.value, allow_smtputf8=False, check_deliverability=False)
        except email_validator.EmailNotValidError as e:
            return FormatResult(valid=False, error=str(e))

        return FormatResult(valid=True)


class IDNEmailFormat(Format):
    __attr__ = "idn-email"

    def evaluate(self, instance: JSONString) -> FormatResult:
        try:
            email_validator.validate_email(instance.value, check_deliverability=False)
        except email_validator.EmailNotValidError as e:
            return FormatResult(valid=False, error=str(e))

        return FormatResult(valid=True)


class HostnameFormat(Format):
    __attr__ = "hostname"

    def evaluate(self, instance: JSONString) -> FormatResult:
        raise NotImplementedError


class IDNHostnameFormat(Format):
    __attr__ = "idn-hostname"

    def evaluate(self, instance: JSONString) -> FormatResult:
        raise NotImplementedError


class IPv4Format(Format):
    __attr__ = "ipv4"

    def evaluate(self, instance: JSONString) -> FormatResult:
        raise NotImplementedError


class IPv6Format(Format):
    __attr__ = "ipv6"

    def evaluate(self, instance: JSONString) -> FormatResult:
        raise NotImplementedError


class URIFormat(Format):
    __attr__ = "uri"

    def evaluate(self, instance: JSONString) -> FormatResult:
        validator = rfc3986.validators.Validator().require_presence_of('scheme')
        try:
            validator.validate(rfc3986.uri_reference(instance.value))
        except rfc3986.exceptions.ValidationError as e:
            return FormatResult(valid=False, error=str(e))

        return FormatResult(valid=True)


class URIReferenceFormat(Format):
    __attr__ = "uri-reference"

    def evaluate(self, instance: JSONString) -> FormatResult:
        validator = rfc3986.validators.Validator()
        try:
            validator.validate(rfc3986.uri_reference(instance.value))
        except rfc3986.exceptions.ValidationError as e:
            return FormatResult(valid=False, error=str(e))

        return FormatResult(valid=True)


class IRIFormat(Format):
    __attr__ = "iri"

    def evaluate(self, instance: JSONString) -> FormatResult:
        raise NotImplementedError


class IRIReferenceFormat(Format):
    __attr__ = "iri-reference"

    def evaluate(self, instance: JSONString) -> FormatResult:
        raise NotImplementedError


class UUIDFormat(Format):
    __attr__ = "uuid"

    def evaluate(self, instance: JSONString) -> FormatResult:
        raise NotImplementedError


class URITemplateFormat(Format):
    __attr__ = "uri-template"

    def evaluate(self, instance: JSONString) -> FormatResult:
        raise NotImplementedError


class JSONPointerFormat(Format):
    __attr__ = "json-pointer"

    def evaluate(self, instance: JSONString) -> FormatResult:
        try:
            JSONPointer(instance.value)
        except JSONPointerError as e:
            return FormatResult(valid=False, error=str(e))

        return FormatResult(valid=True)


class RelativeJSONPointerFormat(Format):
    __attr__ = "relative-json-pointer"

    def evaluate(self, instance: JSONString) -> FormatResult:
        raise NotImplementedError


class RegexFormat(Format):
    __attr__ = "regex"

    def evaluate(self, instance: JSONString) -> FormatResult:
        raise NotImplementedError