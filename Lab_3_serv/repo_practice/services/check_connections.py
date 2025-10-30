import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Lab_3_serv.settings')
django.setup()

try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        print("✅ Підключення до MySQL успішне!")
        print(f"Результат тестового запиту: {result}")

        # Перевірка бази даних
        cursor.execute("SELECT DATABASE()")
        db_name = cursor.fetchone()
        print(f"Поточна база даних: {db_name[0]}")

except Exception as e:
    print(f"❌ Помилка підключення: {e}")