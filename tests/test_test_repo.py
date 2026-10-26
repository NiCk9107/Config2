"""Тесты загрузчика тестового репозитория."""
import json
import os
import tempfile
import unittest

from src.test_repo import load_test_repo, make_fetcher, TestRepoError


class TestTestRepo(unittest.TestCase):
    """Тесты функций load_test_repo и make_fetcher."""

    def _write(self, data) -> str:
        """Запись данных во временный файл."""
        handle = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        )
        json.dump(data, handle)
        handle.close()
        return handle.name

    def test_load_valid(self) -> None:
        """Тест загрузки валидного описания графа."""
        path = self._write({"A": ["B"], "B": []})
        repo = load_test_repo(path)
        self.assertEqual(repo["A"], ["B"])
        os.unlink(path)

    def test_missing_file(self) -> None:
        """Тест отсутствия файла."""
        with self.assertRaises(TestRepoError):
            load_test_repo("no_such_file.json")

    def test_lowercase_name_rejected(self) -> None:
        """Тест отклонения строчных имён пакетов."""
        path = self._write({"a": ["B"]})
        with self.assertRaises(TestRepoError):
            load_test_repo(path)
        os.unlink(path)

    def test_fetcher_unknown_package(self) -> None:
        """Тест fetcher для неизвестного пакета."""
        fetcher = make_fetcher({"A": ["B"]})
        self.assertEqual(fetcher("Z"), [])


if __name__ == "__main__":
    unittest.main()