from ..repositories.car_repo import CarRepository
from ..repositories.customer_repo import CustomerRepository
from ..repositories.employee_repo import EmployeeRepository
from ..repositories.sale_repo import SaleRepository


class RepositoryService:
    def __init__(self):
        self.car_repository = CarRepository()
        self.customer_repository = CustomerRepository()
        self.employee_repository = EmployeeRepository()
        self.sale_repository = SaleRepository()

    # Car methods
    def get_all_cars(self):
        return self.car_repository.get_all()

    def get_car_by_id(self, car_id):
        return self.car_repository.get_by_id(car_id)

    def create_car(self, **kwargs):
        return self.car_repository.create(**kwargs)

    def get_available_cars(self):
        return self.car_repository.get_available_cars()

    def get_cars_by_make(self, make):
        return self.car_repository.get_cars_by_make(make)

    def get_premium_cars(self, min_price=80000):
        return self.car_repository.get_premium_cars(min_price)

    def get_cars_by_year_range(self, start_year, end_year):
        return self.car_repository.get_cars_by_year_range(start_year, end_year)

    def get_most_expensive_car(self):
        return self.car_repository.get_most_expensive()

    def get_cheapest_car(self):
        return self.car_repository.get_cheapest()

    # Customer methods
    def get_all_customers(self):
        return self.customer_repository.get_all()

    def get_customer_by_id(self, customer_id):
        return self.customer_repository.get_by_id(customer_id)

    def create_customer(self, **kwargs):
        return self.customer_repository.create(**kwargs)

    def get_customer_by_email(self, email):
        return self.customer_repository.get_by_email(email)

    # Employee methods
    def get_all_employees(self):
        return self.employee_repository.get_all()

    def get_employee_by_id(self, employee_id):
        return self.employee_repository.get_by_id(employee_id)

    def create_employee(self, **kwargs):
        return self.employee_repository.create(**kwargs)

    def get_employees_by_position(self, position):
        return self.employee_repository.get_by_position(position)

    # Sale methods
    def get_all_sales(self):
        return self.sale_repository.get_all()

    def get_sale_by_id(self, sale_id):
        return self.sale_repository.get_by_id(sale_id)

    def create_sale(self, **kwargs):
        return self.sale_repository.create(**kwargs)

    def get_sales_by_customer(self, customer_id):
        return self.sale_repository.get_sales_by_customer(customer_id)


# Глобальний екземпляр для використання
repository_service = RepositoryService()