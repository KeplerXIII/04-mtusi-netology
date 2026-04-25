#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from eval.calc import calculate_cost


def print_cost(title: str, result: dict) -> None:
    print(f"=== {title} ===")
    print(f"Запросов/месяц: {result['requests_month']:,}")
    print(f"Input tokens/month: {result['total_input_tokens']:,}")
    print(f"Output tokens/month: {result['total_output_tokens']:,}")
    print(f"Input: ${result['input_cost']}")
    print(f"Output: ${result['output_cost']}")
    print(f"Итого: ${result['total_monthly']}/мес")
    print(f"За запрос: ${result['cost_per_request']}")
    print()


# =========================
# Сценарий 1: Web scraping + первичная оценка материалов
# =========================
# Система ежедневно получает статьи/новости/публикации,
# очищает текст, оценивает релевантность и присваивает категорию.

scraping_analysis = calculate_cost(
    requests_per_day=500,
    avg_input_tokens=1800,    # текст статьи + инструкция оценки
    avg_output_tokens=250,    # категория, краткая оценка, признаки релевантности
    input_price_per_m=0.10,   # условно дешёвая модель для первичной фильтрации
    output_price_per_m=0.40,
    cache_ratio=0.4,          # часть промпта стабильная, сами статьи разные
    cache_discount=0.9,
)

print_cost(
    "Сценарий 1: Web scraping + первичная оценка материалов",
    scraping_analysis,
)


# =========================
# Сценарий 2: Генерация отчётов и дайджестов
# =========================
# На основе отобранных материалов система готовит
# ежедневные дайджесты, аналитические справки и краткие отчёты.

report_generation = calculate_cost(
    requests_per_day=80,
    avg_input_tokens=6000,    # подборка материалов за период
    avg_output_tokens=1200,   # развёрнутый отчёт/дайджест
    input_price_per_m=0.50,   # более сильная модель для синтеза текста
    output_price_per_m=3.00,
    cache_ratio=0.25,         # материалы разные, кэшируется только шаблон инструкции
    cache_discount=0.9,
)

print_cost(
    "Сценарий 2: Генерация отчётов и дайджестов",
    report_generation,
)


# =========================
# Сценарий 3: RAG по базе материалов
# =========================
# Пользователь задаёт вопросы по накопленным материалам.
# Во входной контекст попадает вопрос + найденные фрагменты.

rag_materials = calculate_cost(
    requests_per_day=1000,
    avg_input_tokens=2500,    # вопрос + 3-5 найденных chunks
    avg_output_tokens=600,    # ответ со ссылками/обоснованием
    input_price_per_m=0.50,
    output_price_per_m=3.00,
    cache_ratio=0.35,         # system prompt стабилен, документы разные
    cache_discount=0.9,
)

print_cost(
    "Сценарий 3: Работа с RAG по накопленным материалам",
    rag_materials,
)


# =========================
# Сценарий 4: Работа с ЛНА в RAG
# =========================
# Пользователь задаёт вопросы по локальным нормативным актам:
# регламенты, инструкции, приказы, положения.
# Требуется высокая точность и осторожность против галлюцинаций.

rag_lna = calculate_cost(
    requests_per_day=300,
    avg_input_tokens=4500,    # вопрос + фрагменты ЛНА + системные ограничения
    avg_output_tokens=800,    # официальный ответ с указанием оснований
    input_price_per_m=0.50,
    output_price_per_m=3.00,
    cache_ratio=0.45,         # часть ЛНА и системной инструкции может повторяться
    cache_discount=0.9,
)

print_cost(
    "Сценарий 4: Работа с ЛНА в RAG",
    rag_lna,
)


# =========================
# Итог
# =========================

total_monthly = (
    scraping_analysis["total_monthly"]
    + report_generation["total_monthly"]
    + rag_materials["total_monthly"]
    + rag_lna["total_monthly"]
)

total_requests = (
    scraping_analysis["requests_month"]
    + report_generation["requests_month"]
    + rag_materials["requests_month"]
    + rag_lna["requests_month"]
)

print("=" * 80)
print("ИТОГО ПО ВСЕМ СЦЕНАРИЯМ")
print("=" * 80)
print(f"Запросов/месяц: {total_requests:,}")
print(f"Итого: ${round(total_monthly, 2)}/мес")
print()