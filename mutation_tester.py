import subprocess
import abc


class MutationRunner(abc.ABC):
    """
    Defines an interface for running mutation testing.
    """

    def __init__(self, target_module, test_module):
        self._target_module = target_module
        self._test_module = test_module

    @abc.abstractmethod
    def run(self):
        pass


# todo: implement a MutPyRunner that is not dependent on the command line
class MutPyRunner(MutationRunner):
    """
    Defines a runner for MutPy mutation testing tool.
    """

    def __init__(self, target_module, test_module):
        self._target_module = self._convert_path_to_module(target_module)
        self._test_module = self._convert_path_to_module(test_module)
        # mut.py --target examples.example --unit-test examples.example_test -m
        self._command = [
            "mut.py",
            "--target",
            self._target_module,
            "--unit-test",
            self._test_module,
            "--runner",
            "unittest",
        ]

    def _convert_path_to_module(self, path):
        """
        Convert a file path to a module path.
        """
        return path.replace("./", "").replace("/", ".").replace(".py", "")

    # Pretty naive implementation. Should be improved. Definitely not alright to run mut py from the command line.
    def run(self):
        try:
            process = subprocess.Popen(
                self._command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            while True:
                if process.stdout is None:
                    break
                output = process.stdout.readline()
                if output == "" and process.poll() is not None:
                    break
                if output:
                    print(output.strip())

            stderr = process.communicate()[1]
            if stderr:
                print(stderr.strip())

            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, self._command)

        except subprocess.CalledProcessError as error:
            raise RuntimeError(f"An error occurred while running MutPy: {error}")
        except FileNotFoundError:
            raise RuntimeError(
                "MutPy command not found. Make sure it's installed and in your PATH."
            )
