import os

from typing import Any, Dict

from jinja2 import Environment, FunctionLoader, select_autoescape, TemplateNotFound, nodes
from jinja2.ext import Extension

from os.path import join, exists, getmtime


class SectionExtension(Extension):
    tags = {"section"}

    def __init__(self, environment):
        super().__init__(environment)

        environment.extend(
            section_data=None,
            section_output_path="",
            section_delim_selector=None
        )

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        section_name = parser.parse_expression()
        body = parser.parse_statements(["name:endsection"], drop_needle=True)

        return nodes.CallBlock(
            self.call_method("_section_lookup", [section_name]), [], [], body
        ).set_lineno(lineno)

    def _section_lookup(self, name, caller):
        output_path = self.environment.section_output_path 
        delim = self.environment.section_delim_selector(output_path)

        if self.environment.section_data == None:
            self.environment.section_data = load_section_data(output_path, delim)
        
        rv = self.environment.section_data.get(name)
        if rv == None:
            rv = caller()

        indent = get_indent(rv)
        marker = delim + name

        return indent + marker + '\n' + rv + indent + marker


def make_new_env(delim, filters):
    env = Environment(
        loader=FunctionLoader(load_template),
        extensions=[SectionExtension],
        autoescape=select_autoescape(),
        trim_blocks=True,
        lstrip_blocks=True
    )

    if delim == None:
        delim = default_section_delim
    env.section_delim_selector=delim

    if filters is not None:
        env.filters.update(filters)

    return env


def default_section_delim(fn: str) -> str:
    if fn.endswith(".py"):
        return "#$section:"
    else:
        return "//$section:"


def load_template(path):
    if not exists(path):
        raise TemplateNotFound(path)

    mtime = getmtime(path)
    with open(path) as f:
        source = f.read()

    return source, path, lambda: mtime == getmtime(path)


def load_section_data(path: str, delim: str) -> Dict[str,str]:
    data = {}

    try:
        with open(path, 'r') as f:
            while True:
                s = f.readline()
                if s == "":
                    break
                
                delim_idx = s.find(delim)
                if delim_idx == -1:
                    continue

                section_name = s[delim_idx+len(delim):].strip()

                buf = ""

                while True:
                    s = f.readline()
                    if s == "":
                        break

                    delim_idx = s.find(delim)
                    if delim_idx == -1:
                        buf += s
                        continue

                    if section_name != s[delim_idx+len(delim):].strip():
                        break

                    data[section_name] = buf
    except IOError:
        pass
    
    return data


def get_indent(s: str):
    for i in range(0, len(s)):
        if not s[i].isspace():
            return s[0:i]
    return ""
