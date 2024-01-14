import inspect
from typing import List, Dict, Any, Union, Optional
from pydantic import BaseModel


def validate_with_model(*models):
    """a decorator that will use the Pydantic model to parse and validate the input"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            # Merge args and kwargs into a single dict
            sig = inspect.signature(func)
            bound_args = sig.bind_partial(*args, **kwargs)
            bound_args.apply_defaults()
            keyword_args = bound_args.arguments.pop("kwargs")

            # creating Pydantic classes
            for name, param in sig.parameters.items():
                if issubclass(param.annotation, BaseModel):
                    for model in models:
                        if model == param.annotation:
                            model_dict = {
                                key: value
                                for key, value in keyword_args.items()
                                if key in model.model_fields
                            }
                            model_object = model(**model_dict)
                            keyword_args[name] = model_object
                            keyword_args = {
                                key: value
                                for key, value in keyword_args.items()
                                if key not in model_dict.keys()
                            }
                            break

            # Pass the model instance(s) to the wrapped function
            return func(*bound_args.args, **keyword_args)

        return wrapper

    return decorator
