import requests


class ApiClient:
    BASE_URL_USERS = "https://hr-challenge.dev.tapyou.com/api/test/users"
    BASE_URL_USER_INFO = "https://hr-challenge.dev.tapyou.com/api/test/user"

    def get_users_by_gender(self, gender):
        url = f"{self.BASE_URL_USERS}?gender={gender}"
        response = requests.get(url)
        return response

    def get_users_without_gender(self):
        url = self.BASE_URL_USERS
        response = requests.get(url)
        return response

    def get_user_info(self, user_id):
        url = f"{self.BASE_URL_USER_INFO}/{user_id}"
        response = requests.get(url)
        return response
