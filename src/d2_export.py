"""Экспорт графа зависимостей в язык D2 и рендер изображения."""
import os
import subprocess
import sys
from typing import List

from .graph import DependencyGraph


def graph_to_d2(graph: DependencyGraph) -> str:
    """
    Формирование текстового представления графа на языке D2.

    Args:
        graph: Построенный граф зависимостей.

    Returns:
        Строка с D2-описанием: узлы и рёбра графа.
    """
    lines: List[str] = [f'"{node}"' for node in graph.nodes()]
    lines += [
        f'"{source}" -> "{target}"'
        for source, target in graph.edges()
    ]
    return "\n".join(lines) + "\n"


def write_d2(text: str, path: str) -> None:
    """
    Запись D2-представления в файл.

    Args:
        text: D2-представление графа.
        path: Путь к выходному файлу .d2.
    """
    with open(path, "w", encoding="utf-8") as file:
        file.write(text)


def render_d2(d2_path: str, out_path: str) -> bool:
    """
    Рендер файла .d2 в изображение через CLI-утилиту d2.

    Args:
        d2_path: Путь к исходному файлу .d2.
        out_path: Путь к итоговому изображению.

    Returns:
        True, если рендер успешен; иначе False.
    """
    try:
        subprocess.run(
            ["d2", d2_path, out_path],
            check=True,
            capture_output=True,
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def open_image(path: str) -> None:
    """
    Открытие изображения системным просмотрщиком.

    Args:
        path: Путь к файлу изображения.
    """
    if sys.platform == "win32":
        os.startfile(path)  # type: ignore[attr-defined]
    else:
        subprocess.Popen(["xdg-open", path])