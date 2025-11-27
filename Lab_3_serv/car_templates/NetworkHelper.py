import requests
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class NetworkHelper:
    """
    Helper class to interact with the REST API using requests library.
    Demonstrates working with external APIs (in this case, our own API).
    """

    def __init__(self, base_url: str = "http://127.0.0.1:8000/api/cars/",
                 username: str = None, password: str = None):
        """
        Initialize the NetworkHelper with API credentials.

        Args:
            base_url: The base URL of the API endpoint
            username: Username for Basic Authentication
            password: Password for Basic Authentication
        """
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.auth = (username, password) if username and password else None

    def get_list(self) -> List[Dict]:
        """
        Get list of all cars from the API.

        Returns:
            List of car dictionaries
        """
        try:
            url = f"{self.base_url}/"
            response = requests.get(url, auth=self.auth, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching car list: {e}")
            return []

    def get_by_id(self, car_id: int) -> Optional[Dict]:
        """
        Get a specific car by ID from the API.

        Args:
            car_id: The ID of the car to retrieve

        Returns:
            Car dictionary or None if not found
        """
        try:
            url = f"{self.base_url}/{car_id}/"
            response = requests.get(url, auth=self.auth, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching car {car_id}: {e}")
            return None

    def create_item(self, data: Dict) -> Optional[Dict]:
        """
        Create a new car via the API.

        Args:
            data: Dictionary containing car data

        Returns:
            Created car dictionary or None if failed
        """
        try:
            url = f"{self.base_url}/"
            response = requests.post(url, json=data, auth=self.auth, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating car: {e}")
            return None

    def update_item(self, car_id: int, data: Dict) -> Optional[Dict]:
        """
        Update an existing car via the API.

        Args:
            car_id: The ID of the car to update
            data: Dictionary containing updated car data

        Returns:
            Updated car dictionary or None if failed
        """
        try:
            url = f"{self.base_url}/{car_id}/"
            response = requests.put(url, json=data, auth=self.auth, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error updating car {car_id}: {e}")
            return None

    def delete_item(self, car_id: int) -> bool:
        """
        Delete a car via the API.

        Args:
            car_id: The ID of the car to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            url = f"{self.base_url}/{car_id}/"
            response = requests.delete(url, auth=self.auth, timeout=10)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Error deleting car {car_id}: {e}")
            return False

