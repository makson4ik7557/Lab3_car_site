from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .forms import CarForm, CustomLoginForm
from .NetworkHelper import NetworkHelper
from decimal import Decimal




def home(request):
    return render(request, 'car_templates/home.html')


def car_list(request):
    api = NetworkHelper()
    cars = api.get_list()
    context = {
        'cars': cars,
        'page_title': 'Car Inventory'
    }
    return render(request, 'car_templates/car_list.html', context)


def car_detail(request, car_id):
    api = NetworkHelper()
    car = api.get_by_id(car_id)
    if not car:
        messages.error(request, f'Car with ID {car_id} not found.')
        return redirect('car_list')

    context = {
        'car': car,
        'page_title': f"{car['make']} {car['model']}"
    }
    return render(request, 'car_templates/car_detail.html', context)


@require_http_methods(["GET", "POST"])
def car_add(request):
    if request.method == 'POST':
        form = CarForm(request.POST)
        if form.is_valid():
            api = NetworkHelper()
            car_data = form.cleaned_data
            # Конвертуємо Django об'єкти в dict для API
            car_dict = {
                'make': str(car_data['make']),
                'model': str(car_data['model']),
                'year': int(car_data['year']),
                'price': str(car_data['price']),
                'in_stock': bool(car_data.get('in_stock', True))
            }
            car = api.create_item(car_dict)
            if car:
                messages.success(request, f'Car "{car["make"]} {car["model"]}" added successfully!')
                return redirect('car_detail', car_id=car['id'])
            else:
                messages.error(request, 'Failed to add car via API.')
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
    api = NetworkHelper()
    car = api.get_by_id(car_id)
    if not car:
        messages.error(request, f'Car with ID {car_id} not found.')
        return redirect('car_list')

    if request.method == 'POST':
        form = CarForm(request.POST)
        if form.is_valid():
            car_data = form.cleaned_data
            # Конвертуємо в dict для API
            car_dict = {
                'make': str(car_data['make']),
                'model': str(car_data['model']),
                'year': int(car_data['year']),
                'price': str(car_data['price']),
                'in_stock': bool(car_data.get('in_stock', True)),
                'owner': car.get('owner')  # Зберігаємо власника
            }
            updated_car = api.update_item(car_id, car_dict)
            if updated_car:
                messages.success(request, f'Car "{updated_car["make"]} {updated_car["model"]}" updated successfully!')
                return redirect('car_detail', car_id=car_id)
            else:
                messages.error(request, 'Failed to update car via API.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Створюємо форму з початковими даними з API
        form = CarForm(initial=car)

    context = {
        'form': form,
        'car': car,
        'page_title': f'Edit {car["make"]} {car["model"]}',
        'action': 'Edit'
    }
    return render(request, 'car_templates/car_form.html', context)


@require_http_methods(["POST"])
def car_delete(request, car_id):
    api = NetworkHelper()
    car = api.get_by_id(car_id)
    if car:
        car_info = f"{car['make']} {car['model']}"
        success = api.delete_item(car_id)
        if success:
            messages.success(request, f'Car "{car_info}" deleted successfully!')
        else:
            messages.error(request, f'Failed to delete car via API.')
    else:
        messages.error(request, f'Car with ID {car_id} not found.')

    return redirect('car_list')


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
    Dealer dashboard через API
    """
    api = NetworkHelper()
    data = api.get_dealer_dashboard(request.user.id)

    if not data:
        messages.error(request, 'Failed to load dashboard')
        return redirect('home')

    context = {
        'dealer_profile': data.get('dealer_profile'),
        'owned_cars': data.get('owned_cars', []),
        'transactions': data.get('transactions', []),
        'available_cars': data.get('available_cars', []),
        'page_title': 'Dealer Dashboard'
    }
    return render(request, 'car_templates/dealer_dashboard.html', context)



@login_required
@require_http_methods(["POST"])
def buy_car(request, car_id):
    """
    Buy car через API
    """
    api = NetworkHelper()
    result = api.buy_car_api(request.user.id, car_id)

    if result and 'message' in result:
        messages.success(request, result['message'])
    elif result and 'error' in result:
        messages.error(request, result['error'])
    else:
        messages.error(request, 'Failed to buy car')

    return redirect('dealer_dashboard')


@login_required
@require_http_methods(["GET", "POST"])
def modify_car(request, car_id):
    """
    Modify car через API
    """
    if request.method == 'POST':
        modification_cost = Decimal(request.POST.get('modification_cost', 0))
        price_increase = Decimal(request.POST.get('price_increase', 0))
        description = request.POST.get('modification_description', 'Car modification')

        if modification_cost <= 0 or price_increase <= 0:
            messages.error(request, 'Invalid modification cost or price increase!')
            return redirect('modify_car', car_id=car_id)

        api = NetworkHelper()
        result = api.modify_car_api(request.user.id, car_id, float(modification_cost), float(price_increase), description)

        if result and 'message' in result:
            messages.success(request, result['message'])
            return redirect('dealer_dashboard')
        elif result and 'error' in result:
            messages.error(request, result['error'])
        else:
            messages.error(request, 'Failed to modify car')

    # GET - показуємо форму
    api = NetworkHelper()
    car = api.get_by_id(car_id)
    dashboard_data = api.get_dealer_dashboard(request.user.id)

    if not car or car.get('owner') != request.user.id:
        messages.error(request, 'Car not found or you do not own this car.')
        return redirect('dealer_dashboard')

    context = {
        'car': car,
        'dealer_profile': dashboard_data.get('dealer_profile') if dashboard_data else None,
        'page_title': f'Modify {car["make"]} {car["model"]}'
    }
    return render(request, 'car_templates/modify_car.html', context)


@login_required
@require_http_methods(["POST"])
def sell_car(request, car_id):
    """
    Sell car через API
    """
    api = NetworkHelper()
    result = api.sell_car_api(request.user.id, car_id)

    if result and 'message' in result:
        messages.success(request, result['message'])
    elif result and 'error' in result:
        messages.error(request, result['error'])
    else:
        messages.error(request, 'Failed to sell car')

    return redirect('dealer_dashboard')


@login_required
def transaction_history(request):
    """
    Transaction history через API
    """
    api = NetworkHelper()
    data = api.get_dealer_transactions(request.user.id)
    dashboard_data = api.get_dealer_dashboard(request.user.id)

    context = {
        'transactions': data.get('transactions', []) if data else [],
        'dealer_profile': dashboard_data.get('dealer_profile') if dashboard_data else None,
        'page_title': 'Transaction History'
    }
    return render(request, 'car_templates/transaction_history.html', context)


# Custom Error Handlers
def custom_404(request, exception=None):
    """
    Custom 404 error page handler
    """
    return render(request, 'car_templates/404.html', status=404)

