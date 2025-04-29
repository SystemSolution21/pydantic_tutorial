"""computed field"""

from pydantic import BaseModel, computed_field
from pprint import pprint


class Box(BaseModel):
    width: float
    height: float
    depth: float

    @computed_field
    @property
    def volume(self) -> float:
        return self.width * self.height * self.depth


pprint(object=Box.model_json_schema(mode="serialization"))
# model_json_schema(mode= "serialization")
"""
{
    'properties': {
        'width': {'title': 'Width', 'type': 'number'},
        'height': {'title': 'Height', 'type': 'number'},
        'depth': {'title': 'Depth', 'type': 'number'},
        'volume': {'readOnly': True, 'title': 'Volume', 'type': 'number'},
    },
    'required': ['width', 'height', 'depth', 'volume'],
    'title': 'Box',
    'type': 'object',
}
"""


# Usage
def main() -> None:
    box = Box(width=1, height=2, depth=3)
    print(f"{box.volume = }")
    print(box.model_dump(mode="json"))


if __name__ == "__main__":
    main()
