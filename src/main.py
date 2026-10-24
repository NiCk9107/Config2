"""Главный модуль CLI-приложения визуализации графа зависимостей."""
import sys
import argparse
from src.config_loader import ConfigLoader, ConfigError


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
        print("\nКонфигурация успешно загружена и валидна.")
        return 0
    except ConfigError as error:
        print(f"\nОшибка конфигурации: {error}", file=sys.stderr)
        return 1
    except Exception as error:
        print(f"\nНепредвиденная ошибка: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())