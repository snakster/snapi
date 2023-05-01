from typing import Any, Dict, List
import dataclasses

import os
import snapi

import models.cpp


def main():
    g = snapi.Generator(
        filters={
            "cpp_args_as_str": models.cpp.args_as_str,
            "cpp_args_as_str_with_defaults": models.cpp.args_as_str_with_defaults,
        }
    )

    g.add_inputs(
        name="api_spec",
        impl=read_specs,
        args={
            "spec_dir": "spec"
        }
    )

    g.add_transformer(
        name="cpp_data",
        inputs="api_spec",
        impl=models.cpp.from_input
    )

    g.add_outputs(
        name="cpp",
        data="cpp_data",
        impl=write_cpp_outputs,
        args={
            "out_dir": "out/cpp",
            "tpl_dir": "templates/cpp",
        }
    )

    g.run()


def read_specs(inputs: snapi.Inputs, spec_dir: str):
    for root, dirs, files in os.walk(spec_dir):
        for p in files:
            if p.endswith(".yml"):
                inputs.from_file(os.path.join(root, p))



def write_cpp_outputs(outputs: snapi.Outputs, data: List[models.cpp.Module], out_dir: str, tpl_dir: str):
    for module_data in data:
        path_prefix = os.path.join(out_dir, module_data.name)

        outputs.to_file(
            path_prefix + ".h",
            template=f"{tpl_dir}/module.h.jinja",
            data={
                "module": module_data
            }
        )

        for service_data in module_data.services:
            service_path_prefix = os.path.join(path_prefix, service_data.impl_name)

            outputs.to_file(
                service_path_prefix + ".h",
                template=f"{tpl_dir}/service_impl.h.jinja",
                data={
                    "service": service_data,
                    "module": module_data
                }
            )
            outputs.to_file(
                service_path_prefix + ".cpp",
                template=f"{tpl_dir}/service_impl.cpp.jinja",
                data={
                    "service": service_data,
                    "module": module_data
                }
            )


if __name__ == "__main__":
    main()