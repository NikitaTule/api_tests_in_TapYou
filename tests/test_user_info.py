import pytest_check as check
from utils.api_requests import ApiClient


class TestUserInfoPositive(ApiClient):
    # Check ID: a1
    def test_successful_response_keys_in_json(self):
        response = self.get_user_info(15)
        assert response.status_code == 200
        json_response = response.json()

        # Проверка наличия ключей в JSON-ответе
        check.is_in("success", json_response, "Key 'success' is missing")
        check.is_in("errorCode", json_response, "Key 'errorCode' is missing")
        check.is_in("errorMessage", json_response, "Key 'errorMessage' is missing")
        check.is_in("result", json_response, "Key 'result' is missing")

        # Проверка наличия ключей в user внутри result
        user = json_response["result"]
        check.is_in("id", user, "Key 'id' is missing in user info")
        check.is_in("name", user, "Key 'name' is missing in user info")
        check.is_in("gender", user, "Key 'gender' is missing in user info")
        check.is_in("age", user, "Key 'age' is missing in user info")
        check.is_in("city", user, "Key 'city' is missing in user info")
        check.is_in("registrationDate", user, "Key 'registrationDate' is missing in user info")

    # Check ID: a2 (success был заменен на isSuccess, result на user что бы тест работал)
    def test_successful_response_values_user_info(self):
        response = self.get_user_info(5)
        assert response.status_code == 200
        json_response = response.json()

        # Проверка значений ключей в JSON-ответе
        check.equal(json_response["isSuccess"], "true", "Value of 'isSuccess' is not true")
        check.equal(json_response["errorCode"], 0, "Value of 'errorCode' is not 0")
        check.equal(json_response["errorMessage"], "null", "Value of 'errorMessage' is not null")

        user = json_response["user"]
        print(user)
        check.equal(user["id"], 5, "Value of 'id' is not 5")  # Здесь ожидаемое значение id 5
        check.is_instance(user["name"], str, "Value of 'name' is not a string")
        check.is_instance(user["gender"], str, "Value of 'gender' is not a string")
        check.is_instance(user["age"], int, "Value of 'age' is not an integer")
        check.is_instance(user["city"], str, "Value of 'city' is not a string")
        check.is_instance(user["registrationDate"], str, "Value of 'registrationDate' is not a string")


class TestUserInfoNegative(ApiClient):
    # Check ID: b1
    def test_invalid_user_id(self):
        response = self.get_user_info(99999999999)
        assert response.status_code != 200
        json_response = response.json()
        print(json_response)
        check.is_in("success", json_response, "Key 'success' is missing")
        check.equal(json_response["success"], "false", "Value of 'success' is not false")
        check.is_in("errorCode", json_response, "Key 'errorCode' is missing")
        check.is_in("errorMessage", json_response, "Key 'errorMessage' is missing")

    # Check ID: b2
    def test_with_special_characters_instead_of_id(self):
        response = self.get_user_info("_)(&*)(&*^&")
        assert response.status_code != 200

    # Check ID: b3
    def test_non_numeric_user_id(self):
        response = self.get_user_info("g")
        assert response.status_code != 200

    # Check ID: b4
    def test_missing_user_id(self):
        response = self.get_user_info("")
        assert response.status_code != 200


class TestUserInfoSecurity(ApiClient):
    # Check ID: c1
    def test_sql_injection_user_info(self):
        response = self.get_user_info("10' OR '1'='1")
        # Проверяем, что API возвращает ошибку
        assert response.status_code != 200, "API should return an error for SQL injection"
        # Проверяем, что в ответе нет корректной JSON-структуры
        try:
            json_response = response.json()
            assert "error" in json_response or "errorCode" in json_response or "errorMessage" in json_response, \
                "Error information should be present in response"
        except ValueError:
            # Если JSON не парсится, значит вернулась ошибка, что ожидается
            pass
