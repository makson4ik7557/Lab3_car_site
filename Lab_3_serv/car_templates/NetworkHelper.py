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

