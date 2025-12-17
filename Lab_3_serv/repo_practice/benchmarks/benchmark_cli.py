"""
Утиліта для запуску експериментів та пошуку оптимальних параметрів
Можна запускати як окремий скрипт
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Lab_3_serv.settings')
django.setup()

from repo_practice.benchmarks.run_benchmarks import (
    run_experiment,
    run_multiple_experiments,
    find_optimal_parameters,
    run_large_scale_test,
    generate_comparison_report
)


def main():

    while True:
        print("\nОберіть опцію:")
        print("1. Запустити один експеримент")
        print("2. Запустити серію експериментів (Grid Search)")
        print("3. Знайти оптимальні параметри для threading")
        print("4. Знайти оптимальні параметри для multiprocessing")
        print("5. Запустити великий тест (100-200 запитів)")
        print("6. Порівняльний звіт threading vs multiprocessing")
        print("7. Створити повний набір тестів для dashboard")
        print("0. Вийти")

        choice = input("\nВаш вибір: ").strip()

        if choice == '0':
            print("\nДо побачення!")
            break

        elif choice == '1':
            # Один експеримент
            exec_type = input("Тип виконання (threading/multiprocessing) [threading]: ").strip() or 'threading'
            workers = int(input("Кількість workers [4]: ").strip() or '4')
            queries = int(input("Кількість запитів [100]: ").strip() or '100')
            batch = int(input("Розмір пакету [10]: ").strip() or '10')

            print("\nЗапуск експерименту...")
            result = run_experiment(exec_type, workers, queries, batch)
            print(f"\n✓ Завершено!")
            print(f"  ID: {result.id}")
            print(f"  Час виконання: {result.execution_time:.2f}s")
            print(f"  CPU: {result.cpu_usage:.1f}%")
            print(f"  Пам'ять: {result.memory_usage:.1f}%")

        elif choice == '2':
            # Серія експериментів
            print("\nЗапуск серії експериментів...")
            results = run_multiple_experiments(
                execution_types=['threading', 'multiprocessing'],
                worker_counts=[2, 4, 8, 16],
                query_counts=[100],
                batch_sizes=[10, 20]
            )
            print(f"\nЗавершено! Виконано {len(results)} експериментів")

        elif choice == '3':
            # Оптимальні параметри для threading
            queries = int(input("Кількість запитів для тесту [100]: ").strip() or '100')
            best_workers, best_time = find_optimal_parameters(
                execution_type='threading',
                min_workers=2,
                max_workers=16,
                num_queries=queries
            )

        elif choice == '4':
            # Оптимальні параметри для multiprocessing
            queries = int(input("Кількість запитів для тесту [100]: ").strip() or '100')
            best_workers, best_time = find_optimal_parameters(
                execution_type='multiprocessing',
                min_workers=2,
                max_workers=16,
                num_queries=queries
            )

        elif choice == '5':
            # Великий тест
            exec_type = input("Тип виконання (threading/multiprocessing) [threading]: ").strip() or 'threading'
            workers = int(input("Кількість workers [8]: ").strip() or '8')
            queries = int(input("Кількість запитів (100-200) [150]: ").strip() or '150')

            summary = run_large_scale_test(exec_type, workers, queries)

        elif choice == '6':
            # Порівняльний звіт
            print("\nГенерація порівняльного звіту...")
            report = generate_comparison_report()

            for exec_type, stats in report.items():
                print(f"{exec_type.upper()}:")
                print(f"  Кількість тестів: {stats['count']}")
                if stats['avg_time']:
                    print(f"  Середній час: {stats['avg_time']:.2f}s")
                    print(f"  Мінімальний час: {stats['min_time']:.2f}s")
                    print(f"  Максимальний час: {stats['max_time']:.2f}s")
                if stats['avg_cpu']:
                    print(f"  Середній CPU: {stats['avg_cpu']:.1f}%")
                if stats['avg_memory']:
                    print(f"  Середня пам'ять: {stats['avg_memory']:.1f}%")
                print()

        elif choice == '7':
            # Створити повний набір для dashboard
            print("\nСтворення повного набору тестів для dashboard...")
            print("Це може зайняти кілька хвилин...\n")

            # Threading з різними параметрами
            print("Тестування Threading...")
            threading_results = run_multiple_experiments(
                execution_types=['threading'],
                worker_counts=[2, 4, 6, 8, 12, 16],
                query_counts=[100, 150],
                batch_sizes=[10, 20, 50]
            )

            # Multiprocessing з різними параметрами
            print("\nТестування Multiprocessing...")
            mp_results = run_multiple_experiments(
                execution_types=['multiprocessing'],
                worker_counts=[2, 4, 6, 8],
                query_counts=[100, 150],
                batch_sizes=[10, 20, 50]
            )

            total = len(threading_results) + len(mp_results)
            print(f"\n✓ Створено {total} експериментів для dashboard!")
            print("Тепер відкрийте dashboard за адресою: /repo/benchmark/")

        else:
            print("\nНевірний вибір. Спробуйте ще раз.")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nПереривано користувачем. До побачення!")
    except Exception as e:
        print(f"\nПомилка: {e}")
        import traceback
        traceback.print_exc()

