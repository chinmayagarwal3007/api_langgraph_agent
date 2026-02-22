import requests

BASE_URL = "http://localhost:8000"


class APIClient:
    def __init__(self):
        self.token = None

    def set_token(self, token: str):
        self.token = token

    def _headers(self):
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}

    # ---------------- AUTH ---------------- #

    def signup(self, username, password):
        return requests.post(
            f"{BASE_URL}/auth/signup",
            params={"username": username, "password": password},
        )

    def login(self, username, password):
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data={"username": username, "password": password},
        )
        if response.status_code == 200:
            token = response.json()["access_token"]
            self.set_token(token)
        return response

    # ---------------- CHAT ---------------- #

    def create_session(self):
        return requests.post(
            f"{BASE_URL}/chat/sessions",
            headers=self._headers(),
        )

    def get_sessions(self):
        return requests.get(
            f"{BASE_URL}/chat/sessions",
            headers=self._headers(),
        )

    def get_messages(self, session_id):
        return requests.get(
            f"{BASE_URL}/chat/sessions/{session_id}/messages",
            headers=self._headers(),
        )

    def send_message(self, session_id, content):
        return requests.post(
            f"{BASE_URL}/chat/sessions/{session_id}/messages",
            headers=self._headers(),
            params={"content": content},
        )
    
    def delete_session(self, session_id):
        return requests.delete(
            f"{BASE_URL}/chat/sessions/{session_id}",
            headers=self._headers(),
        )