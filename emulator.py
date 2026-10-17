"""
Этап 1. Минимальный прототип с конфигурацией.
Инструмент визуализации графа зависимостей для менеджера пакетов.
"""

import json
import sys
import os


# Допустимые режимы работы с тестовым репозиторием
VALID_MODES = {"online", "local", "mock"}

# Путь к конфигурационному файлу (по умолчанию — в той же папке, что и скрипт)
DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")


def load_config(path: str) -> dict:
    """
    Загружает и парсит JSON-файл конфигурации.
    Обрабатывает ошибки: файл не найден, невалидный JSON.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Конфигурационный файл не найден: '{path}'")

    try:
        with open(path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Невалидный JSON в файле '{path}': {e}")

    if not isinstance(config, dict):
        raise ValueError(f"Ожидается JSON-объект (словарь), получено: {type(config).__name__}")

    return config


def validate_config(config: dict) -> dict:
    """
    Проверяет наличие и корректность всех обязательных параметров.
    Возвращает нормализованный словарь параметров.
    """
    required_keys = {
        "package_name": str,
        "repository_url": str,
        "repository_path": str,
        "test_repo_mode": str,
    }

    # Проверка наличия всех обязательных ключей
    for key, expected_type in required_keys.items():
        if key not in config:
            raise KeyError(f"Отсутствует обязательный параметр: '{key}'")
        if not isinstance(config[key], expected_type):
            raise TypeError(
                f"Параметр '{key}' должен быть типа {expected_type.__name__}, "
                f"получено: {type(config[key]).__name__}"
            )

    # Нормализация: убираем лишние пробелы
    package_name = config["package_name"].strip()
    repository_url = config["repository_url"].strip()
    repository_path = config["repository_path"].strip()
    test_repo_mode = config["test_repo_mode"].strip().lower()

    # Проверка на пустые значения
    if not package_name:
        raise ValueError("Параметр 'package_name' не может быть пустым")

    if not test_repo_mode:
        raise ValueError("Параметр 'test_repo_mode' не может быть пустым")

    # Проверка режима работы
    if test_repo_mode not in VALID_MODES:
        raise ValueError(
            f"Недопустимый режим работы '{test_repo_mode}'. "
            f"Допустимые значения: {', '.join(sorted(VALID_MODES))}"
        )

    # Логические проверки в зависимости от режима
    if test_repo_mode == "online" and not repository_url:
        raise ValueError(
            "В режиме 'online' параметр 'repository_url' должен быть заполнен"
        )

    if test_repo_mode == "local":
        if not repository_path:
            raise ValueError(
                "В режиме 'local' параметр 'repository_path' должен быть заполнен"
            )
        if not os.path.exists(repository_path):
            raise FileNotFoundError(
                f"Путь к тестовому репозиторию не существует: '{repository_path}'"
            )

    return {
        "package_name": package_name,
        "repository_url": repository_url,
        "repository_path": repository_path,
        "test_repo_mode": test_repo_mode,
    }


def print_parameters(params: dict) -> None:
    """Выводит все настраиваемые параметры в формате ключ-значение."""
    print("=" * 50)
    print("  Параметры конфигурации")
    print("=" * 50)
    for key, value in params.items():
        # Для наглядности пустые значения помечаем
        display_value = value if value else "<не задано>"
        print(f"  {key:<20} : {display_value}")
    print("=" * 50)


def main() -> int:
    """Точка входа в CLI-приложение. Возвращает код завершения."""
    # Путь к конфигу можно передать как аргумент командной строки
    config_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CONFIG_PATH

    print(f"[INFO] Загрузка конфигурации из: {config_path}\n")

    try:
        raw_config = load_config(config_path)
        params = validate_config(raw_config)
    except FileNotFoundError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 2
    except (KeyError, TypeError, ValueError) as e:
        print(f"[ERROR] Ошибка валидации конфигурации: {e}", file=sys.stderr)
        return 3

    print_parameters(params)

    print("\n[OK] Конфигурация успешно загружена. Этап 1 завершён.")
    return 0


if __name__ == "__main__":
    sys.exit(main())