import argparse
import sys
import logging
from typing import Any, Callable
from test_generator import OpenAITestGenerator
from unit_tests import UnitTests
from mutation_tester import MutPyRunner
from util import exec_module

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def load_function(file_path: str, function_name: str) -> Callable[..., Any]:
    module = exec_module(file_path)
    return getattr(module, function_name)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Automated Testing Library with Mutation Testing"
    )
    parser.add_argument(
        "file_path", help="Path to the Python file containing the function to test"
    )
    parser.add_argument("function_name", help="Name of the function to test")
    args = parser.parse_args()

    function_to_test = load_function(args.file_path, args.function_name)

    test_generator = OpenAITestGenerator()
    output_file = args.file_path.replace(".py", "_test.py")
    test_generator.generate_tests([function_to_test], output_file)
    unit_tests = UnitTests()
    test_results = unit_tests.run_tests(
        "examples/example_test.py"
    )  # TODO: Change this to output_file
    if not test_results.wasSuccessful():
        logging.error(
            "Unit tests failed. Please fix the issues before proceeding with mutation testing."
        )
        sys.exit(1)
    mutation_runner = MutPyRunner(
        target_module="examples/example.py", test_module="examples/example_test.py"
    )
    mutation_runner.run()


if __name__ == "__main__":
    main()
