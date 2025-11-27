from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from repo_practice.services.repo_service import RepositoryService
from .forms import CarForm
from .NetworkHelper import NetworkHelper


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
