# snapi 

snapi (/sneɪ.piˈaɪ/) is a simple yet flexible code generation framework. It uses Python, but can generate code for any language - or any text in general.

### Why?

TODO

### Installation

With [pip](https://pip.pypa.io/en/stable/getting-started/):
```
pip install snapi
```

[For usage in a container, see here.](todo)

## Quick example

### 1. Design your API model in YAML/JSON
API specification (YAML):
```YAML
services:
  - name: database
    functions:
      - name: put
        args:
          - key: string
          - value: string

      - name: get
        args:
          - key: string
        returns: string
```

### 2. Create templates using Jinja markup

Python template:
```Python
{% for fn in functions %}
def {{fn.name}}({{fn.arg_decls}}) -> {{fn.return_type}}:
  {% section fn.name + "_impl" %}
  # TODO: Implement.
  # Note: User code within a section is generally preserved between generator runs.
  {% endsection %}
{% endfor %}
```

Go template:
```Go
// TODO
```

Templates might use a transformed input model that contains language-specific data.

### 3. Implement generator with snapi

Create generator and declare inputs:
```Python
import snapi

g = snapi.Generator()

g.add_inputs(
  name="api_spec",
  impl=snapi.input_from_single_file,
  args={"path": "spec/api.yaml"}
)
```

Transform to input model for use in language-specific templates:
```Python

g.add_transformer(
  name="py_data",
  inputs="api_spec",
  impl=my_python_transformer
)

g.add_transformer(
  name="go_data",
  inputs="api_spec",
  impl=my_go_transformer
)
```

Declare outputs and run generator:
```Python
g.add_outputs(
  name="py",
  data="py_data",
  impl=write_py_outputs,
  args={"out_dir": "out/py", "tpl_dir": "templates/py"}
)

g.add_outputs(
  name="go",
  data="go_data",
  impl=write_go_outputs,
  args={"out_dir": "out/go", "tpl_dir": "templates/go"}
)

g.run()
```

An example output implementation:
```Python
def write_py_outputs(outputs: snapi.Outputs, services: List[models.py.Service], out_dir: str, tpl_dir: str):
  for service in services:
    outputs.to_file(
      os.path.join(out_dir, service.name + ".py"),
      template=f"{tpl_dir}/service.py.jinja",
      data={"service": service}
    )
```
