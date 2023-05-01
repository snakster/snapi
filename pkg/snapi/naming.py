from typing import Any, Dict, Union, List, Tuple
from dataclasses import dataclass

import re

@dataclass
class NestedType:
    name: str
    nested: List[Union[str, Any]]


class _TypeTokenScanner:
    def __init__(self, s: str):
        self._tokens = _tokenize_type_decl(s)
        self.cur = next(self._tokens)
        self.next = next(self._tokens)


    def forward(self, n = 1):
        for i in range(n):
            self.cur = self.next
            self.next = next(self._tokens)


def parse_type(s: str) -> Union[str, NestedType]:
    return _parse_type_expr(_TypeTokenScanner(s))


def _parse_type_expr(scanner: _TypeTokenScanner):
    name = scanner.cur

    if scanner.next != "<":
        return name
    scanner.forward(2)    

    nested = [_parse_type_expr(scanner)]

    while True:
        if scanner.next != ",":
            break
        scanner.forward(2)

        nested.append(_parse_type_expr(scanner))
    
    if scanner.next != ">":
        raise Exception("expected '>'")
    scanner.forward()

    return NestedType(name=name, nested=nested)


def _tokenize_type_decl(s: str):
    while True:
        separators = ["<", ">", ","]
        tok = _parse_next_token(s, separators)
        yield tok
        s = s[len(tok):]


def _parse_next_token(s: str, separators: List[str]) -> str:
    s = s.lstrip()
    for tok in separators:
        if s.startswith(tok):
            return tok

    m = re.match(r'[a-zA-Z_]\w*', s)
    if not m:
        return ""
    return m.group()
            

def convert_type(s: str, mapper, delims: Tuple[str,str]) -> str:
    if isinstance(mapper, dict):
        type_map = mapper
        mapper = lambda x : type_map.get(x, x)

    return _convert_type_impl(parse_type(s), mapper, delims)


def _convert_type_impl(t: Union[str, NestedType], mapper, delims) -> str:
    if isinstance(t, str):
        return mapper(t)
    elif isinstance(t, NestedType):
        return mapper(t.name) + delims[0] \
            + ",".join([_convert_type_impl(inner, mapper, delims) for inner in t.nested]) \
            + delims[1]