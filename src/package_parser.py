"""Модуль для получения и парсинга package.json из GitHub."""
import json
import urllib.request
import urllib.error
from typing import List, Dict, Any, Optional

from .url_parser import build_raw_url

HTTP_TIMEOUT = 10
FALLBACK_BRANCHES = ("main", "master")


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


def fetch_with_fallback(
    owner: str, repo: str, branch: str
) -> Dict[str, Any]:
    """
    Загрузка package.json с перебором веток-кандидатов.

    Args:
        owner: Владелец репозитория.
        repo: Имя репозитория.
        branch: Ветка из конфигурации.

    Returns:
        Словарь с содержимым package.json.

    Raises:
        PackageParseError: Если ни одна ветка не подошла.
    """
    candidates = _build_branch_candidates(branch)
    last_error: Optional[PackageParseError] = None

    for candidate in candidates:
        try:
            return fetch_package_json(owner, repo, candidate)
        except PackageParseError as error:
            last_error = error

    raise last_error


def _build_branch_candidates(branch: str) -> List[str]:
    """
    Построение списка веток-кандидатов для перебора.

    Args:
        branch: Ветка из конфигурации.

    Returns:
        Список веток в порядке приоритета.
    """
    candidates = [branch]
    for fallback in FALLBACK_BRANCHES:
        if fallback not in candidates:
            candidates.append(fallback)
    return candidates


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