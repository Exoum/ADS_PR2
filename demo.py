"""Demo module."""

#!/usr/bin/env python3
"""Демонстрация всех алгоритмов поиска подстрок."""

import search

def demo_algorithms():
    """Демонстрирует работу всех алгоритмов поиска."""
    text = "ababbababa"
    pattern = "aba"

    print("Демонстрация алгоритмов поиска подстрок")
    print("=" * 50)
    print(f"Текст: '{text}'")
    print(f"Паттерн: '{pattern}'")
    print()

    # KMP
    print("1. Алгоритм Кнута-Морриса-Пратта (KMP):")
    kmp_result = search.kmp_search(text, pattern)
    print(f"   Результат: {kmp_result}")

    # Boyer-Moore
    print("2. Алгоритм Бойера-Мура:")
    bm_result = search.boyer_moore_search(text, pattern)
    print(f"   Результат: {bm_result}")

    # Boyer-Moore-Horspool
    print("3. Алгоритм Бойера-Мура-Хорспула:")
    bmh_result = search.boyer_moore_horspool_search(text, pattern)
    print(f"   Результат: {bmh_result}")

    # Rabin-Karp
    print("4. Алгоритм Рабина-Карпа:")
    rk_result = search.rabin_karp_search(text, pattern)
    print(f"   Результат: {rk_result}")

    # Aho-Corasick для множественного поиска
    print("5. Алгоритм Ахо-Корасик (множественный поиск):")
    patterns = ["aba", "bba"]
    ac = search.AhoCorasick()
    ac.build_automaton(patterns)
    ac_result = ac.search(text)
    print(f"   Паттерны: {patterns}")
    print(f"   Результат: {ac_result}")

    print()
    print("Все алгоритмы дают одинаковый результат для одиночного поиска!")

    # Демонстрация основной функции search
    print("\n" + "=" * 50)
    print("Демонстрация основной функции search():")

    # Одиночный поиск
    result1 = search.search(text, pattern)
    print(f"Поиск '{pattern}' в '{text}': {result1}")

    # Множественный поиск
    result2 = search.search(text, patterns)
    print(f"Поиск {patterns} в '{text}': {result2}")

    # С ограничением количества
    result3 = search.search(text, pattern, count=2)
    print(f"Поиск '{pattern}' (макс. 2): {result3}")

    # С конца
    result4 = search.search(text, pattern, method='last')
    print(f"Поиск '{pattern}' с конца: {result4}")

if __name__ == "__main__":
    demo_algorithms()
