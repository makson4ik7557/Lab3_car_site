import os
import django
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Lab_3_serv.settings')
django.setup()


def execute_query_in_process():
    import os
    import django

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Lab_3_serv.settings')
    django.setup()

    from repo_practice.benchmarks.test_queries import execute_random_query
    from django.db import connection

    try:
        result = execute_random_query()
        connection.close()
        return True, len(result) if result else 0
    except Exception as e:
        connection.close()
        return False, str(e)


def run_multiprocessing_benchmark(num_workers=4, num_queries=100):
    start_time = time.time()

    successful_queries = 0
    failed_queries = 0

    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(execute_query_in_process) for _ in range(num_queries)]

        for future in as_completed(futures):
            success, result = future.result()
            if success:
                successful_queries += 1
            else:
                failed_queries += 1

    end_time = time.time()
    execution_time = end_time - start_time

    return {
        'execution_type': 'multiprocessing',
        'num_workers': num_workers,
        'num_queries': num_queries,
        'execution_time': execution_time,
        'successful_queries': successful_queries,
        'failed_queries': failed_queries,
        'queries_per_second': num_queries / execution_time if execution_time > 0 else 0
    }


if __name__ == '__main__':
    result = run_multiprocessing_benchmark(num_workers=4, num_queries=50)
    print(f"Multiprocessing test completed:")
    print(f"Workers: {result['num_workers']}")
    print(f"Queries: {result['num_queries']}")
    print(f"Time: {result['execution_time']:.2f}s")
    print(f"Successful: {result['successful_queries']}")
    print(f"Failed: {result['failed_queries']}")
    print(f"QPS: {result['queries_per_second']:.2f}")

