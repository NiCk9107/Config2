"""Модуль для загрузки и валидации конфигурации приложения."""
import json
import os
from typing import Any, Dict

MAX_NAME_LENGTH = 100
VALID_MODES = ("local", "remote")
REQUIRED_FIELDS = ("package_name", "repository", "mode")


class ConfigError(Exception):
    """Исключение, возникающее при ошибках конфигурации."""
    pass


class ConfigLoader:
    """Загрузчик конфигурации из JSON файла с валидацией."""

    def __init__(self, config_path: str) -> None:
        """
        Инициализация загрузчика.

        Args:
            config_path: Путь к файлу конфигурации JSON.
        """
        self.config_path = config_path
        self.config: Dict[str, Any] = {}

    def load(self) -> Dict[str, Any]:
        """
        Загрузка и валидация конфигурации.

        Returns:
            Словарь с параметрами конфигурации.

        Raises:
            ConfigError: Если файл не найден или невалиден.
        """
        if not os.path.exists(self.config_path):
            msg = f"Файл конфигурации не найден: {self.config_path}"
            raise ConfigError(msg)

        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                self.config = json.load(file)
        except json.JSONDecodeError as error:
            raise ConfigError(f"Ошибка парсинга JSON: {error}")

        self._validate()
        return self.config

    def _validate(self) -> None:
        """Проверка наличия и корректности всех обязательных полей."""
        for field in REQUIRED_FIELDS:
            if field not in self.config:
                raise ConfigError(f"Отсутствует поле: {field}")

        self._validate_package_name()
        self._validate_repository()
        self._validate_mode()

    def _validate_package_name(self) -> None:
        """Валидация имени пакета."""
        name = self.config["package_name"]
        if not isinstance(name, str):
            raise ConfigError("package_name должен быть строкой")
        if not name.strip():
            raise ConfigError("package_name не может быть пустым")
        if len(name) > MAX_NAME_LENGTH:
            msg = f"package_name слишком длинный (макс. {MAX_NAME_LENGTH})"
            raise ConfigError(msg)

    def _validate_repository(self) -> None:
        """Валидация пути или URL репозитория."""
        repo = self.config["repository"]
        if not isinstance(repo, str):
            raise ConfigError("repository должен быть строкой")
        if not repo.strip():
            raise ConfigError("repository не может быть пустым")

        is_url = repo.startswith(("http://", "https://", "git://"))
        is_path = os.path.exists(repo) or repo.startswith(
            ("/", "./", "../", "~")
        )

        if not is_url and not is_path:
            msg = f"Невалидный repository: {repo}"
            raise ConfigError(msg)

    def _validate_mode(self) -> None:
        """Валидация режима работы."""
        mode = self.config["mode"]
        if not isinstance(mode, str):
            raise ConfigError("mode должен быть строкой")
        if mode not in VALID_MODES:
            modes_str = ", ".join(VALID_MODES)
            raise ConfigError(f"mode должен быть: {modes_str}")