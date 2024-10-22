import os
import logging
import inspect
from typing import Callable, Any
from abc import ABC, abstractmethod
from openai import OpenAI
from enum import Enum
from dataclasses import dataclass


class AnalysisResult(Enum):
    TEST_FAULT = 0  # test is wrong, needs fixing
    FUNC_FAULT = 1  # function is wrong, suggested fix provided
    UNKNOWN_FAULT = 2  # cannot determine the issue


@dataclass
class FixAttemptResult:
    result_type: AnalysisResult
    suggestion: str


class TestGenerator(ABC):
    functions: list[Callable[..., Any]]

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def generate_tests(self, output_file: str) -> None:
        pass


class OpenAITestGenerator(TestGenerator):
    """
    Generates unit tests for multiple Python functions using OpenAI's GPT API.
    Requires an OpenAI API key located in the environment variable OPENAI_API_KEY.
    """

    _base_prompt = """
            Generate Python unit tests for the following function. Ensure the syntax is always correct. 
            Provide comprehensive and unique test cases that cover various scenarios, including edge cases and exceptions. Be careful with the limits of python. Only generate the methods inside the class. 
            Do not include the class definition or imports.
            Do not give your code in code formatted block.
            Do not forget to include the self argument in each method.
            Use a single tab for indentation.
            The function is not a method of the class. Call it and use it as it is.
            keep indentation the same among the methods.
            """
    _api_key = os.getenv("OPENAI_API_KEY")
    if not _api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    client = OpenAI(api_key=_api_key)

    def __init__(self, functions: list[Callable[..., Any]]) -> None:
        self.functions = functions

    def generate_tests(self, output_file: str) -> None:
        all_test_cases = []
        for function in self.functions:
            logging.info(f"Generating tests for function: {function.__name__}")
            logging.debug(f"Source code of function: {inspect.getsource(function)}")

            prompt = f"""
            {self._base_prompt}
            {function.__name__}
            {inspect.getsource(function)}
            """

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that generates Python unit tests.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=1500,
                temperature=0.7,
            )
            content = response.choices[0].message.content
            if content is None:
                raise ValueError("response was invalid")
            test_cases = content.strip()
            all_test_cases.append((function, test_cases))

        test_file_content = self._generate_test_file_content(all_test_cases)

        with open(output_file, "w") as f:
            f.write(test_file_content)

        logging.info(f"Test cases generated and saved to {output_file}")

    def attempt_to_fix_test(
        self, source_of_function: str, failed_unit_test: str
    ) -> FixAttemptResult:
        """
        Attempts to fix a failing unit test by determining whether the test or function is at fault
        and generating corrected code suggestions.
        Returns:
            FixAttemptResult: Contains both the analysis result type and suggested fix
                - result_type: AnalysisResult enum indicating what's at fault
                - suggestion: Either fixed test code, suggested function fix, or explanation
        """
        max_attempts = 3

        for attempt in range(max_attempts):
            # first, determine if the function or test is at fault
            analysis_prompt = f"""
            Analyze this function and its failing unit test to determine which has the problem.
            Consider only syntax, logic, and correctness - not style or best practices.
            
            Function:
            {source_of_function}
            
            Failing Test:
            {failed_unit_test}
            
            Respond with ONE of these exactly:
            'TEST_FAULT' - if the test appears incorrect
            'FUNC_FAULT' - if the function appears incorrect
            'UNKNOWN_FAULT' - if you cannot determine which is wrong
            """
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a Python testing expert. Analyze code and respond precisely.",
                    },
                    {"role": "user", "content": analysis_prompt},
                ],
                max_tokens=20,
                temperature=0.1,
            )

            if response.choices[0].message.content is None:
                raise ValueError("Invalid response from OpenAI API")

            fault_type = response.choices[0].message.content.strip().upper()

            if fault_type == "UNKNOWN_FAULT":
                return FixAttemptResult(
                    AnalysisResult.UNKNOWN_FAULT,
                    "Unable to determine whether the function or test is at fault.",
                )

            if fault_type == "FUNC_FAULT":
                fix_prompt = f"""
                The function appears to be incorrect. Provide a corrected version that would make the test pass.
                Only provide the fixed function code, no explanations or markdown.
                
                Current Function:
                {source_of_function}
                
                Test to Satisfy:
                {failed_unit_test}
                """

                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a Python expert. Generate only the corrected function code.",
                        },
                        {"role": "user", "content": fix_prompt},
                    ],
                    max_tokens=1000,
                    temperature=0.7,
                )

                if response.choices[0].message.content is None:
                    continue

                suggested_fix = response.choices[0].message.content.strip()
                return FixAttemptResult(AnalysisResult.FUNC_FAULT, suggested_fix)

            # If we reach here, attempt to fix the test
            fix_prompt = f"""
            Fix the following failing unit test for this function.
            Ensure the test is correct, properly handles edge cases, and uses valid assertions.
            Only provide the fixed test method code, no explanations or markdown.
            
            Function:
            {source_of_function}
            
            Current Failing Test:
            {failed_unit_test}
            """

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a Python testing expert. Generate only the corrected test code.",
                    },
                    {"role": "user", "content": fix_prompt},
                ],
                max_tokens=1000,
                temperature=0.7,
            )

            if response.choices[0].message.content is None:
                continue

            fixed_test = response.choices[0].message.content.strip()

            # Verify the fixed test looks valid
            if "def test_" in fixed_test and "self" in fixed_test:
                return FixAttemptResult(AnalysisResult.TEST_FAULT, fixed_test)

        return FixAttemptResult(
            AnalysisResult.UNKNOWN_FAULT,
            "Unable to generate a valid fix after multiple attempts",
        )

    def _generate_test_file_content(self, all_test_cases: list[tuple]) -> str:
        content = "import unittest\n"

        modules = set(func.__module__ for func, _ in all_test_cases)
        for module in modules:
            content += f"from .{module} import {', '.join(func.__name__ for func, _ in all_test_cases if func.__module__ == module)}\n"

        content += "\n\n"

        for function, test_cases in all_test_cases:
            content += (
                f"class Test{function.__name__.capitalize()}(unittest.TestCase):\n    "
            )
            content += test_cases
            content += "\n"

        content += """
if __name__ == '__main__':
    unittest.main()
"""
        return content
