import importlib.util
import os
import errno
from types import ModuleType


def exec_module(test_file: str) -> ModuleType:
    # Extract the base name of the file without the directory path and file extension
    module_name = os.path.splitext(os.path.basename(test_file))[0]

    # Create a module spec with the correct module name
    spec = importlib.util.spec_from_file_location(module_name, test_file)
    if spec is None:
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), test_file)

    test_module = importlib.util.module_from_spec(spec)
    if spec.loader is None:
        raise Exception("loader is None")

    spec.loader.exec_module(test_module)
    return test_module
