"""Model validators."""

from typing import Any
from typing_extensions import Self

from pydantic import (
    BaseModel,
    EmailStr,
    model_validator,
    SecretStr,
    ValidationInfo,
)
from pydantic.functional_validators import ModelWrapValidatorHandler


class User(BaseModel):
    id: int
    name: str
    email: EmailStr
    password: SecretStr
    password_confirm: SecretStr

    def __str__(self) -> str:
        return (
            f"User(id={self.id}, name='{self.name}', email='{self.email}', "
            f"password='{self.password}', password_confirm='{self.password_confirm}')"
        )

    # before validators
    @model_validator(mode="before")
    @classmethod
    def normalize_user_name(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "name" in data:
                data["name"] = data["name"].strip().title()
        return data

    # before validators
    @model_validator(mode="before")
    @classmethod
    def normalize_user_email(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "email" in data:
                data["email"] = data["email"].lower().strip()
        return data

    # after validators
    @model_validator(mode="after")
    def passwords_confirm(self) -> Self:
        if self.password.get_secret_value() != self.password_confirm.get_secret_value():
            raise ValueError("Passwords do not match")
        return self

    # before validators
    @model_validator(mode="before")
    @classmethod
    def card_number_exists(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "card_number" in data:
                raise ValueError("'card_number' should not be included")
        return data

    # wrap validator
    @model_validator(mode="wrap")
    @classmethod
    def log_validation_flow(
        cls, values: Any, handler: ModelWrapValidatorHandler[Self], info: ValidationInfo
    ) -> Self:
        """
        Logs the input data before validation and the outcome after validation.
        'values' is the input data (e.g., a dictionary).
        'handler' is the next step in the validation chain.
        'info' provides context about the validation call.
        """
        print(f"\nWRAP: Starting validation for {cls.__name__}.")
        print(f"WRAP: Input data: {values}")

        try:
            # Call the handler to proceed with 'before' validators, field parsing/validation, and 'after' validators
            validated_instance: Self = handler(values)
            print(f"\nWRAP: Validation successful for {cls.__name__}.")
            print(
                f"WRAP: Validated User ID: {validated_instance.id}, Name: {validated_instance.name}, Email: {validated_instance.email}"
            )
            return validated_instance
        except (
            ValueError
        ) as e:  # Catching ValueError as other validators might raise it
            print(f"\nWRAP: Validation failed for {cls.__name__} with ValueError: {e}")
            raise  # Re-raise the exception


# Entrypoint
def main() -> None:
    # Valid user - no card_number
    try:
        user1 = User(
            id=1,
            name="  John Doe  ",  # name will be normalized to "John Doe"
            email="   John.Doe@Example.com",  # email will be normalized to "john.doe@example.com"
            password=SecretStr(secret_value="password1"),
            password_confirm=SecretStr(secret_value="password1"),
        )
        print(f"\nValid user created: {user1}")
    except ValueError as e:
        print(f"\nError creating user: {e}")

    # Invalid user with card_number
    try:
        # Using **kwargs to pass extra fields
        user2: dict[str, Any] = {
            "id": 2,
            "name": "Jane Smith",
            "email": "jane.smith@example.com",
            "password": SecretStr(secret_value="password2"),
            "password_confirm": SecretStr(secret_value="password2"),
            "card_number": "1234-5678-9012-3456",
        }
        user_with_card = User(**user2)
        print(f"\nUser with card created: {user_with_card}")
    except ValueError as e:
        print(f"\nError creating user with card: {e}")


if __name__ == "__main__":
    main()
