#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import json
import os
import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from eval.config import (
    LOCAL_MODELS,
    OPENROUTER_MODEL,
    MAX_TOKENS,
    TEMPERATURE,
)
from eval.tasks import TASKS


# =========================
# .env
# =========================

load_dotenv()


# =========================
# API
# =========================

OLLAMA_BASE_URL = "http://127.0.0.1:11434/v1"
OLLAMA_API_KEY = "ollama"

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


# =========================
# Результаты
# =========================

RESULTS_DIR = Path("eval_results")
RESULTS_DIR.mkdir(exist_ok=True)


def make_client(base_url: str, api_key: str) -> OpenAI:
    return OpenAI(
        base_url=base_url,
        api_key=api_key,
    )


def call_model(client: OpenAI, model: str, prompt: str) -> dict:
    started_at = time.perf_counter()
    first_token_at = None
    output_chunks = []

    stream = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        stream=True,
    )

    for chunk in stream:
        delta = chunk.choices[0].delta.content

        if delta:
            if first_token_at is None:
                first_token_at = time.perf_counter()

            output_chunks.append(delta)

    finished_at = time.perf_counter()

    answer = "".join(output_chunks)

    ttft = None
    if first_token_at is not None:
        ttft = first_token_at - started_at

    total_time = finished_at - started_at

    output_tokens = max(1, len(answer.split()))
    throughput = output_tokens / total_time if total_time > 0 else 0

    return {
        "answer": answer,
        "ttft": ttft,
        "total_time": total_time,
        "output_tokens": output_tokens,
        "throughput": throughput,
    }


def run_eval_for_model(model_name: str, client: OpenAI) -> list[dict]:
    rows = []

    print("=" * 80)
    print(f"MODEL: {model_name}")
    print("=" * 80)

    for task in TASKS:
        print(f"[RUN] {task.id} | {task.category}")

        try:
            result = call_model(
                client=client,
                model=model_name,
                prompt=task.prompt,
            )

            answer = result["answer"]
            passed = task.check(answer)

            row = {
                "model": model_name,
                "task_id": task.id,
                "category": task.category,
                "passed": passed,
                "ttft": result["ttft"],
                "total_time": result["total_time"],
                "output_tokens": result["output_tokens"],
                "throughput": result["throughput"],
                "answer": answer,
                "error": "",
            }

            ttft_text = (
                f"{result['ttft']:.2f}s"
                if result["ttft"] is not None
                else "N/A"
            )

            print(
                f"  passed={passed} | "
                f"ttft={ttft_text} | "
                f"throughput={result['throughput']:.2f} tok/s"
            )

        except Exception as e:
            row = {
                "model": model_name,
                "task_id": task.id,
                "category": task.category,
                "passed": False,
                "ttft": None,
                "total_time": None,
                "output_tokens": 0,
                "throughput": 0,
                "answer": "",
                "error": str(e),
            }

            print(f"  ERROR: {e}")

        rows.append(row)

    return rows


def print_summary(rows: list[dict]) -> None:
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)

    models = sorted(set(row["model"] for row in rows))

    for model in models:
        model_rows = [row for row in rows if row["model"] == model]

        total = len(model_rows)
        passed = sum(1 for row in model_rows if row["passed"])
        accuracy = passed / total * 100 if total else 0

        ttft_values = [
            row["ttft"]
            for row in model_rows
            if row["ttft"] is not None
        ]

        throughput_values = [
            row["throughput"]
            for row in model_rows
            if row["throughput"]
        ]

        avg_ttft = sum(ttft_values) / len(ttft_values) if ttft_values else 0

        avg_throughput = (
            sum(throughput_values) / len(throughput_values)
            if throughput_values
            else 0
        )

        print(
            f"{model}: "
            f"accuracy={accuracy:.1f}% | "
            f"passed={passed}/{total} | "
            f"avg_ttft={avg_ttft:.2f}s | "
            f"avg_throughput={avg_throughput:.2f} tok/s"
        )


def save_results(rows: list[dict]) -> None:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    json_path = RESULTS_DIR / f"benchmark_{timestamp}.json"
    csv_path = RESULTS_DIR / f"benchmark_{timestamp}.csv"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)

    fieldnames = [
        "model",
        "task_id",
        "category",
        "passed",
        "ttft",
        "total_time",
        "output_tokens",
        "throughput",
        "answer",
        "error",
    ]

    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)

    print()
    print(f"[OK] JSON: {json_path}")
    print(f"[OK] CSV:  {csv_path}")


def main() -> None:
    all_rows = []

    print("=" * 80)
    print("MODEL EVALUATION BENCHMARK")
    print("=" * 80)

    print(f"Local models: {LOCAL_MODELS}")
    print(f"OpenRouter model: {OPENROUTER_MODEL}")
    print(f"Tasks: {len(TASKS)}")
    print()

    ollama_client = make_client(
        base_url=OLLAMA_BASE_URL,
        api_key=OLLAMA_API_KEY,
    )

    for model in LOCAL_MODELS:
        rows = run_eval_for_model(
            model_name=model,
            client=ollama_client,
        )
        all_rows.extend(rows)

    if not OPENROUTER_API_KEY:
        print()
        print("[WARN] OPENROUTER_API_KEY не найден в .env")
        print("[WARN] OpenRouter модель будет пропущена.")
    else:
        openrouter_client = make_client(
            base_url=OPENROUTER_BASE_URL,
            api_key=OPENROUTER_API_KEY,
        )

        rows = run_eval_for_model(
            model_name=OPENROUTER_MODEL,
            client=openrouter_client,
        )
        all_rows.extend(rows)

    print_summary(all_rows)
    save_results(all_rows)


if __name__ == "__main__":
    main()