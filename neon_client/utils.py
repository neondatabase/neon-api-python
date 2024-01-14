import inspect
from typing import List, Dict, Any, Union, Optional
from pydantic import BaseModel


def validate_obj_model(parameter_name: str, model: BaseModel):
    """A decorator that validates the 'obj' argument against the specified model."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            # Get the 'obj' argument.
            obj = kwargs.get(parameter_name)

            # If the 'obj' argument is not provided, raise an exception.
            if obj is None:
                raise ValueError(f"Missing required argument '{parameter_name}'.")

            # Validate the 'obj' argument against the specified model.
            model.model_validate(obj)

            # Call the wrapped function.
            return func(*args, **kwargs)

        return wrapper

    return decorator
