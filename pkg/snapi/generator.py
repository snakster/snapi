from typing import Any, Dict
from collections.abc import Callable

import os
import yaml

from os.path import join, exists, getmtime

from . import template


class Generator:

    def __init__(self, section_delim = None):
        self._input_decls = {}
        self._transformer_decls = {}
        self._output_decls = {}

        self._template_env = template.make_new_env(section_delim)


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