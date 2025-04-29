# computed_field decorator

The computed_field decorator can be used to include property or cached_property attributes when serializing a model or dataclass. The property will also be taken into account in the JSON Schema (in serialization mode).

# field_validator decorator

Field validator is a callable taking the value to be validated as an argument and returning the validated value.
The callable can perform checks for specific conditions (see raising validation errors) and make changes to the validated value (coercion or mutation).

Four different types of validators can be used. They can all be defined using the annotated pattern or using the field_validator() decorator, applied on a class method.

# model_validator decorator

Validation can also be performed on the entire model's data using the model_validator() decorator.
Three different types of model validators can be used:

- After validators:
  Run after the whole model has been validated. As such, they are defined as instance methods and can be seen as post-initialization hooks.
  Important note: the validated instance should be returned.

- Before validators:
  Run before the model is instantiated.
  These are more flexible than after validators, but they also have to deal with the raw input, which in theory could be any arbitrary object.
  Should also avoid mutating the value directly if raising a validation error later in the validator function, as the mutated value may be passed to other validators if using unions.

- Wrap validators:
  The most flexible of all. Can run code before or after Pydantic and other validators process the input data, or can terminate validation immediately, either by returning the data early or by raising an error.
