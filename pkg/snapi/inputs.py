"""The main generator class and supporting definitions."""

from typing import Any, Union, Tuple

from dataclasses import dataclass

import os
import json

import yaml

from . import logging


class Inputs:
    """Context passed to input delegate functions."""

    @dataclass
    class Stats:
        read_file_count: int = 0


    def __init__(self, log: logging.ILogger):
        self.log = log
        self._data = {}
        self._stats = self.Stats()


    def from_file(self, path: str) -> None:
        """Read input data from file."""

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


def from_single_file(inputs: Inputs, file_path: str) -> None:
    """Use a single file as input."""

    inputs.from_file(file_path)


def from_file_list(inputs: Inputs, list_path: str) -> None:
    """Read a list of newline-separated paths from a file and use them as inputs."""

    with open(list_path, "r") as f:
        while True:
            p = f.readline()
            if not p:
                break
            inputs.from_file(p.strip())


def from_directory(
    inputs: Inputs,
    dir_path: str,
    recursive: bool = True,
    suffix: Union[str,Tuple[str, ...]] = (".yml", ".json")
) -> None:
    """Iterate all files in directory and use them as inputs."""

    for root, dirs, files in os.walk(dir_path):
        for p in files:
            if p.endswith(suffix):
                inputs.from_file(os.path.join(root, p))
        
        if not recursive:
            break
