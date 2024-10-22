import importlib
import unittest
import logging
import inspect


class UnitTests:
    """Defines a class to run unit tests programmatically."""

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

    def get_failed_tests_source(
        self, test_results: unittest.TestResult
    ) -> dict[unittest.TestCase, str]:
        """Retrieve the source code of failed tests."""
        failed_tests_source = {}

        for failed_test, _ in test_results.failures + test_results.errors:
            test_method = getattr(failed_test, failed_test._testMethodName)
            source_code = inspect.getsource(test_method)
            failed_tests_source[failed_test] = source_code

        return failed_tests_source
