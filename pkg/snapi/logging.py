"""Logging utilities for use in internal and user-provided functions."""

from abc import ABC, abstractmethod
from enum import Enum

import rich
import json


class ILogger(ABC):
    """Logging interface."""

    @abstractmethod
    def step(self, s: str) -> None:
        """Log a message that indicates progression to the next step of execution."""
        pass

    @abstractmethod
    def info(self, s: str) -> None:
        """Log a normal status message."""
        pass

    @abstractmethod
    def warn(self, s: str) -> None:
        """Log a messages that requires special attention."""
        pass

    @abstractmethod
    def error(self, s: str) -> None:
        """Log a messages that indictates a non-fatal error."""
        pass


class LogFormat(Enum):
    """Log formats supported by the default logger."""
    PRETTY = 1
    JSON = 2


class Logger(ILogger):
    """The default logger."""

    def __init__(
        self,
        mode = LogFormat.PRETTY
    ):
        if mode == LogFormat.JSON:
            self._formatter = JSONFormatter(self)
        else:
            self._formatter = PrettyFormatter(self)

        self._cur_scope = ""


    def step(self, s: str) -> None:
        self._formatter.step(s)


    def info(self, s: str) -> None:
        self._formatter.info(s)
    
    
    def warn(self, s: str) -> None:
        self._formatter.warn(s)
        

    def error(self, s: str) -> None:
        self._formatter.error(s)


class Scope:
    """Logging scope helper for the default logger."""
    
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


class PrettyFormatter():
    def __init__(self, logger):
        self._logger = logger


    def step(self, s: str) -> None:
        rich.print(f"\n{s} ...")


    def info(self, s: str) -> None:
        rich.print(f"{self._fmt_context(s, 'bold')}{s}")
    
    
    def warn(self, s: str) -> None:
        rich.print(f"{self._fmt_context(s, 'bold yellow')}{s}")
        

    def error(self, s: str) -> None:
        rich.print(f"{self._fmt_context(s, 'bold red')}{s}")


    def _fmt_context(self, s: str, style: str) -> str:
        if len(self._logger._cur_scope) == 0:
            return ""
        return f"[{style}]\[{self._logger._cur_scope}][/{style}] "


class JSONFormatter():
    def __init__(self, logger):
        self._logger = logger


    def step(self, s: str) -> None:
        self._print_json(s, "step")


    def info(self, s: str) -> None:
        self._print_json(s, "info")
    
    
    def warn(self, s: str) -> None:
        self._print_json(s, "warning")
        

    def error(self, s: str) -> None:
        self._print_json(s, "error")


    def _print_json(self, message: str, level: str) -> str:
        t = {
            "message": message,
            "level": level
        }
        if len(self._logger._cur_scope) > 0:
            t["scope"] = self._logger._cur_scope
        
        print(json.dumps(t))


