import requests
from requests.exceptions import RequestException

# TODO: ask nicolai for api key
class ServerAPIService:
    BASE_URL = "https://api.policeroleplay.community/v1"

    def __init__(self):
        self.api_key = "" # uhhhh, i dont have that
        self.headers = {
            "server-key": self.api_key,
            "Accept": "*/*"
        }

    def get_server_data(self):
        try:
            response = requests.get(f"{self.BASE_URL}/server", headers=self.headers)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            print(f"An error occurred: {e}")
            return None
        
    def get_queue(self):
        try:
            response = requests.get(f"{self.BASE_URL}/server/queue", headers=self.headers)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            print(f"An error occurred: {e}")
            return None
        
if __name__ == "__main__":
        service = ServerAPIService()
        server_data = service.get_server_data()
        queue_data = service.get_queue()
        print("Server Data:", server_data)
        print("Queue Data:", queue_data[0])

