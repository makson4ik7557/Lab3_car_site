import requests
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class NetworkHelper:
    def __init__(self, base_url: str = "http://127.0.0.1:8000/api/cars/",
                 username: str = "admin", password: str = "gigachad123"):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.auth = (username, password) if username and password else None

    def get_list(self) -> List[Dict]:
        try:
            url = f"{self.base_url}/"
            response = requests.get(url, auth=self.auth, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching car list: {e}")
            return []

    def get_by_id(self, car_id: int) -> Optional[Dict]:
        try:
            url = f"{self.base_url}/{car_id}/"
            response = requests.get(url, auth=self.auth, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching car {car_id}: {e}")
            return None

    def create_item(self, data: Dict) -> Optional[Dict]:
        try:
            url = f"{self.base_url}/"
            response = requests.post(url, json=data, auth=self.auth, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating car: {e}")
            return None

    def update_item(self, car_id: int, data: Dict) -> Optional[Dict]:
        try:
            url = f"{self.base_url}/{car_id}/"
            response = requests.put(url, json=data, auth=self.auth, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error updating car {car_id}: {e}")
            return None

    def delete_item(self, car_id: int) -> bool:
        try:
            url = f"{self.base_url}/{car_id}/"
            response = requests.delete(url, auth=self.auth, timeout=10)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Error deleting car {car_id}: {e}")
            return False

    def create_transaction(self, data: Dict) -> Optional[Dict]:
        try:
            url = "http://127.0.0.1:8000/api/transactions/"
            response = requests.post(url, json=data, auth=self.auth, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating transaction: {e}")
            return None

    def get_dealer_profiles(self) -> List[Dict]:
        try:
            url = "http://127.0.0.1:8000/api/dealer-profiles/"
            response = requests.get(url, auth=self.auth, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching dealer profiles: {e}")
            return []

    def get_dealer_profile(self, profile_id: int) -> Optional[Dict]:
        try:
            url = f"http://127.0.0.1:8000/api/dealer-profiles/{profile_id}/"
            response = requests.get(url, auth=self.auth, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching dealer profile {profile_id}: {e}")
            return None

    def update_dealer_profile(self, profile_id: int, data: Dict) -> Optional[Dict]:
        try:
            url = f"http://127.0.0.1:8000/api/dealer-profiles/{profile_id}/"
            response = requests.put(url, json=data, auth=self.auth, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error updating dealer profile {profile_id}: {e}")
            return None

    def get_transactions(self) -> List[Dict]:
        try:
            url = "http://127.0.0.1:8000/api/transactions/"
            response = requests.get(url, auth=self.auth, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching transactions: {e}")
            return []

    # ============== DEALER OPERATIONS ==============

    def get_dealer_dashboard(self, user_id: int) -> Optional[Dict]:
        """GET /api/dealer/dashboard/{user_id}/"""
        try:
            url = f"http://127.0.0.1:8000/api/dealer/dashboard/{user_id}/"
            response = requests.get(url, auth=self.auth, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching dealer dashboard for user {user_id}: {e}")
            return None

    def buy_car_api(self, user_id: int, car_id: int) -> Optional[Dict]:
        """POST /api/dealer/buy/"""
        try:
            url = "http://127.0.0.1:8000/api/dealer/buy/"
            data = {'user_id': user_id, 'car_id': car_id}
            response = requests.post(url, json=data, auth=self.auth, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error buying car {car_id} for user {user_id}: {e}")
            if hasattr(e.response, 'json'):
                try:
                    return e.response.json()
                except:
                    pass
            return None

    def sell_car_api(self, user_id: int, car_id: int) -> Optional[Dict]:
        """POST /api/dealer/sell/"""
        try:
            url = "http://127.0.0.1:8000/api/dealer/sell/"
            data = {'user_id': user_id, 'car_id': car_id}
            response = requests.post(url, json=data, auth=self.auth, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error selling car {car_id} for user {user_id}: {e}")
            if hasattr(e.response, 'json'):
                try:
                    return e.response.json()
                except:
                    pass
            return None

    def modify_car_api(self, user_id: int, car_id: int, modification_cost: float, price_increase: float, description: str) -> Optional[Dict]:
        """POST /api/dealer/modify/"""
        try:
            url = "http://127.0.0.1:8000/api/dealer/modify/"
            data = {
                'user_id': user_id,
                'car_id': car_id,
                'modification_cost': str(modification_cost),
                'price_increase': str(price_increase),
                'description': description
            }
            response = requests.post(url, json=data, auth=self.auth, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error modifying car {car_id} for user {user_id}: {e}")
            if hasattr(e.response, 'json'):
                try:
                    return e.response.json()
                except:
                    pass
            return None

    def get_dealer_transactions(self, user_id: int) -> Optional[Dict]:
        """GET /api/dealer/transactions/{user_id}/"""
        try:
            url = f"http://127.0.0.1:8000/api/dealer/transactions/{user_id}/"
            response = requests.get(url, auth=self.auth, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching dealer transactions for user {user_id}: {e}")
            return None
