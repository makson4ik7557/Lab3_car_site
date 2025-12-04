"""
Script to create a dealer user for testing
"""
import os
import django

# Configure Django settings first
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Lab_3_serv.settings')
django.setup()

from django.contrib.auth.models import User
from repo_practice.models import DealerProfile

def create_dealer():
    # Create or get dealer user
    username = 'dealer'
    password = 'dealer123'

    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': 'dealer@autohub.com',
            'is_staff': False,
            'is_superuser': False
        }
    )

    if created:
        user.set_password(password)
        user.save()
        print(f"Created new user: {username}")
    else:
        print(f"User {username} already exists")

    # Create or get dealer profile with initial balance
    dealer_profile, profile_created = DealerProfile.objects.get_or_create(
        user=user,
        defaults={'balance': 10000.00}
    )

    if profile_created:
        print(f"Created dealer profile with balance: ${dealer_profile.balance}")
    else:
        print(f"Dealer profile exists with balance: ${dealer_profile.balance}")

    print(f"\nLogin credentials:")
    print(f"Username: {username}")
    print(f"Password: {password}")
    print(f"\nYou can now log in and access the dealer dashboard!")

if __name__ == '__main__':

    create_dealer()

