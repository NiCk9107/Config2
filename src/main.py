"""Главный модуль CLI-приложения визуализации графа зависимостей."""
import sys
import argparse

from .config_loader import ConfigLoader, ConfigError, LOCAL_MODE
from .url_parser import parse_github_url, UrlParseError
from .package_parser import (
    fetch_with_fallback,
    extract_dependencies,
    PackageParseError,
)
from .graph import DependencyGraph
from .graph_builder import build_graph, FetchFunc
from .test_repo import load_test_repo, make_fetcher, TestRepoError
from .registry_parser import make_remote_fetcher, RegistryError
from .load_order import bfs_load_order, topological_load_order


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


def print_graph(graph: DependencyGraph) -> None:
    """
    Вывод рёбер и размеров графа зависимостей.

    Args:
        graph: Построенный граф зависимостей.
    """
    print("\nГраф зависимостей:")
    print("-" * 40)
    for source, target in graph.edges():
        print(f"  {source} -> {target}")
    print(f"\nВсего узлов: {len(graph.nodes())}")
    print(f"Всего рёбер: {len(graph.edges())}")


def print_cycles(graph: DependencyGraph) -> None:
    """
    Вывод найденных циклических зависимостей.

    Args:
        graph: Построенный граф зависимостей.
    """
    cycles = graph.find_cycles()
    if not cycles:
        print("\nЦиклические зависимости не обнаружены.")
        return
    print(f"\nОбнаружены циклические зависимости ({len(cycles)}):")
    for cycle in cycles:
        print("  " + " -> ".join(cycle))


def print_load_order(
    graph: DependencyGraph,
    root: str,
    fetcher: FetchFunc,
) -> None:
    """
    Вывод порядка загрузки зависимостей (BFS и топологический).

    Args:
        graph: Построенный граф зависимостей.
        root: Имя корневого пакета.
        fetcher: Функция получения зависимостей пакета.
    """
    bfs_order = bfs_load_order(root, fetcher)
    print("\nПорядок загрузки (BFS, порядок обнаружения):")
    print("  " + " -> ".join(bfs_order))

    topo_order = topological_load_order(graph)
    if not topo_order:
        print("\nТопологический порядок: не определён (в графе циклы)")
        return
    print("\nПорядок загрузки (топологический, зависимости первыми):")
    print("  " + " -> ".join(topo_order))


def process_local(config: dict, show_order: bool) -> int:
    """
    Обработка тестового репозитория (режим local).

    Args:
        config: Словарь с параметрами конфигурации.
        show_order: Флаг вывода порядка загрузки.

    Returns:
        Код возврата (0 — успех).
    """
    repo = load_test_repo(config["repository"])
    fetcher = make_fetcher(repo)
    root = config["package_name"]
    graph = build_graph(root, fetcher)
    print_graph(graph)
    print_cycles(graph)
    if show_order:
        print_load_order(graph, root, fetcher)
    return 0


def process_remote(config: dict, show_order: bool) -> int:
    """
    Обработка реального репозитория (режим remote).

    Args:
        config: Словарь с параметрами конфигурации.
        show_order: Флаг вывода порядка загрузки.

    Returns:
        Код возврата (0 — успех).
    """
    owner, repo_name, branch = parse_github_url(config["repository"])
    print(f"\nРепозиторий: {owner}/{repo_name} (ветка {branch})")
    data = fetch_with_fallback(owner, repo_name, branch)
    root_deps = {config["package_name"]: extract_dependencies(data)}
    fetcher = make_remote_fetcher(root_deps)
    root = config["package_name"]
    graph = build_graph(root, fetcher)
    print_graph(graph)
    print_cycles(graph)
    if show_order:
        print_load_order(graph, root, fetcher)
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
    parser.add_argument(
        "--show-order",
        action="store_true",
        help="Вывести порядок загрузки зависимостей"
    )

    args = parser.parse_args()

    try:
        loader = ConfigLoader(args.config)
        config = loader.load()
        print_config(config)
        if config["mode"] == LOCAL_MODE:
            return process_local(config, args.show_order)
        return process_remote(config, args.show_order)
    except ConfigError as error:
        print(f"\nОшибка конфигурации: {error}", file=sys.stderr)
        return 1
    except UrlParseError as error:
        print(f"\nОшибка URL: {error}", file=sys.stderr)
        return 1
    except (PackageParseError, TestRepoError, RegistryError) as error:
        print(f"\nОшибка данных: {error}", file=sys.stderr)
        return 1
    except Exception as error:
        print(f"\nНепредвиденная ошибка: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())