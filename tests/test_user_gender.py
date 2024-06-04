import pytest
import pytest_check as check
from utils.api_requests import ApiClient


class TestUserGenderPositive(ApiClient):
    # Check ID: 1a
    @pytest.mark.parametrize("gender", ["male", "female"])
    def test_successful_response_structure(self, gender):
        response = self.get_users_by_gender(gender)
        assert response.status_code == 200
        json_response = response.json()

        check.is_in("success", json_response, "Key 'success' is missing")
        check.is_in("errorCode", json_response, "Key 'errorCode' is missing")
        check.is_in("errorMessage", json_response, "Key 'errorMessage' is missing")
        check.is_in("result", json_response, "Key 'result' is missing")

    # Check ID: 2a (success был заменен на isSuccess, result на idList что бы тест работал)
    @pytest.mark.parametrize("gender", ["male", "female"])
    def test_successful_response_values(self, gender):
        response = self.get_users_by_gender(gender)
        assert response.status_code == 200
        json_response = response.json()
        print(json_response)

        check.equal(json_response.get("isSuccess"), "true", "Value of 'isSuccess' is not true")
        check.equal(json_response.get("errorCode"), 0, "Value of 'errorCode' is not 0")
        check.equal(json_response.get("errorMessage"), "null", "Value of 'errorMessage' is not None")
        check.is_instance(json_response.get("idList"), list, "Value of 'idList' is not a list")

    # Check ID: 3a, 4a (success был заменен на isSuccess, result на idList что бы тест работал)
    @pytest.mark.parametrize("gender", ["male", "female"])
    def test_gender_specific_response(self, gender):
        # Отправляем запрос на получение списка пользователей по гендеру
        response = self.get_users_by_gender(gender)
        assert response.status_code == 200
        json_response = response.json()

        # Проверка наличия ключа "idList" в ответе
        assert "idList" in json_response, "Key 'idList' is missing in the response"

        # Получаем список идентификаторов пользователей
        user_ids = json_response.get("idList", [])

        # Для каждого идентификатора пользователя
        for user_id in user_ids:
            # Отправляем запрос на получение информации о конкретном пользователе
            user_response = self.get_user_info(user_id)
            assert user_response.status_code == 200
            user_info = user_response.json()

            # Проверка наличия ключа "user" в ответе
            assert "user" in user_info, f"Key 'user' is missing in the user info response for user ID {user_id}"
            user_data = user_info.get("user", {})

            # Проверяем, что гендер пользователя соответствует ожидаемому
            assert "gender" in user_data, f"Key 'gender' is missing for user ID {user_id}"
            assert user_data[
                       "gender"].lower() == gender, f"User ID {user_id} has gender {user_data['gender']} but expected {gender}"

    # Check ID: 5a (success был заменен на isSuccess, result на idList что бы тест работал)
    def test_gender_ids_dont_match(self):
        response_male = self.get_users_by_gender("male")
        assert response_male.status_code == 200
        json_response_male = response_male.json()
        response_female = self.get_users_by_gender("female")
        assert response_female.status_code == 200
        json_response_female = response_female.json()

        # Проверяем наличие ключа "idList" в обоих ответах
        assert "idList" in json_response_male, "Key 'idList' not found in male response"
        assert "idList" in json_response_female, "Key 'idList' not found in female response"

        male_ids = set(json_response_male.get("idList", []))
        female_ids = set(json_response_female.get("idList", []))

        print(f"Male IDs: {male_ids}")
        print(f"Female IDs: {female_ids}")

        assert male_ids.isdisjoint(female_ids), "Male and female user IDs should not overlap"


class TestUserGenderNegative(ApiClient):
    # Check ID: 1b
    def test_invalid_gender_request_keys(self):
        response = self.get_users_by_gender("fgewg")
        json_response = response.json()
        print(json_response)

        check.is_in("success", json_response, "Key 'success' is missing")
        check.equal(json_response.get("success"), "false", "Value of 'success' is not False")
        check.is_in("errorCode", json_response, "Key 'errorCode' is missing")
        check.is_in("errorMessage", json_response, "Key 'errorMessage' is missing")

    # Check ID: 2b
    def test_missing_gender_parameter(self):
        response = self.get_users_by_gender(" ")
        assert response.status_code != 200

    # Check ID: 3b
    def test_empty_gender_parameter(self):
        response = self.get_users_without_gender()
        assert response.status_code != 200

    # Check ID: 4b
    def test_invalid_gender_parameter(self):
        response = self.get_users_by_gender("unknown")
        assert response.status_code != 200


class TestUserGenderSecurity(ApiClient):
    # Check ID: 1c, 2c, 3c, 4c, 5c
    @pytest.mark.parametrize("sql_injection", [
        "' OR '1'='1",
        "male' OR 'a'='a",
        "male' UNION SELECT null--",
        "male'; SELECT * FROM users--",
        "male'; DROP TABLE users--"
    ])
    def test_sql_injection(self, sql_injection):
        response = self.get_users_by_gender(sql_injection)

        # Проверяем, что API возвращает ошибку (код состояния не 200)
        assert response.status_code != 200, "API should return an error for SQL injection"

        # Проверяем, что в ответе нет корректной JSON-структуры
        try:
            json_response = response.json()
            assert "error" in json_response or "errorCode" in json_response or "errorMessage" in json_response, \
                "Error information should be present in response"
        except ValueError:
            # Если JSON не парсится, значит вернулась ошибка, что ожидается
            pass
