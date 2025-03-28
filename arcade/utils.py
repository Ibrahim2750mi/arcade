"""
Various utility functions.

IMPORTANT:
These  should be standalone and not rely on any arcade imports
"""
import functools
import platform
import sys
import warnings
from typing import Tuple, Type
from pathlib import Path


class PerformanceWarning(Warning):
    """Use this for issuing performance warnings."""
    pass


class ReplacementWarning(Warning):
    """Use this for issuing warnings about naming and functionality changes."""
    pass


def warning(warning_type: Type[Warning], message: str = "", **kwargs):
    def actual_warning_decorator(func):
        nonlocal message
        if warning_type == ReplacementWarning and not message:
            message = f"{func.__name__} is deprecated. Use {kwargs.get('new_name', '')} instead."
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(message, warning_type)
            return func(*args, **kwargs)
        return wrapper
    return actual_warning_decorator


def generate_uuid_from_kwargs(**kwargs) -> str:
    """
    Given key/pair combos, returns a string in uuid format.
    Such as `text='hi', size=32` it will return "text-hi-size-32".
    Called with no parameters, id does NOT return a random unique id.
    """
    if len(kwargs) == 0:
        raise Exception("generate_uuid_from_kwargs has to be used with kwargs, please check the doc.")

    return "|".join(f"{key}={str(value)}" for key, value in kwargs.items())


def is_raspberry_pi() -> bool:
    """
    Determine if the host is a raspberry pi.

    :returns: bool
    """
    return get_raspberry_pi_info()[0]


def get_raspberry_pi_info() -> Tuple[bool, str, str]:
    """
    Determine if the host is a raspberry pi
    with additional info.

    :returns: 3 component tuple.
              bool (is host a raspi)
              str (architecture)
              str (model name)
    """
    # armv7l is raspi 32 bit
    # aarch64 is raspi 64 bit
    architecture = platform.machine()
    model_name = ""

    # The platform for raspi should always be linux
    if not sys.platform == "linux":
        return False, "", ""

    # Check for model info file
    MODEL_PATH = Path("/sys/firmware/devicetree/base/model")
    if MODEL_PATH.exists():
        try:
            model_name = MODEL_PATH.read_text()[:-1]
            if "raspberry pi" in model_name.lower():
                return True, architecture, model_name
        except Exception:
            pass

    return False, "", ""
