"""computed field"""

from pprint import pprint

from pydantic import BaseModel, computed_field


class Box(BaseModel):
    width: float
    height: float
    depth: float

    @computed_field
    @property
    def volume(self) -> float:
        return self.width * self.height * self.depth


print('\n pprint - Box.model_json_schema(mode="serialization")\n')
pprint(object=Box.model_json_schema(mode="serialization"))


# Usage
def main() -> None:
    box = Box(width=1, height=2, depth=3)
    print(f"\n{box.volume = }")
    print(f"\n{box.model_dump(mode="json") = }")


if __name__ == "__main__":
    main()
