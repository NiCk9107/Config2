"""Модульные тесты для загрузчика конфигурации."""
import json
import os
import unittest
import tempfile
from src.config_loader import ConfigLoader, ConfigError


class TestConfigLoader(unittest.TestCase):
    """Тесты для класса ConfigLoader."""

    def setUp(self) -> None:
        """Создание временного файла для тестов."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.valid_config_path = os.path.join(
            self.temp_dir.name, "valid.json"
        )
        config_data = {
            "package_name": "test-pkg",
            "repository": "https://github.com/test/repo.git",
            "mode": "remote"
        }
        with open(self.valid_config_path, "w", encoding="utf-8") as file:
            json.dump(config_data, file)

    def tearDown(self) -> None:
        """Очистка временных файлов."""
        self.temp_dir.cleanup()

    def test_load_valid_config(self) -> None:
        """Тест успешной загрузки валидной конфигурации."""
        loader = ConfigLoader(self.valid_config_path)
        config = loader.load()
        self.assertEqual(config["package_name"], "test-pkg")

    def test_missing_file(self) -> None:
        """Тест ошибки при отсутствии файла."""
        loader = ConfigLoader("nonexistent.json")
        with self.assertRaises(ConfigError):
            loader.load()

    def test_invalid_mode(self) -> None:
        """Тест ошибки при невалидном режиме."""
        invalid_path = os.path.join(self.temp_dir.name, "invalid.json")
        with open(invalid_path, "w", encoding="utf-8") as file:
            json.dump({
                "package_name": "test",
                "repository": "https://test.com",
                "mode": "wrong_mode"
            }, file)
        loader = ConfigLoader(invalid_path)
        with self.assertRaises(ConfigError):
            loader.load()


if __name__ == "__main__":
    unittest.main()