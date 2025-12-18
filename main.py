"""Консольная утилита для поиска подстрок в строке или файле."""

import argparse
import sys
from pathlib import Path
from typing import List, Union, Dict, Tuple, Optional
import search


class Colors:
    """Класс для цветового выделения текста в консоли."""
    RESET = '\033[0m'
    COLORS = [
        '\033[91m',  # Красный
        '\033[92m',  # Зеленый
        '\033[93m',  # Желтый
        '\033[94m',  # Синий
        '\033[95m',  # Пурпурный
        '\033[96m',  # Голубой
    ]

    @classmethod
    def get_color(cls, index: int) -> str:
        """Получить цвет по индексу."""
        return cls.COLORS[index % len(cls.COLORS)]


def highlight_matches(text: str, matches_dict: Dict[str, Tuple[int, ...]],
                     max_lines: int = 10) -> str:
    """
    Выделяет найденные подстроки цветом в тексте.

    Args:
        text: Исходный текст
        matches_dict: Словарь с найденными совпадениями
        max_lines: Максимальное количество строк для вывода

    Returns:
        Текст с цветовым выделением
    """
    if not matches_dict:
        return text

    # Создаем список всех позиций для выделения
    highlights = []
    color_map = {}
    color_index = 0

    for pattern, positions in matches_dict.items():
        if positions:
            color = Colors.get_color(color_index)
            color_map[pattern] = color
            for pos in positions:
                highlights.append((pos, pos + len(pattern), color, pattern))
            color_index += 1

    # Сортируем по позиции
    highlights.sort(key=lambda x: x[0])

    # Применяем выделение
    result = ""
    last_pos = 0

    for start, end, color, pattern in highlights:
        if start >= last_pos:
            result += text[last_pos:start]
            result += color + text[start:end] + Colors.RESET
            last_pos = end

    result += text[last_pos:]

    # Ограничиваем количество строк
    lines = result.split('\n')
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines.append(f"... (показано {max_lines} из {len(result.split())} строк)")

    return '\n'.join(lines)


def read_file(file_path: str) -> str:
    """
    Читает содержимое файла.

    Args:
        file_path: Путь к файлу

    Returns:
        Содержимое файла
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Ошибка: Файл '{file_path}' не найден.")
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        sys.exit(1)


def format_results(results: Union[Tuple[int, ...], Dict[str, Tuple[int, ...]], None],
                  patterns: Union[str, List[str]]) -> str:
    """
    Форматирует результаты поиска для вывода.

    Args:
        results: Результаты поиска
        patterns: Искомые подстроки

    Returns:
        Отформатированная строка результатов
    """
    if results is None:
        return "Совпадений не найдено."

    if isinstance(results, tuple):
        return f"Найдено {len(results)} совпадений на позициях: {results}"

    if isinstance(results, dict):
        output = []
        total_matches = 0
        for pattern, positions in results.items():
            if positions:
                output.append(f"'{pattern}': {positions}")
                total_matches += len(positions)
            else:
                output.append(f"'{pattern}': не найдено")

        result_str = "\n".join(output)
        result_str += f"\n\nВсего найдено {total_matches} совпадений."
        return result_str

    return str(results)


def main():
    """Главная функция консольной утилиты."""
    parser = argparse.ArgumentParser(
        description="Поиск подстрок в строке или файле с использованием различных алгоритмов."
    )

    # Основные параметры
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-s', '--string', type=str, help="Строка для поиска")
    group.add_argument('-f', '--file', type=str, help="Путь к файлу для поиска")

    parser.add_argument('patterns', nargs='+', help="Подстроки для поиска")

    # Опциональные параметры
    parser.add_argument('-c', '--case-sensitive', action='store_true',
                       help="Учитывать регистр символов")
    parser.add_argument('-m', '--method', choices=['first', 'last'], default='first',
                       help="Направление поиска (по умолчанию: first)")
    parser.add_argument('-k', '--count', type=int,
                       help="Максимальное количество совпадений")
    parser.add_argument('--no-highlight', action='store_true',
                       help="Отключить цветовое выделение")
    parser.add_argument('--max-lines', type=int, default=10,
                       help="Максимальное количество строк для вывода (по умолчанию: 10)")

    args = parser.parse_args()

    # Получаем текст для поиска
    if args.string:
        text = args.string
    else:
        text = read_file(args.file)
    
    # Проверка на пустую строку или строку только с пробелами
    if text is None or text == "" or text.isspace():
        print("Ошибка: Строка для поиска пустая.")
        sys.exit(1)

    # Подготавливаем паттерны
    patterns = args.patterns[0] if len(args.patterns) == 1 else args.patterns

    # Выполняем поиск
    print("Выполняется поиск...")
    results = search.search(
        string=text,
        sub_string=patterns,
        case_sensitivity=args.case_sensitive,
        method=args.method,
        count=args.count
    )

    # Выводим результаты
    print("\nРезультаты поиска:")
    print(format_results(results, patterns))

    # Выводим текст с выделением (если есть совпадения и не отключено)
    if not args.no_highlight and results:
        print(f"\nТекст с выделением (максимум {args.max_lines} строк):")

        if isinstance(results, tuple) and len(args.patterns) == 1:
            # Для одной подстроки
            matches_dict = {args.patterns[0]: results}
        elif isinstance(results, dict):
            # Для множества подстрок
            matches_dict = results
        else:
            matches_dict = {}

        highlighted_text = highlight_matches(text, matches_dict, args.max_lines)
        print(highlighted_text)

        # Показываем легенду цветов
        if matches_dict:
            print("\nЛегенда цветов:")
            color_index = 0
            for pattern, positions in matches_dict.items():
                if positions:
                    color = Colors.get_color(color_index)
                    print(f"{color}*{Colors.RESET} - '{pattern}'")
                    color_index += 1


if __name__ == "__main__":
    main()
