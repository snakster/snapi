from typing import Any, Dict, Optional
from collections.abc import Callable

from dataclasses import dataclass

import os
import yaml
import json

from rich import print

from . import logging, template
from .errors import GeneratorError


class Generator:

    def __init__(self, section_delim = None, filters = None):
        self._input_decls = {}
        self._transformer_decls = {}
        self._output_decls = {}

        self._template_env = template.make_new_env(section_delim, filters)

        self.log = logging.Logger()


    def add_inputs(self, name: str, impl: Callable[..., None], args = {}):
        self._input_decls[name] = {
            "impl": impl,
            "args": args
        }


    def add_transformer(self, name: str, inputs: str, impl: Callable[..., None], args = {}):
        if inputs not in self._input_decls:
            raise GeneratorError(f"undefined inputs '{inputs}'")

        self._transformer_decls[name] = {
            "inputs": inputs,
            "impl": impl,
            "args": args
        }


    def add_outputs(self, name: str, data: str, impl: Callable[..., None], args = {}):
        if data not in self._transformer_decls:
            raise GeneratorError(f"undefined transformer '{data}'")
        
        self._output_decls[name] = {
            "data": data,
            "impl": impl,
            "args": args
        }


    def run(self):
        in_cache = {}
        tr_cache = {}

        if len(self._input_decls) == 0:
            raise GeneratorError("no inputs defined")
        
        if len(self._transformer_decls) == 0:
            raise GeneratorError("no transformers defined")
        
        if len(self._output_decls) == 0:
            raise GeneratorError("no outputs defined")

        def process_in_decl(decl):
            
            impl = decl["impl"]
            args = decl["args"]

            inputs = Inputs()
            impl(inputs, **args)
            return inputs._data, inputs._stats
        
        self.log.step(f"Inputs")

        for name, decl in self._input_decls.items():
            if not name in in_cache:
                with logging.Scope(self.log, name):
                    in_cache[name], stats = process_in_decl(decl)
                    self.log.info(f"[green]{stats.read_file_count}[/green] read")

        def process_tr_decl(decl):
            impl = decl["impl"]
            args = decl["args"]
            
            data = in_cache[decl["inputs"]]
            return impl(data, **args)

        self.log.step(f"Transformers")

        for name, decl in self._transformer_decls.items():
            if not name in tr_cache:
                with logging.Scope(self.log, name):
                    tr_cache[name] = process_tr_decl(decl)
                    self.log.info(f"done")

        def process_out_decl(decl):
            impl = decl["impl"]
            args = decl["args"]
            data = tr_cache[decl["data"]]

            outputs = Outputs(self._template_env)
            impl(outputs, data, **args)
            return outputs._stats

        self.log.step(f"Outputs")

        for name, decl in self._output_decls.items():
            with logging.Scope(self.log, name):
                stats = process_out_decl(decl)
                self.log.info(f"[green]{stats.written_file_count}[/green] written")


class Inputs:
    @dataclass
    class Stats:
        read_file_count: int = 0

    def __init__(self):
        self._data = {}
        self._stats = self.Stats()

    def from_file(self, path: str):
        self._data[path] = read_input_file(path)
        self._stats.read_file_count += 1


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
    
    @dataclass
    class Stats:
        written_file_count: int = 0


    def __init__(self, env):
        self._env = env
        self._stats = self.Stats()

    def to_file(self, path: str, template: str, data: Any):
        write_output_file(self._env,
            template_path=template,
            output_path=path,
            data=data
        )
        self._stats.written_file_count += 1


def write_output_file(env, template_path: str, output_path: str, data: Any):
    env.section_output_path = output_path
    env.section_data = None

    tpl = env.get_template(template_path)
    s = tpl.render(data)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w') as f:
        f.write(s)