"""Виртуальная файловая система, загружаемая из XML-файла."""

import base64
import binascii
import hashlib
import re
import time
import xml.etree.ElementTree as et

DEFAULT_NAME = "vfs"
DEFAULT_DIR_MODE = 0o755
DEFAULT_FILE_MODE = 0o644
OCTAL_BASE = 8
MODE_PATTERN = re.compile(r"[0-7]{3}")


class VFSError(Exception):
    """Ошибка загрузки виртуальной файловой системы."""


class Node:
    """Узел дерева VFS: файл или папка."""

    def __init__(self, name, is_dir, mode, data=b""):
        """Создаёт узел с именем, правами и содержимым."""
        self.name = name
        self.is_dir = is_dir
        self.mode = mode
        self.data = data
        self.children = {}

    def add_child(self, node):
        """Добавляет вложенный узел в папку."""
        self.children[node.name] = node


class VFS:
    """Виртуальная файловая система, которая целиком хранится в памяти."""

    def __init__(self, name, root, digest):
        """Хранит имя VFS, корневую папку и хеш исходных данных."""
        self.name = name
        self.root = root
        self.digest = digest

    def get_prompt(self):
        """Возвращает приглашение к вводу с именем VFS."""
        return f"{self.name}$ "


def parse_octal_mode(text):
    """Переводит запись прав (например, 755) в число. Иначе возвращает None."""
    if MODE_PATTERN.fullmatch(text):
        return int(text, OCTAL_BASE)
    return None


def read_name(element):
    """Возвращает имя узла из атрибута name."""
    name = element.get("name")
    if not name or "/" in name:
        raise VFSError(f"неверное имя в теге <{element.tag}>")
    return name


def read_mode(element, default):
    """Читает права из атрибута mode (например, 755)."""
    text = element.get("mode")
    if text is None:
        return default
    mode = parse_octal_mode(text)
    if mode is None:
        raise VFSError(f"неверные права '{text}'")
    return mode


def read_file_data(element):
    """Читает содержимое файла: обычный текст или base64."""
    text = element.text or ""
    encoding = element.get("encoding", "text")
    if encoding == "text":
        return text.encode("utf-8")
    if encoding == "base64":
        try:
            return base64.b64decode("".join(text.split()), validate=True)
        except binascii.Error as error:
            raise VFSError("неверные данные base64") from error
    raise VFSError(f"неизвестная кодировка '{encoding}'")


def add_children(node, element):
    """Добавляет в папку все вложенные файлы и папки."""
    for child_element in element:
        child = build_node(child_element)
        if child.name in node.children:
            raise VFSError(f"повторяется имя '{child.name}'")
        node.add_child(child)


def build_node(element):
    """Строит узел дерева по XML-элементу <dir> или <file>."""
    name = read_name(element)
    if element.tag == "file":
        mode = read_mode(element, DEFAULT_FILE_MODE)
        return Node(name, False, mode, read_file_data(element))
    if element.tag == "dir":
        node = Node(name, True, read_mode(element, DEFAULT_DIR_MODE))
        add_children(node, element)
        return node
    raise VFSError(f"неизвестный тег <{element.tag}>")


def read_file_bytes(path):
    """Читает файл целиком; ошибки чтения превращает в VFSError."""
    try:
        with open(path, "rb") as file:
            return file.read()
    except FileNotFoundError as error:
        raise VFSError(f"файл не найден: {path}") from error
    except OSError as error:
        raise VFSError(f"не удалось прочитать файл: {path}") from error


def load_vfs(path):
    """Загружает VFS из XML-файла. При ошибке бросает VFSError."""
    raw = read_file_bytes(path)
    try:
        root_element = et.fromstring(raw)
    except et.ParseError as error:
        raise VFSError("неверный формат XML") from error
    if root_element.tag != "vfs":
        raise VFSError("корневой тег должен быть <vfs>")
    name = read_name(root_element)
    root = Node("", True, read_mode(root_element, DEFAULT_DIR_MODE))
    add_children(root, root_element)
    return VFS(name, root, hashlib.sha256(raw).hexdigest())


def create_empty_vfs():
    """Создаёт пустую VFS (когда параметр --vfs не задан)."""
    root = Node("", True, DEFAULT_DIR_MODE)
    return VFS(DEFAULT_NAME, root, hashlib.sha256(b"").hexdigest())
