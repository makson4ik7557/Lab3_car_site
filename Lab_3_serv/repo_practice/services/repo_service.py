from ..repositories.car_repo import CarRepository
from ..repositories.customer_repo import CustomerRepository
from ..repositories.employee_repo import EmployeeRepository
from ..repositories.sale_repo import SaleRepository
from ..repositories.dealer_profile_repo import DealerProfileRepository
from ..repositories.transaction_repo import TransactionRepository


class RepositoryService:
    def __init__(self):
        self.cars = CarRepository()
        self.customers = CustomerRepository()
        self.employees = EmployeeRepository()
        self.sales = SaleRepository()
        self.dealer_profiles = DealerProfileRepository()
        self.transactions = TransactionRepository()

# Глобальний екземпляр для використання
repository_service = RepositoryService()