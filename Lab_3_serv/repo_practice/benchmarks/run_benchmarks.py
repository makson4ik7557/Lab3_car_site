"""
Модуль для оркестрації та управління бенчмарк експериментами
Включає вимірювання CPU, пам'яті та збереження результатів
"""
import psutil
import os
import time
from typing import Dict, Any, List, Tuple


def measure_resources_before():
    """
    Вимірює стан ресурсів перед запуском бенчмарка
    """
    process = psutil.Process(os.getpid())
    return {
        'cpu_percent': psutil.cpu_percent(interval=0.1),
        'memory_percent': process.memory_percent(),
        'memory_info': process.memory_info().rss / 1024 / 1024  # MB
    }


def measure_resources_after():
    """
    Вимірює стан ресурсів після запуску бенчмарка
    """
    process = psutil.Process(os.getpid())
    return {
        'cpu_percent': psutil.cpu_percent(interval=0.1),
        'memory_percent': process.memory_percent(),
        'memory_info': process.memory_info().rss / 1024 / 1024  # MB
    }


def run_experiment(execution_type: str = 'threading',
                  num_workers: int = 4,
                  num_queries: int = 100,
                  batch_size: int = 10) -> Any:
    """
    Запускає експеримент з бенчмаркінгу та зберігає результати

    Args:
        execution_type: Тип виконання ('threading' або 'multiprocessing')
        num_workers: Кількість потоків/процесів
        num_queries: Кількість запитів для виконання
        batch_size: Розмір пакету запитів

    Returns:
        BenchmarkResult: Збережений об'єкт з результатами
    """
    from repo_practice.models import BenchmarkResult

    # Вимірюємо початковий стан ресурсів
    resources_before = measure_resources_before()

    # Запускаємо відповідний бенчмарк
    if execution_type == 'threading':
        from repo_practice.benchmarks.threading_executor import run_threading_benchmark
        result = run_threading_benchmark(num_workers=num_workers, num_queries=num_queries)
    elif execution_type == 'multiprocessing':
        from repo_practice.benchmarks.multiprocessing_executor import run_multiprocessing_benchmark
        result = run_multiprocessing_benchmark(num_workers=num_workers, num_queries=num_queries)
    else:
        raise ValueError(f"Unknown execution_type: {execution_type}")

    # Вимірюємо кінцевий стан ресурсів
    resources_after = measure_resources_after()

    # Розраховуємо середнє використання ресурсів
    cpu_usage = (resources_before['cpu_percent'] + resources_after['cpu_percent']) / 2
    memory_usage = (resources_before['memory_percent'] + resources_after['memory_percent']) / 2

    # Зберігаємо результат в базу даних
    benchmark = BenchmarkResult.objects.create(
        execution_type=execution_type,
        num_workers=num_workers,
        batch_size=batch_size,
        num_queries=num_queries,
        execution_time=result['execution_time'],
        cpu_usage=cpu_usage,
        memory_usage=memory_usage
    )

    return benchmark


def run_multiple_experiments(
    execution_types: List[str] = None,
    worker_counts: List[int] = None,
    query_counts: List[int] = None,
    batch_sizes: List[int] = None
) -> List[Any]:
    """
    Запускає серію експериментів з різними параметрами
    Корисно для пошуку оптимальних параметрів

    Args:
        execution_types: Список типів виконання
        worker_counts: Список кількостей workers
        query_counts: Список кількостей запитів
        batch_sizes: Список розмірів пакетів

    Returns:
        List[BenchmarkResult]: Список всіх результатів експериментів
    """
    if execution_types is None:
        execution_types = ['threading', 'multiprocessing']
    if worker_counts is None:
        worker_counts = [2, 4, 8, 16]
    if query_counts is None:
        query_counts = [100]
    if batch_sizes is None:
        batch_sizes = [10, 20, 50]

    results = []
    total_experiments = len(execution_types) * len(worker_counts) * len(query_counts) * len(batch_sizes)
    current = 0

    for exec_type in execution_types:
        for workers in worker_counts:
            for queries in query_counts:
                for batch in batch_sizes:
                    current += 1
                    print(f"Running experiment {current}/{total_experiments}: "
                          f"{exec_type}, workers={workers}, queries={queries}, batch={batch}")

                    try:
                        result = run_experiment(
                            execution_type=exec_type,
                            num_workers=workers,
                            num_queries=queries,
                            batch_size=batch
                        )
                        results.append(result)
                        print(f"Completed in {result.execution_time:.2f}s")
                    except Exception as e:
                        print(f"Failed: {e}")

                    # Невелика пауза між експериментами
                    time.sleep(0.5)

    return results


def find_optimal_parameters(
    execution_type: str = 'threading',
    min_workers: int = 2,
    max_workers: int = 16,
    num_queries: int = 100
) -> Tuple[int, float]:
    """
    Знаходить оптимальну кількість workers для заданого типу виконання

    Args:
        execution_type: Тип виконання ('threading' або 'multiprocessing')
        min_workers: Мінімальна кількість workers
        max_workers: Максимальна кількість workers
        num_queries: Кількість запитів для тестування

    Returns:
        Tuple[int, float]: (оптимальна кількість workers, час виконання)
    """
    best_workers = min_workers
    best_time = float('inf')

    print(f"Пошук оптимальних параметрів для {execution_type}")

    worker_range = [2, 4, 8, 12, 16] if max_workers >= 16 else list(range(min_workers, max_workers + 1, 2))

    for workers in worker_range:
        if workers > max_workers:
            break

        print(f"Тестування з {workers} workers...")

        result = run_experiment(
            execution_type=execution_type,
            num_workers=workers,
            num_queries=num_queries,
            batch_size=10
        )

        exec_time = result.execution_time
        print(f"  Час виконання: {exec_time:.2f}s")
        print(f"  CPU: {result.cpu_usage:.1f}%, Memory: {result.memory_usage:.1f}%")

        if exec_time < best_time:
            best_time = exec_time
            best_workers = workers
            print(f"Новий оптимум!!!!")

        print()

    print(f"Оптимальні параметри:")
    print(f"  Workers: {best_workers}")
    print(f"  Час виконання: {best_time:.2f}s")

    return best_workers, best_time


def run_large_scale_test(
    execution_type: str = 'threading',
    num_workers: int = 4,
    num_queries: int = 200
) -> Dict[str, Any]:
    """
    Запускає великий тест з 100-200 запитами

    Args:
        execution_type: Тип виконання
        num_workers: Кількість workers
        num_queries: Кількість запитів (100-200)

    Returns:
        Dict з детальними результатами
    """
    print(f"Запуск великомасштабного тесту")
    print(f"Тип: {execution_type}, Workers: {num_workers}, Запитів: {num_queries}")

    result = run_experiment(
        execution_type=execution_type,
        num_workers=num_workers,
        num_queries=num_queries,
        batch_size=20
    )

    queries_per_second = num_queries / result.execution_time if result.execution_time > 0 else 0

    summary = {
        'benchmark_id': result.id,
        'execution_type': result.execution_type,
        'num_workers': result.num_workers,
        'num_queries': result.num_queries,
        'execution_time': result.execution_time,
        'queries_per_second': queries_per_second,
        'cpu_usage': result.cpu_usage,
        'memory_usage': result.memory_usage,
        'timestamp': result.timestamp
    }

    print(f"Результати:")
    print(f"  Час виконання: {result.execution_time:.2f}s")
    print(f"  Запитів за секунду: {queries_per_second:.2f}")
    print(f"  CPU: {result.cpu_usage:.1f}%")
    print(f"  Пам'ять: {result.memory_usage:.1f}%")
    print(f"{'='*60}\n")

    return summary


def generate_comparison_report() -> Dict[str, Any]:
    """
    Генерує порівняльний звіт між threading та multiprocessing
    """
    from repo_practice.models import BenchmarkResult
    from django.db.models import Avg, Min, Max, Count

    report = {}

    for exec_type in ['threading', 'multiprocessing']:
        stats = BenchmarkResult.objects.filter(execution_type=exec_type).aggregate(
            count=Count('id'),
            avg_time=Avg('execution_time'),
            min_time=Min('execution_time'),
            max_time=Max('execution_time'),
            avg_cpu=Avg('cpu_usage'),
            avg_memory=Avg('memory_usage')
        )
        report[exec_type] = stats

    return report


if __name__ == '__main__':
    print("Тестування системи бенчмаркінгу...")

    result = run_experiment(
        execution_type='threading',
        num_workers=4,
        num_queries=50,
        batch_size=10
    )
    print(f"Експеримент завершено: {result}")

