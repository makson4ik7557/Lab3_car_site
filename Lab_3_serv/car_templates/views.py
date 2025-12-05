from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db import transaction as db_transaction
from repo_practice.services.repo_service import RepositoryService
from .forms import CarForm, CustomLoginForm
from .NetworkHelper import NetworkHelper
from decimal import Decimal


repo_service = RepositoryService()


def home(request):
    return render(request, 'car_templates/home.html')


def car_list(request):
    cars = repo_service.cars.get_all()
    context = {
        'cars': cars,
        'page_title': 'Car Inventory'
    }
    return render(request, 'car_templates/car_list.html', context)


def car_detail(request, car_id):
    car = repo_service.cars.get_by_id(car_id)
    if not car:
        messages.error(request, f'Car with ID {car_id} not found.')
        return redirect('car_list')

    context = {
        'car': car,
        'page_title': f'{car.make} {car.model}'
    }
    return render(request, 'car_templates/car_detail.html', context)


@require_http_methods(["GET", "POST"])
def car_add(request):
    if request.method == 'POST':
        form = CarForm(request.POST)
        if form.is_valid():
            car_data = form.cleaned_data
            car = repo_service.cars.create(**car_data)
            messages.success(request, f'Car "{car.make} {car.model}" added successfully!')
            return redirect('car_detail', car_id=car.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CarForm()

    context = {
        'form': form,
        'page_title': 'Add New Car',
        'action': 'Add'
    }
    return render(request, 'car_templates/car_form.html', context)


@require_http_methods(["GET", "POST"])
def car_edit(request, car_id):
    car = repo_service.cars.get_by_id(car_id)
    if not car:
        messages.error(request, f'Car with ID {car_id} not found.')
        return redirect('car_list')

    if request.method == 'POST':
        form = CarForm(request.POST, instance=car)
        if form.is_valid():
            car_data = form.cleaned_data
            updated_car = repo_service.cars.update(car_id, **car_data)
            messages.success(request, f'Car "{updated_car.make} {updated_car.model}" updated successfully!')
            return redirect('car_detail', car_id=car_id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CarForm(instance=car)

    context = {
        'form': form,
        'car': car,
        'page_title': f'Edit {car.make} {car.model}',
        'action': 'Edit'
    }
    return render(request, 'car_templates/car_form.html', context)


@require_http_methods(["POST"])
def car_delete(request, car_id):
    car = repo_service.cars.get_by_id(car_id)
    if car:
        car_info = f"{car.make} {car.model}"
        repo_service.cars.delete(car_id)
        messages.success(request, f'Car "{car_info}" deleted successfully!')
    else:
        messages.error(request, f'Car with ID {car_id} not found.')

    return redirect('car_list')


# OPTION 1: Always use a service account (default NetworkHelper credentials) for API calls.
# This simplifies development but is not secure for production. Replace with token/session auth later.

def car_api_list(request):
    network_helper = NetworkHelper()  # uses default admin credentials
    cars = network_helper.get_list()

    if not cars:
        messages.warning(request, 'No cars returned from API or API unreachable.')

    context = {
        'cars': cars,
        'page_title': 'Car Inventory (via API)',
        'using_api': True
    }
    return render(request, 'car_templates/car_api_list.html', context)


@require_http_methods(["POST"])
def car_api_delete(request, car_id):
    network_helper = NetworkHelper()  # uses default admin credentials
    success = network_helper.delete_item(car_id)

    if success:
        messages.success(request, 'Car deleted successfully via API!')
    else:
        messages.error(request, 'Failed to delete car via API (check authentication or ID).')

    return redirect('car_api_list')


# Authentication Views
def user_login(request):
    """
    Відображає форму логіну та обробляє автентифікацію користувача
    """
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = request.POST.get('remember')

            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)

                # Налаштування сесії залежно від "запам'ятати мене"
                if remember_me:
                    # Зберігати сесію на 30 днів
                    request.session.set_expiry(30 * 24 * 60 * 60)
                else:
                    # Видалити сесію при закритті браузера
                    request.session.set_expiry(0)

                messages.success(request, f'Ласкаво просимо, {user.username}!')
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
            else:
                messages.error(request, 'Неправильне ім\'я користувача або пароль.')
        else:
            messages.error(request, 'Будь ласка, виправте помилки у формі.')
    else:
        form = CustomLoginForm()

    return render(request, 'car_templates/login.html', {'form': form})


def user_logout(request):
    """
    Виходить з системи та перенаправляє на сторінку логіну
    """
    logout(request)
    messages.success(request, 'Ви успішно вийшли з системи.')
    return redirect('login')


# Dealer Views
@login_required
def dealer_dashboard(request):
    """
    Dealer dashboard showing balance and transaction history
    """
    dealer_profile, created = repo_service.dealer_profiles.get_or_create_by_user(request.user)

    # Get dealer's owned cars
    owned_cars = repo_service.cars.get(owner=request.user)

    # Get recent transactions
    transactions = repo_service.transactions.get_dealer_recent_transactions(request.user, limit=20)

    # Get available cars to buy (not owned by this dealer)
    all_available = repo_service.cars.get(in_stock=True)
    available_cars = [car for car in all_available if car.owner != request.user][:10]

    context = {
        'dealer_profile': dealer_profile,
        'owned_cars': owned_cars,
        'transactions': transactions,
        'available_cars': available_cars,
        'page_title': 'Dealer Dashboard'
    }
    return render(request, 'car_templates/dealer_dashboard.html', context)


@login_required
@require_http_methods(["POST"])
def buy_car(request, car_id):
    """
    Buy a car from the inventory
    """
    car = repo_service.cars.get_by_id(car_id)
    if not car:
        messages.error(request, f'Car with ID {car_id} not found.')
        return redirect('dealer_dashboard')

    dealer_profile, created = repo_service.dealer_profiles.get_or_create_by_user(request.user)

    # Check if car is already owned by this dealer
    if car.owner == request.user:
        messages.error(request, 'You already own this car!')
        return redirect('dealer_dashboard')

    # Check if dealer has enough balance
    if dealer_profile.balance < car.price:
        messages.error(request, f'Insufficient balance! You need ${car.price} but have ${dealer_profile.balance}')
        return redirect('dealer_dashboard')

    # Perform transaction
    with db_transaction.atomic():
        balance_before = dealer_profile.balance

        # Update balance using repository
        repo_service.dealer_profiles.deduct_from_balance(request.user, car.price)

        # Update car ownership using repository
        repo_service.cars.update(car_id, owner=request.user)

        # Record transaction using repository
        repo_service.transactions.create(
            dealer=request.user,
            car=car,
            transaction_type='BUY',
            amount=-car.price,
            description=f'Purchased {car.make} {car.model} ({car.year})',
            balance_before=balance_before,
            balance_after=dealer_profile.balance - car.price
        )

    messages.success(request, f'Successfully purchased {car.make} {car.model} for ${car.price}!')
    return redirect('dealer_dashboard')


@login_required
@require_http_methods(["GET", "POST"])
def modify_car(request, car_id):
    """
    Modify a car (costs money to upgrade)
    """
    car = repo_service.cars.get_by_id(car_id)
    if not car or car.owner != request.user:
        messages.error(request, 'Car not found or you do not own this car.')
        return redirect('dealer_dashboard')

    dealer_profile, created = repo_service.dealer_profiles.get_or_create_by_user(request.user)

    if request.method == 'POST':
        modification_cost = Decimal(request.POST.get('modification_cost', 0))
        price_increase = Decimal(request.POST.get('price_increase', 0))
        modification_desc = request.POST.get('modification_description', 'Car modification')

        if modification_cost <= 0 or price_increase <= 0:
            messages.error(request, 'Invalid modification cost or price increase!')
            return redirect('modify_car', car_id=car_id)

        # Check if dealer has enough balance
        if dealer_profile.balance < modification_cost:
            messages.error(request, f'Insufficient balance! Modification costs ${modification_cost} but you have ${dealer_profile.balance}')
            return redirect('modify_car', car_id=car_id)

        # Perform transaction
        with db_transaction.atomic():
            balance_before = dealer_profile.balance

            # Update balance using repository
            repo_service.dealer_profiles.deduct_from_balance(request.user, modification_cost)

            # Update car price using repository
            old_price = car.price
            new_price = car.price + price_increase
            repo_service.cars.update(car_id, price=new_price)

            # Record transaction using repository
            repo_service.transactions.create(
                dealer=request.user,
                car=car,
                transaction_type='MODIFY',
                amount=-modification_cost,
                description=f'{modification_desc} - Price increased from ${old_price} to ${new_price}',
                balance_before=balance_before,
                balance_after=dealer_profile.balance - modification_cost
            )

        messages.success(request, f'Successfully modified {car.make} {car.model}! Price increased to ${new_price}')
        return redirect('dealer_dashboard')

    context = {
        'car': car,
        'dealer_profile': dealer_profile,
        'page_title': f'Modify {car.make} {car.model}'
    }
    return render(request, 'car_templates/modify_car.html', context)


@login_required
@require_http_methods(["POST"])
def sell_car(request, car_id):
    """
    Sell a car owned by the dealer
    """
    car = repo_service.cars.get_by_id(car_id)
    if not car or car.owner != request.user:
        messages.error(request, 'Car not found or you do not own this car.')
        return redirect('dealer_dashboard')

    dealer_profile, created = repo_service.dealer_profiles.get_or_create_by_user(request.user)

    # Perform transaction
    with db_transaction.atomic():
        balance_before = dealer_profile.balance

        # Update balance using repository
        repo_service.dealer_profiles.add_to_balance(request.user, car.price)

        # Record transaction before removing ownership
        repo_service.transactions.create(
            dealer=request.user,
            car=car,
            transaction_type='SELL',
            amount=car.price,
            description=f'Sold {car.make} {car.model} ({car.year})',
            balance_before=balance_before,
            balance_after=dealer_profile.balance + car.price
        )

        # Remove ownership using repository
        repo_service.cars.update(car_id, owner=None)

    messages.success(request, f'Successfully sold {car.make} {car.model} for ${car.price}!')
    return redirect('dealer_dashboard')


@login_required
def transaction_history(request):
    """
    View full transaction history
    """
    transactions = repo_service.transactions.get_by_dealer(request.user)
    dealer_profile, created = repo_service.dealer_profiles.get_or_create_by_user(request.user)

    context = {
        'transactions': transactions,
        'dealer_profile': dealer_profile,
        'page_title': 'Transaction History'
    }
    return render(request, 'car_templates/transaction_history.html', context)


# Custom Error Handlers
def custom_404(request, exception=None):
    """
    Custom 404 error page handler
    """
    return render(request, 'car_templates/404.html', status=404)

