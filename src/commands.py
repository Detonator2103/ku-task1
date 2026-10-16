"""Команды эмулятора (этап 1: заглушки) и выполнение строки ввода."""

from errors import ExitShell, ShellError
from parsing import parse_line

MAX_CD_ARGS = 1


def print_stub(name, args):
    """Печатает имя команды-заглушки и её аргументы."""
    print(f"Команда: {name}")
    print(f"Аргументы: {args}")


def cmd_ls(args):
    """Заглушка команды ls."""
    print_stub("ls", args)


def cmd_cd(args):
    """Заглушка команды cd: принимает не больше одного аргумента."""
    if len(args) > MAX_CD_ARGS:
        raise ShellError("cd: слишком много аргументов")
    print_stub("cd", args)


def cmd_exit(args):
    """Завершает работу эмулятора."""
    if args:
        raise ShellError("exit: команда не принимает аргументов")
    raise ExitShell()


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "exit": cmd_exit,
}


def execute_line(line):
    """Разбирает строку и выполняет команду.

    Бросает ShellError при ошибке и ExitShell для команды exit.
    """
    try:
        tokens = parse_line(line)
    except ValueError as error:
        raise ShellError("неверный синтаксис (не закрыта кавычка)") from error
    if not tokens:
        return
    name, args = tokens[0], tokens[1:]
    handler = COMMANDS.get(name)
    if handler is None:
        raise ShellError(f"неизвестная команда '{name}'")
    handler(args)
