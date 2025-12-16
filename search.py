"""Search module."""

from typing import List, Dict, Union, Optional, Tuple
import time


def timing_decorator(func):
    """Декоратор для измерения времени выполнения функции."""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Время выполнения {func.__name__}: {end_time - start_time:.6f} секунд")
        return result
    return wrapper


def compute_lps(pattern: str) -> List[int]:
    """Вычисляет массив LPS для алгоритма КМП."""
    length = 0
    lps = [0] * len(pattern)
    i = 1

    while i < len(pattern):
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1
    return lps


def kmp_search(text: str, pattern: str) -> List[int]:
    """Алгоритм Кнута-Морриса-Пратта."""
    if not pattern:
        return []

    lps = compute_lps(pattern)
    matches = []
    i = j = 0

    while i < len(text):
        if pattern[j] == text[i]:
            i += 1
            j += 1

        if j == len(pattern):
            matches.append(i - j)
            j = lps[j - 1]
        elif i < len(text) and pattern[j] != text[i]:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1

    return matches


def bad_char_table(pattern: str) -> Dict[str, int]:
    """Создает таблицу плохих символов для алгоритма Бойера-Мура."""
    table = {}
    for i in range(len(pattern)):
        table[pattern[i]] = i
    return table


def boyer_moore_search(text: str, pattern: str) -> List[int]:
    """Алгоритм Бойера-Мура."""
    if not pattern:
        return []

    bad_char = bad_char_table(pattern)
    matches = []
    shift = 0

    while shift <= len(text) - len(pattern):
        j = len(pattern) - 1

        while j >= 0 and pattern[j] == text[shift + j]:
            j -= 1

        if j < 0:
            matches.append(shift)
            shift += 1
        else:
            shift += max(1, j - bad_char.get(text[shift + j], -1))

    return matches


def boyer_moore_horspool_search(text: str, pattern: str) -> List[int]:
    """Алгоритм Бойера-Мура-Хорспула."""
    if not pattern:
        return []

    skip = {}
    for i in range(len(pattern) - 1):
        skip[pattern[i]] = len(pattern) - i - 1

    matches = []
    i = 0

    while i <= len(text) - len(pattern):
        j = len(pattern) - 1

        while j >= 0 and text[i + j] == pattern[j]:
            j -= 1

        if j < 0:
            matches.append(i)
            i += 1
        else:
            i += skip.get(text[i + len(pattern) - 1], len(pattern))

    return matches


class AhoCorasick:
    """Класс для реализации алгоритма Ахо-Корасик."""

    def __init__(self):
        self.goto = {}
        self.fail = {}
        self.output = {}

    def build_automaton(self, patterns: List[str]):
        """Строит автомат для поиска множества образцов."""
        # Построение goto функции
        for pattern in patterns:
            current_state = 0
            for char in pattern:
                if (current_state, char) not in self.goto:
                    new_state = len(self.goto) + 1
                    self.goto[(current_state, char)] = new_state
                current_state = self.goto[(current_state, char)]

            if current_state not in self.output:
                self.output[current_state] = []
            self.output[current_state].append(pattern)

        # Построение fail функции
        queue = []
        for char in set(char for (state, char) in self.goto.keys() if state == 0):
            state = self.goto[(0, char)]
            self.fail[state] = 0
            queue.append(state)

        while queue:
            r = queue.pop(0)
            for char in set(char for (state, char) in self.goto.keys() if state == r):
                u = self.goto[(r, char)]
                queue.append(u)
                state = self.fail[r]

                while state != 0 and (state, char) not in self.goto:
                    state = self.fail[state]

                if (state, char) in self.goto:
                    self.fail[u] = self.goto[(state, char)]
                else:
                    self.fail[u] = 0

                if self.fail[u] in self.output:
                    if u not in self.output:
                        self.output[u] = []
                    self.output[u].extend(self.output[self.fail[u]])

    def search(self, text: str) -> Dict[str, List[int]]:
        """Поиск всех вхождений образцов в тексте."""
        result = {}
        state = 0

        for i, char in enumerate(text):
            while state != 0 and (state, char) not in self.goto:
                state = self.fail[state]

            if (state, char) in self.goto:
                state = self.goto[(state, char)]

            if state in self.output:
                for pattern in self.output[state]:
                    if pattern not in result:
                        result[pattern] = []
                    result[pattern].append(i - len(pattern) + 1)

        return result


def rolling_hash(s: str, base: int = 256, mod: int = 101) -> int:
    """Вычисляет кольцевой хеш строки."""
    hash_value = 0
    for char in s:
        hash_value = (hash_value * base + ord(char)) % mod
    return hash_value


def rabin_karp_search(text: str, pattern: str) -> List[int]:
    """Алгоритм Рабина-Карпа с кольцевым хешем."""
    if not pattern:
        return []

    base = 256
    mod = 101
    pattern_len = len(pattern)
    text_len = len(text)

    if pattern_len > text_len:
        return []

    pattern_hash = rolling_hash(pattern, base, mod)
    text_hash = rolling_hash(text[:pattern_len], base, mod)

    h = pow(base, pattern_len - 1, mod)
    matches = []

    for i in range(text_len - pattern_len + 1):
        if pattern_hash == text_hash:
            if text[i:i + pattern_len] == pattern:
                matches.append(i)

        if i < text_len - pattern_len:
            text_hash = (text_hash - ord(text[i]) * h) % mod
            text_hash = (text_hash * base + ord(text[i + pattern_len])) % mod
            text_hash = (text_hash + mod) % mod

    return matches


@timing_decorator
def search(string: str, sub_string: Union[str, List[str]],
          case_sensitivity: bool = False, method: str = 'first',
          count: Optional[int] = None) -> Optional[Union[Tuple[int, ...], Dict[str, Tuple[int, ...]]]]:
    """
    Поиск подстрок в строке с использованием различных алгоритмов.

    Args:
        string: Исходная строка для поиска
        sub_string: Подстрока или список подстрок для поиска
        case_sensitivity: Флаг чувствительности к регистру
        method: Метод поиска ('first' или 'last')
        count: Максимальное количество совпадений

    Returns:
        Кортеж индексов для одной подстроки или словарь для нескольких подстрок
    """
    if not string:
        return None

    # Обработка регистра
    search_string = string if case_sensitivity else string.lower()

    # Обработка одной подстроки
    if isinstance(sub_string, str):
        if not sub_string:
            return None

        pattern = sub_string if case_sensitivity else sub_string.lower()
        matches = kmp_search(search_string, pattern)

        if not matches:
            return None

        # Обработка направления поиска
        if method == 'last':
            matches = matches[::-1]

        # Ограничение количества результатов
        if count is not None:
            matches = matches[:count]

        return tuple(matches) if matches else None

    # Обработка множества подстрок
    if isinstance(sub_string, (list, tuple)):
        if not sub_string:
            return None

        patterns = [p if case_sensitivity else p.lower() for p in sub_string if p]
        if not patterns:
            return None

        # Используем алгоритм Ахо-Корасик для множественного поиска
        ac = AhoCorasick()
        ac.build_automaton(patterns)
        all_matches = ac.search(search_string)

        # Собираем все совпадения с информацией о паттерне
        all_results = []
        for pattern, positions in all_matches.items():
            for pos in positions:
                all_results.append((pos, pattern))

        # Сортируем по позиции
        all_results.sort(key=lambda x: x[0])

        # Обработка направления поиска
        if method == 'last':
            all_results = all_results[::-1]

        # Ограничение общего количества результатов
        if count is not None:
            all_results = all_results[:count]

        # Группируем результаты по паттернам
        result = {}
        for original_pattern in sub_string:
            pattern = original_pattern if case_sensitivity else original_pattern.lower()
            matches = [pos for pos, p in all_results if p == pattern]
            result[original_pattern] = tuple(matches) if matches else None

        return result if any(v is not None for v in result.values()) else None

    return None
