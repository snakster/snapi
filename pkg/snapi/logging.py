"""Logging utilities for use in internal and user-provided functions."""

from rich import print


class Logger:
    """TODO"""

    def __init__(self):
        self._cur_scope = ""


    def step(self, s: str) -> None:
        """Log a message that indicates progression to the next step of execution."""

        print(f"\n{s} ...")


    def info(self, s: str) -> None:
        """Log a normal status message."""

        print(f"  [bold]\[{self._cur_scope}][/bold] {s}")
    
    
    def warn(self, s: str) -> None:
        """Log a messages that requires special attention."""

        print(f"  [bold yellow]\[{self._cur_scope}][/bold yellow] {s}")
        

    def error(self, s: str) -> None:
        """Log a messages that indictates a non-fatal error."""

        print(f"  [bold red]\[{self._cur_scope}][/bold red] {s}")


class Scope:
    """TODO"""
    
    def __init__(
        self,
        logger: Logger,
        scope: str
    ):
        self.logger = logger
        self._scope = scope
        self._prev_scope = ""
    

    def __enter__(self):
        self._prev_scope = self.logger._cur_scope
        self.logger._cur_scope = self._scope
        return self


    def __exit__(self, *args):
        self.logger._cur_scope = self._prev_scope