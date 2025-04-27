from datetime import datetime, date
from enum import Enum
from typing import List, Dict, Optional, Union, Literal, TypeVar, Generic, Any
from pydantic import (
    BaseModel,
    Field,
    computed_field,
    model_validator,
    field_validator,
    ValidationError,
    ConfigDict,
    RootModel,
    TypeAdapter,
    Json,
    SecretStr,
    EmailStr,
    AnyUrl,
    StringConstraints,
    ValidationInfo,
    ValidatorFunctionWrapHandler,
)
from typing_extensions import Annotated
import json
from uuid import UUID
from decimal import Decimal


# 1. Basic Model Definition with New Features
class UserRole(str, Enum):
    """User roles in the system"""

    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class User(BaseModel):
    """User model with various validation and configuration features"""

    id: Annotated[int, Field(gt=0, description="User ID must be positive")]
    username: Annotated[str, StringConstraints(min_length=3, max_length=50)]
    email: EmailStr
    password: SecretStr
    password_confirm: SecretStr
    role: UserRole = UserRole.USER
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    tags: List[str] = Field(default_factory=list)
    profile_url: Optional[AnyUrl] = None

    # model configuration using ConfigDict
    model_config = ConfigDict(
        strict=True,
        frozen=False,
        validate_assignment=True,
        populate_by_name=True,
        extra="forbid",
        str_strip_whitespace=True,
        str_to_lower=True,
        json_schema_extra={
            "examples": [{"id": 1, "username": "john_doe", "email": "john@example.com"}]
        },
    )

    # computed_field decorator
    @computed_field
    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    # model validator for username being alphanumeric
    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, value: str) -> str:
        if not value.isalnum():
            raise ValueError("Username must be alphanumeric")
        return value

    # model validator for password containing username
    @model_validator(mode="after")
    def check_password_username(self) -> "User":
        if (
            self.password.get_secret_value()
            and self.username in self.password.get_secret_value()
        ):
            raise ValueError("Password cannot contain username")
        return self

    # model validator for password confirmation
    @model_validator(mode="after")
    def check_password_confirm(self) -> "User":
        if self.password.get_secret_value() != self.password_confirm.get_secret_value():
            raise ValueError("Password confirmation does not match")
        return self


# 2. Generic Models
T = TypeVar("T")


class Response(BaseModel, Generic[T]):
    data: T
    status: int
    message: str


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int


# 3. RootModel for List/Dict Validation
class UserList(RootModel[List[User]]):
    root: List[User]

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


# 4. Type Adapters
user_dict_adapter = TypeAdapter(Dict[str, User])
user_list_adapter = TypeAdapter(List[User])


# 5. Advanced Field Types and Constraints
class Product(BaseModel):
    id: UUID
    name: Annotated[str, StringConstraints(min_length=1, max_length=100)]
    price: Annotated[Decimal, Field(gt=0, decimal_places=2)]
    quantity: Annotated[int, Field(ge=0)]
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    category: Optional[str] = None
    rating: Annotated[float, Field(ge=0, le=5, default=0.0)]
    status: Literal["active", "inactive"] = "active"


# 6. Custom Types and Validators
class PositiveInt:
    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: ValidatorFunctionWrapHandler
    ) -> Any:
        return {"type": "int", "gt": 0, "title": "PositiveInt"}


# 7. JSON Handling
class JsonConfig(BaseModel):
    settings: Json[Dict[str, Any]]
    features: Json[List[str]]


# 8. Nested Models and Complex Validation
class Address(BaseModel):
    street: str
    city: str
    country: str
    postal_code: str


class Customer(BaseModel):
    user: User
    addresses: List[Address]
    primary_address: Optional[int] = Field(
        default=None, description="Index of primary address"
    )

    @model_validator(mode="after")
    def validate_primary_address(self) -> "Customer":
        if self.primary_address is not None:
            if not (0 <= self.primary_address < len(self.addresses)):
                raise ValueError("Primary address index out of range")
        return self


# 9. Model Inheritance and Unions
class BaseEvent(BaseModel):
    id: UUID
    timestamp: datetime
    type: str


class UserEvent(BaseEvent):
    type: Literal["user_event"]
    user_id: int
    action: str


class SystemEvent(BaseEvent):
    type: Literal["system_event"]
    component: str
    level: Literal["info", "warning", "error"]


Event = Union[UserEvent, SystemEvent]


# 10. Advanced Usage Examples
class Settings(BaseModel):
    """Example of complex model with various features"""

    app_name: str
    debug: bool = False
    database_url: SecretStr
    allowed_hosts: List[str] = ["localhost"]
    cors_origins: List[AnyUrl] = Field(default_factory=list)
    cache_ttl: Annotated[int, Field(gt=0, lt=3600)] = 300
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    api_keys: Dict[str, SecretStr] = Field(default_factory=dict)
    feature_flags: Dict[str, bool] = Field(default_factory=dict)

    @field_validator("allowed_hosts")
    @classmethod
    def validate_allowed_hosts(cls, v: List[str]) -> List[str]:
        return [host.lower() for host in v]


# 11. Error Handling and Validation
def handle_validation_error(error: ValidationError) -> Dict[str, Any]:
    return {
        "errors": [
            {"loc": err["loc"], "msg": err["msg"], "type": err["type"]}
            for err in error.errors()
        ]
    }


# 12. Type Adapters Usage
def validate_json_payload(data: str) -> Dict[str, Any]:
    try:
        raw_data = json.loads(data)
        adapter = TypeAdapter(Dict[str, Any])
        return adapter.validate_python(raw_data)
    except ValidationError as e:
        raise ValueError(handle_validation_error(e))


# 13. Example Usage
def main() -> None:
    try:
        # Create a user
        user = User(
            id=1,
            username="john_doe",
            email="john@example.com",
            password=SecretStr(secret_value="password1"),
            password_confirm=SecretStr(secret_value="password1"),
            role=UserRole.ADMIN,
        )

        # Create a response with generic type
        response = Response[User](
            data=user, status=200, message="User created successfully"
        )

        # Validate a list of users
        users_data = [
            {
                "id": 1,
                "username": "user1",
                "email": "user1@example.com",
                "password": "pass1",
                "password_confirm": "pass1",
            },
            {
                "id": 2,
                "username": "user2",
                "email": "user2@example.com",
                "password": "pass2",
                "password_confirm": "pass2",
            },
        ]
        users: UserList = UserList.model_validate(obj=users_data)

        # Use type adapter
        validated_users: List[User] = user_list_adapter.validate_python(users_data)

        print("Validation successful")

    except ValidationError as e:
        print("Validation error:", handle_validation_error(e))


if __name__ == "__main__":
    main()
