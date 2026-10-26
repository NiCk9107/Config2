"""Загрузчик тестового репозитория из файла описания графа."""
import json
import os

from typing import Callable, Dict, List



class TestRepoError(Exception):
    """Исключение для ошибок тестового репозитория."""
    pass


def load_test_repo(path: str) -> Dict[str, List[str]]:
    """
    Загрузка описания графа из файла тестового репозитория.

    Args:
        path: Путь к файлу описания графа (JSON).

    Returns:
        Словарь: имя пакета -> список зависимостей.

    Raises:
        TestRepoError: Если файл не найден или невалиден.
    """
    if not os.path.isfile(path):
        raise TestRepoError(f"Файл репозитория не найден: {path}")

    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as error:
        raise TestRepoError(f"Невалидный JSON: {error}")

    _validate_repo_data(data)
    return data


def make_fetcher(repo: Dict[str, List[str]]) -> "Callable[[str], List[str]]":
    """
    Создание функции получения зависимостей из тестового репозитория.

    Args:
        repo: Словарь имя пакета -> список зависимостей.

    Returns:
        Функция, возвращающая зависимости пакета.
    """
    def fetcher(package: str) -> List[str]:
        if package not in repo:
            return []
        return list(repo[package])
    return fetcher


def _validate_repo_data(data: Dict[str, List[str]]) -> None:
    """
    Проверка структуры описания графа.

    Args:
        data: Словарь имя пакета -> список зависимостей.

    Raises:
        TestRepoError: Если структура невалидна.
    """
    if not isinstance(data, dict):
        raise TestRepoError("Описание графа должно быть объектом")
    for name, deps in data.items():
        _validate_package_name(name)
        _validate_deps_list(name, deps)


def _validate_deps_list(name: str, deps: List[str]) -> None:
    """
    Проверка списка зависимостей пакета.

    Args:
        name: Имя пакета-владельца.
        deps: Список зависимостей.

    Raises:
        TestRepoError: Если список невалиден.
    """
    if not isinstance(deps, list):
        raise TestRepoError(f"Зависимости {name} должны быть списком")
    for dep in deps:
        _validate_package_name(dep)


def _validate_package_name(name: str) -> None:
    """
    Проверка имени пакета: только большие латинские буквы.

    Args:
        name: Имя пакета.

    Raises:
        TestRepoError: Если имя невалидно.
    """
    if not isinstance(name, str) or not _is_upper_latin(name):
        raise TestRepoError(
            f"Имя пакета должно быть большими латинскими: {name}"
        )


def _is_upper_latin(name: str) -> bool:
    """
    Проверка, что строка состоит из больших латинских букв.

    Args:
        name: Проверяемая строка.

    Returns:
        True, если все символы — буквы от A до Z.
    """
    return bool(name) and all("A" <= ch <= "Z" for ch in name)