"""Модуль для парсинга URL GitHub-репозиториев."""
import re
from urllib.parse import urlparse
from typing import Tuple

GITHUB_HOST = "github.com"
DEFAULT_BRANCH = "main"

# ИСПРАВЛЕНО: добавлен $ в конце и ленивый квантификатор [^/]+?
URL_PATTERN = re.compile(
    r"^https?://github\.com/"
    r"(?P<owner>[^/]+)/"
    r"(?P<repo>[^/]+?)"
    r"(?:\.git)?"
    r"(?:/tree/(?P<branch>[^/]+))?"
    r"$"
)


class UrlParseError(Exception):
    """Исключение для ошибок парсинга URL."""
    pass


def parse_github_url(url: str) -> Tuple[str, str, str]:
    """
    Извлечение owner, repo и branch из URL GitHub.

    Args:
        url: URL репозитория GitHub.

    Returns:
        Кортеж (owner, repo, branch).

    Raises:
        UrlParseError: Если URL невалидный или не от GitHub.
    """
    if not isinstance(url, str) or not url.strip():
        raise UrlParseError("URL не может быть пустым")

    parsed = urlparse(url)
    if parsed.hostname != GITHUB_HOST:
        raise UrlParseError(
            f"Ожидается {GITHUB_HOST}, получено: {parsed.hostname}"
        )

    match = URL_PATTERN.match(url)
    if not match:
        raise UrlParseError(f"Не удалось распарсить URL: {url}")

    owner = match.group("owner")
    repo = match.group("repo")
    branch = match.group("branch") or DEFAULT_BRANCH

    return owner, repo, branch


def build_raw_url(owner: str, repo: str, branch: str) -> str:
    """
    Построение URL для получения package.json.

    Args:
        owner: Владелец репозитория.
        repo: Имя репозитория.
        branch: Ветка репозитория.

    Returns:
        URL для загрузки package.json.
    """
    return (
        f"https://raw.githubusercontent.com/"
        f"{owner}/{repo}/{branch}/package.json"
    )