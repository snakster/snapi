from rich import print


class Logger:

    def __init__(self):
        self._cur_scope = ""


    def step(self, s: str):
        print(f"\n{s} ...")


    def info(self, s: str):
        print(f"  [bold]\[{self._cur_scope}][/bold] {s}")
    
    
    def warning(self, s: str):
        print(f"  [bold yellow]\[{self._cur_scope}][/bold yellow]) {s}")
        

    def error(self, s: str):
        print(f"  [bold red]\[{self._cur_scope}][/bold red]) {s}")


class Scope:
    def __init__(self, logger, scope: str):
        self.logger = logger
        self._scope = scope
        self._prev_scope = ""
    

    def __enter__(self):
        self._prev_scope = self.logger._cur_scope
        self.logger._cur_scope = self._scope
        return self


    def __exit__(self, *args):
        self.logger._cur_scope = self._prev_scope