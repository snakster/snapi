"""The main generator class and supporting definitions."""

from typing import Any, Dict, Optional
from collections.abc import Callable

from dataclasses import dataclass

import os
import yaml
import json
import time

from . import logging, template
from .errors import GeneratorError


class Generator:
    """The main generator class."""

    def __init__(
        self,
        section_delim = None,
        save_orphaned_sections = True,
        filters = None
    ):
        self.save_orphaned_sections = save_orphaned_sections

        self._input_decls = {}
        self._transformer_decls = {}
        self._output_decls = {}

        self._template_env = template.make_new_env(section_delim, filters)

        self.log = logging.Logger()


    def add_inputs(
        self,
        name: str,
        impl: Callable[..., None],
        args = {}
    ) -> None:
        """Declare an input group."""

        self._input_decls[name] = {
            "impl": impl,
            "args": args
        }


    def add_transformer(
        self,
        name: str,
        inputs: str,
        impl: Callable[..., None],
        args = {}
    ) -> None:
        """Declare a transformer."""

        if inputs not in self._input_decls:
            raise GeneratorError(f"undefined inputs '{inputs}'")

        self._transformer_decls[name] = {
            "inputs": inputs,
            "impl": impl,
            "args": args
        }


    def add_outputs(
        self,
        name: str,
        data: str,
        impl: Callable[..., None], args = {}
    ) -> None:
        """Declare an output group."""

        if data not in self._transformer_decls:
            raise GeneratorError(f"undefined transformer '{data}'")
        
        self._output_decls[name] = {
            "data": data,
            "impl": impl,
            "args": args
        }


    def run(self) -> None:
        """Run the generator with the previously declared inputs, transformers and outputs."""

        in_cache = {}
        tr_cache = {}

        if len(self._input_decls) == 0:
            raise GeneratorError("no inputs declared")
        
        if len(self._transformer_decls) == 0:
            raise GeneratorError("no transformers declared")
        
        if len(self._output_decls) == 0:
            raise GeneratorError("no outputs declared")

        def process_in_decl(decl):
            
            impl = decl["impl"]
            args = decl["args"]

            inputs = Inputs(self.log)
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

            outputs = Outputs(
                log=self.log,
                env=self._template_env,
                with_save_orphans=self.save_orphaned_sections
            )
            impl(outputs, data, **args)
            return outputs._stats

        self.log.step(f"Outputs")

        for name, decl in self._output_decls.items():
            with logging.Scope(self.log, name):
                stats = process_out_decl(decl)
                self.log.info(f"[green]{stats.written_file_count}[/green] written")


class Inputs:
    """Context passed to input delegate functions."""

    @dataclass
    class Stats:
        read_file_count: int = 0


    def __init__(self, log: logging.Logger):
        self.log = log
        self._data = {}
        self._stats = self.Stats()


    def from_file(self, path: str) -> None:
        """TODO"""
        self._data[path] = self._read_input_file(path)
        self._stats.read_file_count += 1


    def _read_input_file(self, path: str) -> Any:
        if path.endswith(".json"):
            with open(path, 'r') as f:
                return json.load(f)
        elif path.endswith((".yaml", ".yml")):
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        else:
            return None


class Outputs:
    """Context passed to output delegate functions."""
    
    @dataclass
    class Stats:
        written_file_count: int = 0


    def __init__(self, log: logging.Logger, with_save_orphans: bool, env):
        self.log = log
        self._with_save_orphans = with_save_orphans
        self._env = env
        self._stats = self.Stats()


    def to_file(self, path: str, template: str, data: Any) -> None:
        """TODO"""

        self._write_output_file(
            template_path=template,
            output_path=path,
            data=data
        )
        self._stats.written_file_count += 1


    def _write_output_file(self, template_path: str, output_path: str, data: Any) -> None:
        self._env.section_output_path = output_path
        self._env.section_data = None

        tpl = self._env.get_template(template_path)
        s = tpl.render(data)

        if self._with_save_orphans:
            self._save_orphaned_sections(output_path)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w') as f:
            f.write(s)


    def _save_orphaned_sections(self, output_path: str) -> None:
        if self._env.section_data is None:
            return
        
        orphan_count = 0

        for name, data in self._env.section_data.items():
            if not data.referenced:
                orphan_count += 1

        if orphan_count == 0:
            return
        
        cur_time = int(time.time()) 
        fn = f"{output_path}.{cur_time}.orphaned"

        with open(fn, 'w') as f:
            for name, data in self._env.section_data.items():
                if not data.referenced:
                    f.write(f"BEGIN SECTION {name}\n")
                    f.write(data.content)
                    f.write(f"END SECTION {name}\n\n")

        self.log.warn(f"Saved orphaned sections from '{output_path}' to '{fn}'")