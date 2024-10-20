import subprocess
import abc


class MutationRunner(abc.ABC):
    """
    Defines an interface for running mutation testing.
    """

    def __init__(self, target_module, test_module):
        self.target_module = target_module
        self.test_module = test_module

    @abc.abstractmethod
    def run(self) -> str:
        pass

    @abc.abstractmethod
    def _process_output(self, result):
        pass


# todo: implement a MutPyRunner that is not dependent on the command line
class MutPyRunner(MutationRunner):
    """
    Defines a runner for MutPy mutation testing tool.
    """

    def __init__(self, target_module, test_module):
        self._target_module = target_module
        self._test_module = test_module
        self.command = [
            "mut.py",
            "--target",
            self._target_module,
            "--unit-test",
            self._test_module,
            "--runner",
            "pytest",
        ]

    def run(self):
        try:
            result = subprocess.run(
                self.command, capture_output=True, text=True, check=True
            )
            return self._process_output(result)
        except subprocess.CalledProcessError as error:
            raise RuntimeError(f"An error occurred while running MutPy: {error}")
        except FileNotFoundError:
            raise RuntimeError(
                "MutPy command not found. Make sure it's installed and in your PATH."
            )

    def _process_output(self, result):
        output = "MutPy output:\n"
        output += result.stdout

        if result.stderr:
            output += "\nErrors:\n"
            output += result.stderr

        return output
