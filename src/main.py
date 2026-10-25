"""Главный модуль CLI-приложения визуализации графа зависимостей."""
import sys
import argparse
from typing import List

# ИСПРАВЛЕНО: относительные импорты
from .config_loader import ConfigLoader, ConfigError
from .url_parser import parse_github_url, UrlParseError
from .package_parser import (
    fetch_package_json,
    extract_dependencies,
    PackageParseError,
)


def print_config(config: dict) -> None:
    """
    Вывод параметров конфигурации в консоль.

    Args:
        config: Словарь с параметрами конфигурации.
    """
    print("=" * 50)
    print("Конфигурация приложения:")
    print("=" * 50)
    for key, value in config.items():
        print(f"{key}: {value}")
    print("=" * 50)


def print_dependencies(
    package_name: str, dependencies: List[str]
) -> None:
    """
    Вывод списка прямых зависимостей пакета.

    Args:
        package_name: Имя анализируемого пакета.
        dependencies: Список имён зависимостей.
    """
    print(f"\nПрямые зависимости пакета '{package_name}':")
    print("-" * 40)
    if not dependencies:
        print("  (зависимости отсутствуют)")
        return

    for index, dep in enumerate(dependencies, start=1):
        print(f"  {index}. {dep}")
    print(f"\nВсего зависимостей: {len(dependencies)}")


def process_package(config: dict) -> int:
    """
    Обработка пакета: парсинг URL, загрузка и вывод зависимостей.

    Args:
        config: Словарь с параметрами конфигурации.

    Returns:
        Код возврата (0 — успех, 1 — ошибка).
    """
    repository = config["repository"]
    package_name = config["package_name"]

    owner, repo, branch = parse_github_url(repository)
    print(f"\nРепозиторий: {owner}/{repo} (ветка {branch})")

    package_data = fetch_package_json(owner, repo, branch)
    dependencies = extract_dependencies(package_data)
    print_dependencies(package_name, dependencies)
    return 0


def main() -> int:
    """
    Точка входа в приложение.

    Returns:
        Код возврата (0 - успех, 1 - ошибка).
    """
    parser = argparse.ArgumentParser(
        description="Визуализация графа зависимостей"
    )
    parser.add_argument(
        "-c", "--config",
        default="config.json",
        help="Путь к файлу конфигурации"
    )

    args = parser.parse_args()

    try:
        loader = ConfigLoader(args.config)
        config = loader.load()
        print_config(config)
        return process_package(config)
    except ConfigError as error:
        print(f"\nОшибка конфигурации: {error}", file=sys.stderr)
        return 1
    except UrlParseError as error:
        print(f"\nОшибка URL: {error}", file=sys.stderr)
        return 1
    except PackageParseError as error:
        print(f"\nОшибка пакета: {error}", file=sys.stderr)
        return 1
    except Exception as error:
        print(f"\nНепредвиденная ошибка: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())