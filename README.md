# snapi 

snapi (/sneɪ.piˈaɪ/) is a simple yet flexible code generation framework. It uses Python, but can generate code for any programming language - or any text in general.

### Why?

Here are some scenarios where an abstract API definition + code generation might be a good idea:
* Function declarations that are repeated multiple times, i.e. for interface, implementation, testing mocks, ...
* Boilerplate wrappers that forward or convert between layers of an architecture
* SDKs for multiple programming languages using the same general API
* Semantic checks on API changes that require an easy to parse definition, i.e. to programmatically test for backward compatibility

### Development status

This project is still work-in-progress. Current list of open tasks:
- [x] Main features
- [ ] Documentation
- [x] Examples
- [ ] Tests
- [ ] CI pipeline
- [ ] PyPI package

### Installation

With [pip](https://pip.pypa.io/en/stable/getting-started/):
```
$ cd pkg
$ pip install .
```

[For usage in a container, see here.](todo)

## A brief example

### 1. Design your API model in YAML/JSON
API specification (YAML):
```YAML
services:
  - name: files
    functions:
      - name: upload
        args:
          - local_path: string
          - remote_path: string

      - name: download
        args:
          - remote_path: string
          - local_path: string

      - name: list_dir
        args:
          - remote_path: string = "/"
        returns: list<string>
```

### 2. Create templates using Jinja markup

Python template:
```Python
{% for fn in functions %}
def {{fn.name}}({{fn.args | format_py_args}}) -> {{fn.return_type}}:
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

Templates can use a transformed input model that contains language-specific data.

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

## Design rationale

#### Why not use gRPC/OpenAPI/Swagger/... instead?

If there is an existing tool or framework that already meets your requirements w.r.t. to supported input schemas and targeted output code, it is probably more effective to use that.
The role of this framework is to help you implement requirements for which no ready-to-use solution exists yet.

#### Why require code instead of providing an approach that is fully declarative, i.e. rules defined in a YAML file to map inputs, templates and outputs.

Especially when targeting different programming languages, such mappings may require more than just a simple set of rules.
For Python, a single _module.yaml_ input might result in a single generated _<module>.py_.
For C++, there might be multiple header and source files with an entirely different layout.
In general, conditionals, loops and other constructs would be required, so expressing this in Python code is the approach we prefer.

That being said, the goal is to make implementing a code generator as easy as possible.
Eventually this could mean including reusable components for common input schemas and template data models for common programming language.
All that would be left for the user is writing YAML specs, templates and mapping logic.
