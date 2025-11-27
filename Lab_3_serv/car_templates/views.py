from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from repo_practice.services.repo_service import RepositoryService
from .forms import CarForm
from .NetworkHelper import NetworkHelper


# Initialize repository service
repo_service = RepositoryService()


def home(request):
    """Home page with navigation links"""
    return render(request, 'car_templates/home.html')


# ========== TEMPLATE-BASED VIEWS (Using Repository Pattern) ==========

def car_list(request):
    """
    Display list of all cars with links to detail pages.
    Uses repository pattern to fetch data directly from DB.
    """
    cars = repo_service.cars.get_all()
    context = {
        'cars': cars,
        'page_title': 'Car Inventory'
    }
    return render(request, 'car_templates/car_list.html', context)


def car_detail(request, car_id):
    """
    Display details of a specific car with delete option.

    Args:
        car_id: ID of the car to display
    """
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
    """
    Add a new car using Django forms.
    GET: Display empty form
    POST: Process form and create new car
    """
    if request.method == 'POST':
        form = CarForm(request.POST)
        if form.is_valid():
            # Use repository to create the car
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
    """
    Edit an existing car using Django forms.
    GET: Display form with current car data
    POST: Process form and update car

    Args:
        car_id: ID of the car to edit
    """
    car = repo_service.cars.get_by_id(car_id)
    if not car:
        messages.error(request, f'Car with ID {car_id} not found.')
        return redirect('car_list')

    if request.method == 'POST':
        form = CarForm(request.POST, instance=car)
        if form.is_valid():
            # Use repository to update the car
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
    """
    Delete a car by ID.
    Only accepts POST requests for safety.

    Args:
        car_id: ID of the car to delete
    """
    car = repo_service.cars.get_by_id(car_id)
    if car:
        car_info = f"{car.make} {car.model}"
        repo_service.cars.delete(car_id)
        messages.success(request, f'Car "{car_info}" deleted successfully!')
    else:
        messages.error(request, f'Car with ID {car_id} not found.')

    return redirect('car_list')


# ========== API-BASED VIEWS (Using REST API with requests library) ==========

def car_api_list(request):
    """
    Display list of cars fetched from REST API.
    Each car has a delete button that also uses the API.
    Demonstrates working with external APIs using requests library.
    """
    # Get credentials from session or use defaults
    # In production, you'd want to use proper authentication
    username = request.user.username if request.user.is_authenticated else None
    password = None  # You'd need to handle this properly in production

    # For demo purposes, you might want to hardcode credentials or pass them differently
    # This is just to demonstrate the NetworkHelper usage
    network_helper = NetworkHelper(username=username, password=password)

    # If user is not authenticated, try without auth (will fail if API requires auth)
    if not request.user.is_authenticated:
        # For demo, we'll create a helper without auth
        network_helper = NetworkHelper()

    cars = network_helper.get_list()

    context = {
        'cars': cars,
        'page_title': 'Car Inventory (via API)',
        'using_api': True
    }
    return render(request, 'car_templates/car_api_list.html', context)


@require_http_methods(["POST"])
def car_api_delete(request, car_id):
    """
    Delete a car via REST API.
    Uses NetworkHelper to make DELETE request to API.

    Args:
        car_id: ID of the car to delete
    """
    username = request.user.username if request.user.is_authenticated else None
    network_helper = NetworkHelper(username=username, password=None)

    success = network_helper.delete_item(car_id)

    if success:
        messages.success(request, f'Car deleted successfully via API!')
    else:
        messages.error(request, f'Failed to delete car via API. Make sure you are authenticated.')

    return redirect('car_api_list')

