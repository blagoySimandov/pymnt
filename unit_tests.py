import unittest
import importlib
import logging


class UnitTests:
    def run_tests(self, test_file: str) -> unittest.TestResult:
        logging.info(f"Running unit tests from {test_file}")

        if test_file.endswith(".py"):
            test_file = test_file[:-3]

        test_file = test_file.replace("/", ".").replace("\\", ".")

        test_module = importlib.import_module(test_file)

        suite = unittest.TestLoader().loadTestsFromModule(test_module)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)

        return result
