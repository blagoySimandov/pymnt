import os
import logging
import inspect
from typing import Callable, Any
from abc import ABC, abstractmethod
from openai import OpenAI


class TestGenerator(ABC):
    @abstractmethod
    def generate_tests(
        self, functions: list[Callable[..., Any]], output_file: str
    ) -> None:
        pass


class OpenAITestGenerator(TestGenerator):
    """
    Generates unit tests for multiple Python functions using OpenAI's GPT API.
    Requires an OpenAI API key located in the environment variable OPENAI_API_KEY.
    """

    def __init__(self) -> None:
        __api_key = os.getenv("OPENAI_API_KEY")
        if not __api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        self.client = OpenAI(api_key=__api_key)

    def generate_tests(
        self, functions: list[Callable[..., Any]], output_file: str
    ) -> None:
        all_test_cases = []
        for function in functions:
            logging.info(f"Generating tests for function: {function.__name__}")
            logging.debug(f"Source code of function: {inspect.getsource(function)}")

            prompt = f"""
            Generate Python unit tests for the following function. Ensure the syntax is always correct. 
            Provide comprehensive and unique test cases that cover various scenarios, including edge cases and exceptions. Be careful with the limits of python. Only generate the methods inside the class. 
            Do not include the class definition or imports.
            Do not give your code in code formatted block.
            Do not forget to include the self argument in each method.
            Use a single tab for indentation.
            The function is not a method of the class call it and use it as it is.
            keep indentation the same among the methods.
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
            print(content)
            if content is None:
                raise ValueError("response was invalid")
            test_cases = content.strip()
            all_test_cases.append((function, test_cases))

        test_file_content = self._generate_test_file_content(all_test_cases)

        with open(output_file, "w") as f:
            f.write(test_file_content)

        logging.info(f"Test cases generated and saved to {output_file}")

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
