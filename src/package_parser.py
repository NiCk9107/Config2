"""Модуль для получения и парсинга package.json из GitHub."""
import json
import urllib.request
import urllib.error
from typing import List, Dict, Any

# ИСПРАВЛЕНО: относительный импорт
from .url_parser import build_raw_url

HTTP_TIMEOUT = 10


class PackageParseError(Exception):
    """Исключение для ошибок парсинга package.json."""
    pass


def fetch_package_json(
    owner: str, repo: str, branch: str
) -> Dict[str, Any]:
    """
    Загрузка package.json из GitHub-репозитория.

    Args:
        owner: Владелец репозитория.
        repo: Имя репозитория.
        branch: Ветка репозитория.

    Returns:
        Словарь с содержимым package.json.

    Raises:
        PackageParseError: Если файл не найден или невалиден.
    """
    url = build_raw_url(owner, repo, branch)

    try:
        with urllib.request.urlopen(url, timeout=HTTP_TIMEOUT) as response:
            content = response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        if error.code == 404:
            msg = f"package.json не найден в {owner}/{repo}@{branch}"
            raise PackageParseError(msg)
        raise PackageParseError(f"HTTP ошибка {error.code}: {error.reason}")
    except urllib.error.URLError as error:
        raise PackageParseError(f"Ошибка сети: {error.reason}")

    try:
        return json.loads(content)
    except json.JSONDecodeError as error:
        raise PackageParseError(f"Невалидный JSON: {error}")


def extract_dependencies(package_data: Dict[str, Any]) -> List[str]:
    """
    Извлечение списка прямых зависимостей из package.json.

    Args:
        package_data: Содержимое package.json.

    Returns:
        Отсортированный список имён зависимостей.

    Raises:
        PackageParseError: Если поле dependencies отсутствует.
    """
    if not isinstance(package_data, dict):
        raise PackageParseError("package.json должен быть объектом")

    dependencies = package_data.get("dependencies")
    if dependencies is None:
        raise PackageParseError("Поле dependencies отсутствует")

    if not isinstance(dependencies, dict):
        raise PackageParseError("dependencies должен быть объектом")

    return sorted(dependencies.keys())