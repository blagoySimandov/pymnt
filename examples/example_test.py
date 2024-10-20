import unittest
from .example import fibonacci_iterative


class TestFibonacci_iterative(unittest.TestCase):
    def test_fibonacci_iterative_positive_number(self):
        self.assertEqual(fibonacci_iterative(0), 0)
        self.assertEqual(fibonacci_iterative(1), 1)
        self.assertEqual(fibonacci_iterative(2), 1)
        self.assertEqual(fibonacci_iterative(5), 5)
        self.assertEqual(fibonacci_iterative(10), 55)

    def test_fibonacci_iterative_negative_number(self):
        with self.assertRaises(ValueError):
            fibonacci_iterative(-1)

    def test_fibonacci_iterative_large_number(self):
        self.assertEqual(fibonacci_iterative(30), 832040)
        self.assertEqual(fibonacci_iterative(50), 12586269025)

if __name__ == '__main__':
    unittest.main()
