import yaml
import os
from argparse import ArgumentParser

from typing import Any, Dict
from collections.abc import Callable

from jinja2 import Environment, FunctionLoader, select_autoescape, TemplateNotFound, nodes
from jinja2.ext import Extension

from os.path import join, exists, getmtime


class Generator:

    def __init__(self, section_delim = None):
        self._input_decls = {}
        self._transformer_decls = {}
        self._output_decls = {}

        self._template_env = Environment(
            loader=FunctionLoader(load_template),
            extensions=[SectionExtension],
            autoescape=select_autoescape(),
            trim_blocks=True,
            lstrip_blocks=True
        )

        if section_delim == None:
            section_delim = default_section_delim
        self._template_env.section_delim_selector=section_delim


    def add_inputs(self, name: str, impl: Callable[..., None], args = {}):
        self._input_decls[name] = {
            "impl": impl,
            "args": args
        }


    def add_transformer(self, name: str, inputs: str, impl: Callable[..., None], args = {}):
        self._transformer_decls[name] = {
            "inputs": inputs,
            "impl": impl,
            "args": args
        }


    def add_outputs(self, name: str, data: str, impl: Callable[..., None], args = {}):
        self._output_decls[name] = {
            "data": data,
            "impl": impl,
            "args": args
        }


    def run(self):
        in_cache = {}
        tr_cache = {}

        def process_in_decl(decl):
            impl = decl["impl"]
            args = decl["args"]

            inputs = Inputs()
            impl(inputs, **args)
            return inputs._data

        for name, decl in self._input_decls.items():
            if not name in in_cache:
                in_cache[name] = process_in_decl(decl)

        def process_tr_decl(decl):
            impl = decl["impl"]
            args = decl["args"]
            data = in_cache[decl["inputs"]]
            return impl(data, **args)

        for name, decl in self._transformer_decls.items():
            if not name in tr_cache:
                tr_cache[name] = process_tr_decl(decl)

        def process_out_decl(decl):
            impl = decl["impl"]
            args = decl["args"]
            data = tr_cache[decl["data"]]

            outputs = Outputs(self._template_env)
            impl(outputs, data, **args)

        for name, decl in self._output_decls.items():
            process_out_decl(decl)


class Inputs:
    def __init__(self):
        self._data = {}

    def from_file(self, path: str):
        self._data[path] = read_input_file(path)


def read_input_file(path: str) -> Any:
    if path.endswith(".json"):
        with open(path, 'r') as f:
            return json.load(f)
    elif path.endswith((".yaml", ".yml")):
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    else:
        return None


class Outputs:
    def __init__(self, env):
        self._env = env

    def to_file(self, path: str, template: str, data: Any):
        write_output_file(self._env,
            template_path=template,
            output_path=path,
            data=data
        )


def write_output_file(env, template_path: str, output_path: str, data: Any):
    env.section_output_path = output_path
    env.section_data = None

    tpl = env.get_template(template_path)
    s = tpl.render(data)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w') as f:
        f.write(s)



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
