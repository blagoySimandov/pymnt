import argparse
import sys
import inspect
import logging
from typing import Any, Callable
from test_generator import OpenAITestGenerator, AnalysisResult
from unit_tests import UnitTests
from mutation_tester import MutPyRunner
from fix_applier import FixApplier
from util import exec_module

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("debug.log"), logging.StreamHandler(sys.stdout)],
)


def load_function(file_path: str, function_name: str) -> Callable[..., Any]:
    module = exec_module(file_path)
    return getattr(module, function_name)


MAX_ITERATIONS = 3


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

    test_generator = OpenAITestGenerator(functions=[function_to_test])
    unit_test_runner = UnitTests()
    output_file = args.file_path.replace(".py", "_test.py")
    mutation_runner = MutPyRunner(args.file_path, output_file)

    for _ in range(MAX_ITERATIONS):
        test_results = unit_test_runner.run_tests("examples/example_test.py")
        if test_results.wasSuccessful():
            break
        else:
            test_source_map = unit_test_runner.get_failed_tests_source(test_results)
            # for now just get the first as we are running pymnt on only one function. func_source = inspect.getsource(function_to_test)
            test_method = list(test_source_map.keys())[0]
            test_source = test_source_map[test_method]
            func_source = inspect.getsource(function_to_test)
            result = test_generator.attempt_to_fix_test(func_source, test_source)
            logging.info(
                f"Fixing test: {result.result_type}, result: {result.suggestion}"
            )
            applier = FixApplier(result.suggestion)
            if result.result_type == AnalysisResult.FUNC_FAULT:
                logging.info(
                    f"Function fault detected. Suggested fix: {result.suggestion}"
                )
                print(
                    "Function fault detected. Suggested fix: ", result.suggestion
                )  # just print the suggestion i guess ?
                break
            elif result.result_type == AnalysisResult.TEST_FAULT:
                logging.info(f"Test fault detected. Suggested fix: {result.suggestion}")
                applier.apply_test_fix(test_method)
                continue  # run unit tests again
            elif result.result_type == AnalysisResult.UNKNOWN_FAULT:
                logging.info("Could not determine fault.Retrying...")
    else:
        logging.error("Max iterations reached. Exiting...")
        sys.exit(1)
    # MUTATION TESTING PART
    mutation_runner.run()


if __name__ == "__main__":
    main()
