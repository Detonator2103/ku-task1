"""Команды эмулятора и выполнение строки ввода."""

import re
import time

from errors import ExitShell, ShellError
from parsing import parse_line
from vfs import DEFAULT_FILE_MODE, Node, parse_octal_mode

START_TIME = time.time()
TIME_FORMAT = "%Y-%m-%d %H:%M"
SECONDS_IN_HOUR = 3600
SECONDS_IN_MINUTE = 60
PERMISSION_BITS = 9
LETTERS_IN_GROUP = 3
PERMISSION_LETTERS = "rwx"
MAX_LS_PATHS = 1
MAX_CD_ARGS = 1
CHMOD_ARGS_COUNT = 2
SYMBOLIC_PATTERN = re.compile(r"([ugoa]*)([+-])([rwx]+)")
WHO_SHIFTS = {"u": 6, "g": 3, "o": 0}
PERMISSION_VALUES = {"r": 4, "w": 2, "x": 1}
OS_NAME = "VFS-OS"
OS_RELEASE = "1.0"
OS_MACHINE = "python"
UNAME_OPTIONS = {
    "-s": OS_NAME,
    "-r": OS_RELEASE,
    "-m": OS_MACHINE,
}


def cmd_exit(vfs, args):
    """Завершает работу эмулятора."""
    if args:
        raise ShellError("exit: команда не принимает аргументов")
    raise ExitShell()


def cmd_vfs_info(vfs, args):
    """Выводит имя VFS и хеш SHA-256 её данных."""
    if args:
        raise ShellError("vfs-info: команда не принимает аргументов")
    print(f"Имя: {vfs.name}")
    print(f"SHA-256: {vfs.digest}")


def mode_to_string(mode, is_dir):
    """Переводит права (например, 0o755) в строку вида drwxr-xr-x."""
    result = "d" if is_dir else "-"
    for index in range(PERMISSION_BITS):
        bit = PERMISSION_BITS - 1 - index
        if mode & (1 << bit):
            result += PERMISSION_LETTERS[index % LETTERS_IN_GROUP]
        else:
            result += "-"
    return result


def parse_ls_args(args):
    """Разбирает аргументы ls. Возвращает (длинный_формат, путь)."""
    long_format = False
    paths = []
    for arg in args:
        if arg == "-l":
            long_format = True
        elif arg.startswith("-"):
            raise ShellError(f"ls: неизвестная опция '{arg}'")
        else:
            paths.append(arg)
    if len(paths) > MAX_LS_PATHS:
        raise ShellError("ls: слишком много аргументов")
    path = paths[0] if paths else "."
    return long_format, path


def format_entry(node, long_format):
    """Возвращает строку для вывода одной записи команды ls."""
    if not long_format:
        return node.name
    perms = mode_to_string(node.mode, node.is_dir)
    changed = time.strftime(TIME_FORMAT, time.localtime(node.mtime))
    return f"{perms} {node.size():>6} {changed} {node.name}"


def cmd_ls(vfs, args):
    """Показывает содержимое папки: ls [-l] [путь]."""
    long_format, path = parse_ls_args(args)
    node = vfs.find(path)
    if node is None:
        raise ShellError(f"ls: нет такого пути: {path}")
    if node.is_dir:
        nodes = [node.children[name] for name in sorted(node.children)]
    else:
        nodes = [node]
    lines = [format_entry(item, long_format) for item in nodes]
    separator = "\n" if long_format else "  "
    if lines:
        print(separator.join(lines))


def cmd_cd(vfs, args):
    """Меняет текущую папку: cd [путь]. Без аргумента переходит в корень."""
    if len(args) > MAX_CD_ARGS:
        raise ShellError("cd: слишком много аргументов")
    path = args[0] if args else "/"
    parts = vfs.resolve(path)
    node = vfs.find_parts(parts)
    if node is None:
        raise ShellError(f"cd: нет такого пути: {path}")
    if not node.is_dir:
        raise ShellError(f"cd: это не папка: {path}")
    vfs.cwd = parts


def cmd_uname(vfs, args):
    """Выводит сведения об ОС: -s, -r, -m или -a (всё сразу)."""
    options = args or ["-s"]
    if "-a" in options:
        options = ["-s", "-r", "-m"]
    parts = []
    for option in options:
        if option not in UNAME_OPTIONS:
            raise ShellError(f"uname: неизвестная опция '{option}'")
        parts.append(UNAME_OPTIONS[option])
    print(" ".join(parts))


def split_time(seconds):
    """Разбивает секунды на часы, минуты и секунды."""
    hours, rest = divmod(int(seconds), SECONDS_IN_HOUR)
    minutes, secs = divmod(rest, SECONDS_IN_MINUTE)
    return hours, minutes, secs


def cmd_uptime(vfs, args):
    """Показывает время работы эмулятора: uptime [-p]."""
    hours, minutes, secs = split_time(time.time() - START_TIME)
    if not args:
        print(f"up {hours}:{minutes:02d}:{secs:02d}")
    elif args == ["-p"]:
        print(f"up {hours} hours, {minutes} minutes")
    else:
        raise ShellError("uptime: неверные аргументы")


def parse_mode(text, old_mode):
    """Вычисляет новые права по записи вида 755 или u+x."""
    octal_mode = parse_octal_mode(text)
    if octal_mode is not None:
        return octal_mode
    match = SYMBOLIC_PATTERN.fullmatch(text)
    if match is None:
        raise ShellError(f"chmod: неверный режим: '{text}'")
    who, sign, letters = match.groups()
    if not who or "a" in who:
        who = "ugo"
    mask = 0
    for user in who:
        for letter in letters:
            mask |= PERMISSION_VALUES[letter] << WHO_SHIFTS[user]
    if sign == "+":
        return old_mode | mask
    return old_mode & ~mask


def cmd_chmod(vfs, args):
    """Меняет права файла или папки: chmod РЕЖИМ ПУТЬ."""
    if len(args) != CHMOD_ARGS_COUNT:
        raise ShellError(
            "chmod: неверные аргументы (использование: chmod РЕЖИМ ПУТЬ)"
        )
    mode_text, path = args
    node = vfs.find(path)
    if node is None:
        raise ShellError(f"chmod: нет такого пути: {path}")
    node.mode = parse_mode(mode_text, node.mode)


def touch_path(vfs, path, create_missing):
    """Обновляет время изменения или создаёт пустой файл."""
    parts = vfs.resolve(path)
    node = vfs.find_parts(parts)
    if node is not None:
        node.mtime = time.time()
        return
    if not create_missing:
        return
    parent = vfs.find_parts(parts[:-1])
    if parent is None:
        raise ShellError(f"touch: нет такого пути: {path}")
    if not parent.is_dir:
        raise ShellError(f"touch: это не папка: {path}")
    parent.add_child(Node(parts[-1], False, DEFAULT_FILE_MODE))


def cmd_touch(vfs, args):
    """Создаёт пустые файлы или обновляет время: touch [-c] ПУТЬ..."""
    for arg in args:
        if arg.startswith("-") and arg != "-c":
            raise ShellError(f"touch: неизвестная опция '{arg}'")
    paths = [arg for arg in args if arg != "-c"]
    if not paths:
        raise ShellError("touch: не указан файл")
    for path in paths:
        touch_path(vfs, path, "-c" not in args)


COMMANDS = {
    "exit": cmd_exit,
    "vfs-info": cmd_vfs_info,
    "ls": cmd_ls,
    "cd": cmd_cd,
    "uname": cmd_uname,
    "uptime": cmd_uptime,
    "chmod": cmd_chmod,
    "touch": cmd_touch,
}


def execute_line(line, vfs):
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
    handler(vfs, args)
