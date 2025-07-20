import math

def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b

def sin(a):
    return math.sin(math.radians(a))

def cos(a):
    return math.cos(math.radians(a))

def tan(a):
    return math.tan(math.radians(a))

def log(a):
    if a <= 0:
        raise ValueError("Logarithm requires a positive number.")
    return math.log10(a)

def ln(a):
    if a <= 0:
        raise ValueError("Natural logarithm requires a positive number.")
    return math.log(a)

def sqrt(a):
    if a < 0:
        raise ValueError("Cannot take the square root of a negative number.")
    return math.sqrt(a)

def power(a, b):
    return math.pow(a, b)
