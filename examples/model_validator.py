from typing import Any
from typing_extensions import Self
from pydantic import BaseModel, model_validator, SecretStr


class User(BaseModel):
    id: int
    name: str
    password: SecretStr
    password_confirm: SecretStr

    def __str__(self) -> str:
        return f"User(id={self.id}, name={self.name}, password={self.password}, password_confirm={self.password_confirm})"

    # after validators
    @model_validator(mode="after")
    def check_passwords_match(self) -> Self:
        if self.password.get_secret_value() != self.password_confirm.get_secret_value():
            raise ValueError("Passwords do not match")
        return self

    # before validators
    @model_validator(mode="before")
    @classmethod
    def check_card_number_not_present(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "card_number" in data:
                raise ValueError("'card_number' should not be included")
        return data


# Usage
def main() -> None:
    # Valid user - no card_number
    try:
        user1 = User(
            id=1,
            name="John Doe",
            password=SecretStr(secret_value="password1"),
            password_confirm=SecretStr(secret_value="password1"),
        )
        print(f"Valid user created: {user1}")
    except ValueError as e:
        print(f"Error creating user: {e}")

    # Invalid user with card_number
    try:
        # Using **kwargs to pass extra fields
        user2: dict[str, Any] = {
            "id": 2,
            "name": "Jane Smith",
            "password": SecretStr(secret_value="password2"),
            "password_confirm": SecretStr(secret_value="password2"),
            "card_number": "1234-5678-9012-3456",
        }
        user_with_card = User(**user2)
        print(f"User with card created: {user_with_card}")
    except ValueError as e:
        print(f"Error creating user with card: {e}")


if __name__ == "__main__":
    main()
