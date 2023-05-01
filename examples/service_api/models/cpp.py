from typing import Any, Dict, List

from dataclasses import dataclass, field
import os

import snapi.naming

@dataclass
class Function:
    name: str
    return_type: str

@dataclass
class Service:
    name: str
    impl_name: str
    functions: List[Function]

@dataclass
class Module:
    name: str
    services: List[Service]


def from_input(input_data: Dict[str,Any]) -> List[Module]:
    modules: List[Module] = []
    
    for path, module_spec in input_data.items():
        name = os.path.basename(path).split(".")[0]
        modules.append(parse_module(name, module_spec))

    return modules


def parse_module(name: str, module_spec) -> Module:
    return Module(
        name = name,
        services = [parse_service(s) for s in module_spec["services"]]
    )


def parse_service(service_spec) -> Service:
    name = service_spec["name"]
    return Service(
        name = name,
        impl_name = name + "_impl",
        functions = [parse_function(s) for s in service_spec["functions"]]
    )


def parse_function(function_spec) -> Function:
    return Function(
        name = function_spec["name"],
        return_type = convert_type(function_spec.get("returns", "void"))
    )


TYPE_MAP = {
    "string": "std::string",
    "list": "std::vector"
}

def map_type(s: str) -> str:
    if s in TYPE_MAP:
        return TYPE_MAP[s]
    return s

def convert_type(s: str) -> str:
    return snapi.naming.convert_type(s, mapper=map_type, delims=("<", ">"))

