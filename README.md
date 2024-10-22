# PyMNT - Python Mutant Ninja Tests

This Python project automates testing using LLM and mutation testing.
An LLM to generates test cases and mutation testing is run on those cases to ensure their correctness.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

## Program Flow

TestGenerator -> UnitTestRunner -> MutationRunner

Where:

- The `TestGenerator` generates test cases via an `LLM` model.
- The `UnitTestRunner` runs the generated test cases. To ensure that they pass.
  - If the tests pass, the `MutationRunner` runs mutation testing.
  - Else, the wrong tests are fed back to the `TestGenerator` to generate new tests.
    - The process is repeated until the tests pass, or the maximum number of iterations is reached. Default is 3.
- The `MutationRunner` runs mutation testing on the generated test cases.
  - if the mutation testing passes, the process is complete.
  - Else, the wrong tests are fed back to the `TestGenerator` to generate new tests.
    - The process is repeated until the tests pass, or the maximum number of iterations is reached. Default is 3.
