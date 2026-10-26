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
from .d2_export import graph_to_d2, write_d2, render_d2, open_image


def print_config(config: dict) -> None:
    """Вывод параметров конфигурации в консоль."""
    print("=" * 50)
    print("Конфигурация приложения:")
    print("=" * 50)
    for key, value in config.items():
        print(f"{key}: {value}")
    print("=" * 50)


def print_graph(graph: DependencyGraph) -> None:
    """Вывод рёбер и размеров графа зависимостей."""
    print("\nГраф зависимостей:")
    print("-" * 40)
    for source, target in graph.edges():
        print(f"  {source} -> {target}")
    print(f"\nВсего узлов: {len(graph.nodes())}")
    print(f"Всего рёбер: {len(graph.edges())}")


def print_cycles(graph: DependencyGraph) -> None:
    """Вывод найденных циклических зависимостей."""
    cycles = graph.find_cycles()
    if not cycles:
        print("\nЦиклические зависимости не обнаружены.")
        return
    print(f"\nОбнаружены циклические зависимости ({len(cycles)}):")
    for cycle in cycles:
        print("  " + " -> ".join(cycle))


def print_load_order(
    graph: DependencyGraph, root: str, fetcher: FetchFunc
) -> None:
    """Вывод порядка загрузки зависимостей (BFS и топологический)."""
    bfs_order = bfs_load_order(root, fetcher)
    print("\nПорядок загрузки (BFS, порядок обнаружения):")
    print("  " + " -> ".join(bfs_order))
    topo_order = topological_load_order(graph)
    if not topo_order:
        print("\nТопологический порядок: не определён (в графе циклы)")
        return
    print("\nПорядок загрузки (топологический, зависимости первыми):")
    print("  " + " -> ".join(topo_order))


def export_d2(
    graph: DependencyGraph, d2_out: str, render: bool
) -> None:
    """Экспорт графа в D2 и опциональный рендер изображения."""
    text = graph_to_d2(graph)
    write_d2(text, d2_out)
    print("\nТекстовое представление графа (D2):")
    print(text, end="")
    if not render:
        print(f"\nДля рендера выполните: d2 {d2_out} {d2_out}.svg")
        return
    svg_path = d2_out + ".svg"
    if render_d2(d2_out, svg_path):
        print(f"\nИзображение построено: {svg_path}")
        open_image(svg_path)
    else:
        print("\nУтилита d2 не найдена. Установите d2 и повторите")


def process_local(
    config: dict, show_order: bool, d2_out: str, render: bool
) -> int:
    """Обработка тестового репозитория (режим local)."""
    repo = load_test_repo(config["repository"])
    fetcher = make_fetcher(repo)
    root = config["package_name"]
    graph = build_graph(root, fetcher)
    print_graph(graph)
    print_cycles(graph)
    if show_order:
        print_load_order(graph, root, fetcher)
    if d2_out:
        export_d2(graph, d2_out, render)
    return 0


def process_remote(
    config: dict, show_order: bool, d2_out: str, render: bool
) -> int:
    """Обработка реального репозитория (режим remote)."""
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
    if d2_out:
        export_d2(graph, d2_out, render)
    return 0


def main() -> int:
    """Точка входа в приложение."""
    parser = argparse.ArgumentParser(
        description="Визуализация графа зависимостей"
    )
    parser.add_argument(
        "-c", "--config", default="config.json",
        help="Путь к файлу конфигурации"
    )
    parser.add_argument(
        "--show-order", action="store_true",
        help="Вывести порядок загрузки зависимостей"
    )
    parser.add_argument(
        "--d2-out", default="",
        help="Путь к файлу D2-представления графа"
    )
    parser.add_argument(
        "--render", action="store_true",
        help="Отрендерить D2 в изображение и открыть его"
    )
    args = parser.parse_args()

    try:
        loader = ConfigLoader(args.config)
        config = loader.load()
        print_config(config)
        if config["mode"] == LOCAL_MODE:
            return process_local(
                config, args.show_order, args.d2_out, args.render
            )
        return process_remote(
            config, args.show_order, args.d2_out, args.render
        )
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