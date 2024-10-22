import logging
import inspect
import unittest


class FixApplier:
    def __init__(self, suggested_fix: str):
        self._suggested_fix = suggested_fix

    def apply_test_fix(self, test_case: unittest.TestCase):
        """
        Apply the suggested test fix by replacing the specific test method in the test case.
        """
        try:
            source_file = inspect.getsourcefile(test_case.__class__)
            if source_file is None:
                logging.error(f"Could not find source file for {test_case.__class__}")
                return

            test_method_name = test_case._testMethodName
            test_method = getattr(test_case.__class__, test_method_name)

            lines, method_start = inspect.getsourcelines(test_method)
            method_end = method_start + len(lines) - 1

            # could make it better by seeing what indentation the method is at and using that
            indented_fix = "    " + self._suggested_fix.replace("\n", "\n    ")

            with open(source_file, "r") as file:
                all_lines = file.readlines()

            new_lines = (
                all_lines[: method_start - 1]  # lines before the method
                + [indented_fix + "\n"]  # new implementation
                + all_lines[method_end:]  # lines after the method
            )

            with open(source_file, "w") as file:
                file.writelines(new_lines)

            logging.info(
                f"Test fix applied successfully to method {test_method_name} in {test_case.__class__.__name__} ({source_file})."
            )
        except Exception as e:
            logging.error(f"Error applying test fix: {e}")

    @property
    def suggested_fix(self):
        return self._suggested_fix

    @suggested_fix.setter
    def suggested_fix(self, new_suggested_fix: str):
        self._suggested_fix = new_suggested_fix
