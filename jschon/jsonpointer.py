from __future__ import annotations

import collections
import re
import typing as _t
import urllib.parse

from jschon.exceptions import JSONPointerError

__all__ = [
    'JSONPointer',
]


class JSONPointer(_t.Sequence[str]):
    """ JSON Pointer :rfc:`6901`

    A JSON pointer is a string representing a reference to some value within a
    JSON document. It consists of a series of 'reference tokens' prefixed by '/',
    each token in turn being the (escaped) JSON object key or the JSON array
    index at the next node down the path to the referenced value. The empty
    string '' represents a reference to an entire JSON document.

    A ``JSONPointer`` instance is an immutable sequence of the unescaped JSON
    object keys and/or array indices - henceforth referred to simply as 'keys' -
    that comprise the path to a referenced value.

    A ``JSONPointer`` instance is constructed by the concatenation of any number
    of arguments, each of which can be one of:

    - a string conforming to the :rfc:`6901` syntax
    - an iterable of unescaped keys
    - an existing ``JSONPointer`` instance

    Two ``JSONPointer`` instances compare equal if their key sequences are
    identical.

    The ``/`` operator provides a convenient syntax for extending a JSON pointer.
    It produces a new ``JSONPointer`` instance by copying the left-hand argument
    (a ``JSONPointer`` instance) and appending the right-hand argument (an
    unescaped key).

    Taking an index into a ``JSONPointer`` returns the unescaped key at that
    position. Taking a slice into a ``JSONPointer`` returns a new ``JSONPointer``
    composed of the specified slice of the original's keys.
    """

    _json_pointer_re = re.compile(r'^(/([^~/]|(~[01]))*)*$')
    _array_index_re = re.compile(r'^0|([1-9][0-9]*)$')

    def __init__(self, *values: _t.Union[str, _t.Iterable[str], JSONPointer]) -> None:
        """ Constructor.

        :raise JSONPointerError: if a string argument does not conform to the RFC 6901 syntax
        """
        self._keys: _t.List[str] = []

        for value in values:
            if isinstance(value, str):
                if not self._json_pointer_re.fullmatch(value):
                    raise JSONPointerError(f"'{value}' is not a valid JSON pointer")
                self._keys.extend(self.unescape(token) for token in value.split('/')[1:])

            elif isinstance(value, JSONPointer):
                self._keys.extend(value._keys)

            elif isinstance(value, _t.Iterable) and all(isinstance(k, str) for k in value):
                self._keys.extend(value)

            else:
                raise TypeError("Expecting str, Iterable[str], or JSONPointer")

    @_t.overload
    def __getitem__(self, index: int) -> str:
        ...

    @_t.overload
    def __getitem__(self, index: slice) -> JSONPointer:
        ...

    def __getitem__(self, index: _t.Union[int, slice]) -> _t.Union[str, JSONPointer]:
        """ Return self[index] """
        if isinstance(index, int):
            return self._keys[index]
        if isinstance(index, slice):
            return JSONPointer(self._keys[index])
        raise TypeError("Expecting int or slice")

    def __len__(self) -> int:
        """ Return len(self) """
        return len(self._keys)

    def __truediv__(self, key: str) -> JSONPointer:
        """ Return self / key """
        if isinstance(key, str):
            return JSONPointer(self, (key,))
        return NotImplemented

    def __eq__(self, other: JSONPointer) -> bool:
        """ Return self == other """
        if isinstance(other, JSONPointer):
            return self._keys == other._keys
        return NotImplemented

    def __str__(self) -> str:
        """ Return str(self) """
        return ''.join([f'/{self.escape(key)}' for key in self._keys])

    def __repr__(self) -> str:
        """ Return repr(self) """
        return f"JSONPointer('{self}')"

    def evaluate(self, document: _t.Union[_t.Mapping, _t.Sequence]) -> _t.Any:
        """ Return the value at the location in the document indicated by self.

        :raise JSONPointerError: if the location does not exist
        """
        def resolve(value, keys):
            if not keys:
                return value
            key = keys.popleft()
            try:
                if isinstance(value, _t.Mapping):
                    return resolve(value[key], keys)
                if isinstance(value, _t.Sequence) and not isinstance(value, str) and \
                        self._array_index_re.fullmatch(key):
                    return resolve(value[int(key)], keys)
            except (KeyError, IndexError):
                pass
            raise JSONPointerError(f"Failed to resolve '{self}' against the given document")

        return resolve(document, collections.deque(self._keys))

    def apply(self, document: _t.Union[_t.Mapping, _t.Sequence], value: _t.Any) -> None:
        """ Set the value at the location in the document indicated by self.

        :raise JSONPointerError: if the location cannot be reached
        """
        raise NotImplementedError

    @classmethod
    def parse_uri_fragment(cls, value: str) -> JSONPointer:
        if not value.startswith('#'):
            raise JSONPointerError(f"'{value}' is not a valid URI fragment")
        return JSONPointer(urllib.parse.unquote(value[1:]))

    def uri_fragment(self) -> str:
        return f'#{urllib.parse.quote(str(self))}'

    @staticmethod
    def escape(key: str) -> str:
        return key.replace('~', '~0').replace('/', '~1')

    @staticmethod
    def unescape(token: str) -> str:
        return token.replace('~1', '/').replace('~0', '~')