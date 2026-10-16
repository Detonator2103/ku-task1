"""Эмулятор командной строки. Этап 2: параметры и стартовый скрипт."""

import argparse
import os
import sys

from commands import execute_line
from errors import ExitShell, ShellError

DEFAULT_VFS_NAME = "vfs"
NOT_SET = "(не задан)"
EXIT_ERROR = 1
STATUS_OK = "ok"
STATUS_ERROR = "error"
STATUS_EXIT = "exit"


def parse_arguments():
    """Разбирает параметры командной строки."""
    parser = argparse.ArgumentParser(description="Эмулятор командной строки")
    parser.add_argument("--vfs", help="путь к физическому расположению VFS")
    parser.add_argument("--script", help="путь к стартовому скрипту")
    return parser.parse_args()


def print_debug(options):
    """Выводит все заданные параметры запуска (отладочный вывод)."""
    print(f"[DEBUG] vfs    = {options.vfs or NOT_SET}")
    print(f"[DEBUG] script = {options.script or NOT_SET}")


def get_vfs_name(vfs_path):
    """Возвращает имя VFS: имя файла без расширения или имя по умолчанию."""
    if not vfs_path:
        return DEFAULT_VFS_NAME
    file_name = os.path.basename(vfs_path)
    return os.path.splitext(file_name)[0]


def get_prompt(vfs_name):
    """Возвращает приглашение к вводу с именем VFS."""
    return f"{vfs_name}$ "


def run_line(line):
    """Выполняет одну строку. Возвращает STATUS_OK, STATUS_ERROR или EXIT."""
    try:
        execute_line(line)
    except ExitShell:
        return STATUS_EXIT
    except ShellError as error:
        print(f"Ошибка: {error}")
        return STATUS_ERROR
    return STATUS_OK


def read_script(path):
    """Читает строки скрипта; при ошибке чтения возвращает None."""
    try:
        with open(path, encoding="utf-8") as file:
            return file.read().splitlines()
    except (OSError, UnicodeDecodeError):
        return None


def run_script(path, vfs_name):
    """Выполняет стартовый скрипт, показывая и ввод, и вывод.

    Останавливается на первой ошибке. Возвращает статус выполнения.
    """
    lines = read_script(path)
    if lines is None:
        print(f"Ошибка: не удалось открыть скрипт: {path}")
        return STATUS_ERROR
    for number, line in enumerate(lines, start=1):
        text = line.strip()
        if not text or text.startswith("#"):
            continue
        print(f"{get_prompt(vfs_name)}{text}")
        status = run_line(text)
        if status == STATUS_ERROR:
            print(f"Ошибка в скрипте {path} (строка {number})")
        if status != STATUS_OK:
            return status
    return STATUS_OK


def read_command(vfs_name):
    """Читает строку ввода; при вводе из файла дублирует её на экран."""
    line = input(get_prompt(vfs_name))
    if not sys.stdin.isatty():
        print(line)
    return line


def run_repl(vfs_name):
    """Интерактивный цикл: читает команды, пока не будет введён exit."""
    while True:
        try:
            line = read_command(vfs_name)
        except EOFError:
            print()
            break
        except KeyboardInterrupt:
            print()
            continue
        if run_line(line) == STATUS_EXIT:
            break


def main():
    """Запускает эмулятор."""
    options = parse_arguments()
    print_debug(options)
    vfs_name = get_vfs_name(options.vfs)
    if options.script:
        status = run_script(options.script, vfs_name)
        if status == STATUS_ERROR:
            sys.exit(EXIT_ERROR)
        if status == STATUS_EXIT:
            return
    run_repl(vfs_name)


if __name__ == "__main__":
    main()
