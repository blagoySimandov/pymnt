"""
Collection of examples of basic mathematical functions used to test PyMNT
"""


# Function to calculate the nth Fibonacci number iteratively
def fibonacci_iterative(n):
    if n < 0:
        raise ValueError("Negative numbers are not allowed.")
    a, b = 0, 1
    for _ in range(0, n):
        a, b = b, a + b
    return a


# Function to calculate the nth Fibonacci number recursively
def fibonacci_recursive(n):
    if n < 0:
        raise ValueError("Negative numbers are not allowed.")
    if n == 0:
        return 0
    if n == 1:
        return 1
    return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2)


# Function to check if a number is prime
def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, int(n**2) + 1):
        if n % i == 0:
            return False
    return True


# Function to calculate the greatest common divisor (GCD) using Euclidean algorithm
def gcd(a, b):
    while b:
        a, b = b, a % b
    return a


# Function to calculate the least common multiple (LCM)
def lcm(a, b):
    if a == 0 or b == 0:
        return 0
    return abs(a * b) // gcd(a, b)


# Function to calculate the sum of the first n natural numbers
def sum_natural_numbers(n):
    if n < 0:
        raise ValueError("Negative numbers are not allowed.")
    return n * (n + 1) // 2


# Function to calculate the power of a number (x^y) iteratively
def power_iterative(x, y):
    if y < 0:
        raise ValueError("Negative exponent is not supported.")
    result = 1
    for _ in range(y):
        result *= x
    return result


# Function to calculate the power of a number (x^y) recursively
def power_recursive(x, y):
    if y < 0:
        raise ValueError("Negative exponent is not supported.")
    if y == 0:
        return 1
    return x * power_recursive(x, y - 1)
