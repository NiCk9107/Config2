"""Получение зависимостей пакетов из npm registry."""
import json
import urllib.request
import urllib.error
from typing import Callable, Dict, List

REGISTRY_URL = "https://registry.npmjs.org/{name}/latest"
HTTP_TIMEOUT = 10


class RegistryError(Exception):
    """Исключение для ошибок npm registry."""
    pass


def fetch_registry_dependencies(name: str) -> List[str]:
    """
    Получение прямых зависимостей пакета из npm registry.

    Args:
        name: Имя npm-пакета.

    Returns:
        Отсортированный список имён прямых зависимостей.

    Raises:
        RegistryError: Если пакет не найден или ответ невалиден.
    """
    url = REGISTRY_URL.format(name=name)
    try:
        with urllib.request.urlopen(url, timeout=HTTP_TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        raise RegistryError(f"HTTP {error.code} для пакета {name}")
    except urllib.error.URLError as error:
        raise RegistryError(f"Ошибка сети: {error.reason}")
    except json.JSONDecodeError as error:
        raise RegistryError(f"Невалидный JSON: {error}")

    deps = data.get("dependencies", {})
    if not isinstance(deps, dict):
        raise RegistryError(f"dependencies пакета {name} невалидны")
    return sorted(deps.keys())


def make_remote_fetcher(
    root_deps: Dict[str, List[str]]
) -> Callable[[str], List[str]]:
    """
    Создание fetcher для remote-режима.

    Args:
        root_deps: Зависимости корневого пакета из GitHub.

    Returns:
        Функция получения зависимостей любого пакета.
    """
    def fetcher(package: str) -> List[str]:
        if package in root_deps:
            return root_deps[package]
        try:
            return fetch_registry_dependencies(package)
        except RegistryError:
            print(f"  [warn] пакет не раскрыт: {package}")
            return []
    return fetcher