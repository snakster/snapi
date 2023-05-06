from typing import Any, Dict, List, Optional

from dataclasses import dataclass, field
import os

import snapi.naming

@dataclass
class FunctionArg:
    name: str
    type: str
    default: Optional[str]

@dataclass
class Function:
    name: str
    return_type: str
    args: List[FunctionArg]

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
        return_type = convert_type(function_spec.get("returns", "void")),
        args = [parse_function_arg(s) for s in function_spec.get("args", [])]
    )

def parse_function_arg(arg_spec: Dict[str,str]) -> FunctionArg:
    name, type_and_default = next(iter(arg_spec.items()))

    parts = type_and_default.split("=", 1)
    type_spec = parts[0].strip()

    if len(parts) == 2:
        default = parts[1].strip()
    else:
        default = None

    return FunctionArg(
        name = name,
        type = convert_type(type_spec),
        default = default
    )


TYPE_MAP = {
    "string": "std::string",
    "list": "std::vector"
}

def convert_type(s: str) -> str:
    return snapi.naming.convert_type(s, mapper=TYPE_MAP, delims=("<", ">"))


def fmt_args(args: List[FunctionArg]) -> str:
    return ", ".join([f"{a.type} {a.name}" for a in args])


def fmt_args_defaults(args: List[FunctionArg]) -> str:
    r = []
    for a in args:
        if a.default is not None:
            r.append(f"{a.type} {a.name} = {a.default}")
        else:
            r.append(f"{a.type} {a.name}")
    return ", ".join(r)

