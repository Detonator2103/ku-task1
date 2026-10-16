"""Эмулятор командной строки. Этап 1: цикл REPL."""

import sys

from commands import execute_line
from errors import ExitShell, ShellError

VFS_NAME = "vfs"


def get_prompt():
    """Возвращает приглашение к вводу с именем VFS."""
    return f"{VFS_NAME}$ "


def read_command():
    """Читает строку ввода; при вводе из файла дублирует её на экран."""
    line = input(get_prompt())
    if not sys.stdin.isatty():
        print(line)
    return line


def run_line(line):
    """Выполняет одну строку. Возвращает True, если введён exit."""
    try:
        execute_line(line)
    except ExitShell:
        return True
    except ShellError as error:
        print(f"Ошибка: {error}")
    return False


def run_repl():
    """Интерактивный цикл: читает команды, пока не будет введён exit."""
    while True:
        try:
            line = read_command()
        except EOFError:
            print()
            break
        except KeyboardInterrupt:
            print()
            continue
        if run_line(line):
            break


def main():
    """Запускает эмулятор."""
    run_repl()


if __name__ == "__main__":
    main()
