from typing import Any, Dict, List

import os
import snapi

def main():
    g = snapi.Generator()

    g.add_inputs(
        name="my_spec",
        impl=read_specs,
        args={
            "spec_dir": "spec"
        }
    )

    g.add_transformer(
        name="my_data",
        inputs="my_spec",
        impl=make_data
    )

    g.add_outputs(
        name="my_cpp_code",
        data="my_data",
        impl=write_cpp_outputs,
        args={
            "out_dir": "out/cpp",
            "tpl_dir": "templates/cpp",
        }
    )

    g.add_outputs(
        name="my_py_code",
        data="my_data",
        impl=write_py_outputs,
        args={
            "out_dir": "out/py",
            "tpl_dir": "templates/py",
        }
    )

    g.run()


def read_specs(inputs: snapi.Inputs, spec_dir: str):
    for root, dirs, files in os.walk(spec_dir):
        for p in files:
            if p.endswith(".yml"):
                inputs.from_file(f"{root}/{p}")


def make_data(input_data: Dict[str,Any]) -> Any:
    data = []
    
    for path, spec_data in input_data.items():
        data.append({
            "name": os.path.basename(path).split(".")[0],
            "content": spec_data["content"]
        })

    return data


def write_cpp_outputs(outputs: snapi.Outputs, data: Any, out_dir: str, tpl_dir: str):
    for item in data:
        path_prefix = os.path.join(out_dir, item["name"])

        outputs.to_file(
            path_prefix + ".h",
            template=f"{tpl_dir}/code.h",
            data=item
        )
        outputs.to_file(
            path_prefix + ".cpp",
            template=f"{tpl_dir}/code.cpp",
            data=item
        )


def write_py_outputs(outputs: snapi.Outputs, data: Any, out_dir: str, tpl_dir: str):
    for item in data:
        outputs.to_file(
            f"{out_dir}/{item['name']}.py",
            template=f"{tpl_dir}/code.py",
            data=item
        )


if __name__ == "__main__":
    main()