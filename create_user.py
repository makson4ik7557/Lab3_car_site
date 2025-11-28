#!/usr/bin/env python
"""
Скрипт для створення суперкористувача для тестування логін системи
"""
import os
import sys
import django

# Додати шлях до проєкту
sys.path.append(os.path.join(os.path.dirname(__file__), 'Lab_3_serv'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Lab_3_serv.settings')

# Налаштувати Django
django.setup()

from django.contrib.auth.models import User

def create_test_user():
    """Створити тестового користувача для логіну"""
    username = 'admin'
    email = 'admin@example.com'
    password = 'gigachad123'

    try:
        # Перевірити, чи користувач вже існує
        if User.objects.filter(username=username).exists():
            print(f"Користувач '{username}' вже існує!")
            user = User.objects.get(username=username)
            print(f"   ID: {user.id}")
            print(f"   Email: {user.email}")
            print(f"   Суперкористувач: {'Так' if user.is_superuser else 'Ні'}")
        else:
            # Створити нового суперкористувача
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            print(f"🎉 Суперкористувача '{username}' успішно створено!")
            print(f"   Email: {email}")
            print(f"   Пароль: {password}")

        print("\n📋 Дані для входу:")
        print(f"   🔗 URL: http://127.0.0.1:8000/login/")
        print(f"   👤 Логін: {username}")
        print(f"   🔑 Пароль: {password}")

    except Exception as e:
        print(f"❌ Помилка при створенні користувача: {e}")
        return False

    return True

if __name__ == '__main__':
    print("🚀 Створення тестового користувача для AutoHub...")
    print("-" * 50)

    success = create_test_user()

    if success:
        print("\n✅ Готово! Тепер ти можеш увійти в систему.")
        print("\n🖥️  Для запуску сервера виконай:")
        print("   cd Lab_3_serv")
        print("   python manage.py runserver")
    else:
        print("\n❌ Щось пішло не так. Перевір налаштування бази даних.")
