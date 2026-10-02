print("Hello FDE")
from dotenv import load_dotenv
import os

load_dotenv()
print(os.getenv("API_KEY"))


def factorial(n):
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers.")
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result


# Example usage
print(factorial(5))