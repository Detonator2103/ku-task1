"""Разбор введённой строки на токены."""

import os
import shlex


def expand_variables(token):
    """Раскрывает переменные окружения вида $VAR и ${VAR}."""
    return os.path.expandvars(token)


def parse_line(line):
    """Делит строку на токены и раскрывает переменные окружения.

    Бросает ValueError, если в строке не закрыта кавычка.
    """
    tokens = shlex.split(line)
    return [expand_variables(token) for token in tokens]
