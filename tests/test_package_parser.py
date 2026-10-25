"""Тесты для модуля парсинга package.json."""
import unittest
from unittest.mock import patch, MagicMock

# ИСПРАВЛЕНО: импорт через пакет
from src.package_parser import (
    fetch_package_json,
    extract_dependencies,
    PackageParseError,
)


class TestPackageParser(unittest.TestCase):
    """Тесты функций fetch_package_json и extract_dependencies."""

    @patch("src.package_parser.urllib.request.urlopen")
    def test_fetch_success(self, mock_urlopen: MagicMock) -> None:
        """Тест успешной загрузки package.json."""
        mock_response = MagicMock()
        mock_response.read.return_value = (
            b'{"name": "test", "dependencies": {"a": "1.0"}}'
        )
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        data = fetch_package_json("owner", "repo", "main")
        self.assertEqual(data["name"], "test")

    @patch("src.package_parser.urllib.request.urlopen")
    def test_fetch_not_found(self, mock_urlopen: MagicMock) -> None:
        """Тест ошибки 404."""
        import urllib.error
        mock_urlopen.side_effect = urllib.error.HTTPError(
            "url", 404, "Not Found", {}, None
        )
        with self.assertRaises(PackageParseError):
            fetch_package_json("owner", "repo", "main")

    def test_extract_dependencies_success(self) -> None:
        """Тест извлечения зависимостей."""
        data = {
            "dependencies": {
                "z-pkg": "1.0.0",
                "a-pkg": "2.0.0",
            }
        }
        deps = extract_dependencies(data)
        self.assertEqual(deps, ["a-pkg", "z-pkg"])

    def test_extract_missing_field(self) -> None:
        """Тест отсутствия поля dependencies."""
        with self.assertRaises(PackageParseError):
            extract_dependencies({"name": "test"})

    def test_extract_invalid_type(self) -> None:
        """Тест невалидного типа данных."""
        with self.assertRaises(PackageParseError):
            extract_dependencies("not a dict")


if __name__ == "__main__":
    unittest.main()