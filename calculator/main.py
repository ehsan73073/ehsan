import operations

def main():
    """Provides a command-line interface for the calculator."""
    while True:
        print("\nSelect an operation:")
        print("1. Add")
        print("2. Subtract")
        print("3. Multiply")
        print("4. Divide")
        print("5. Sine")
        print("6. Cosine")
        print("7. Tangent")
        print("8. Logarithm (base 10)")
        print("9. Natural Logarithm")
        print("10. Square Root")
        print("11. Power")
        print("12. Exit")

        choice = input("Enter choice(1-12): ")

        if choice in ['1', '2', '3', '4', '11']:
            try:
                num1 = float(input("Enter first number: "))
                num2 = float(input("Enter second number: "))
            except ValueError:
                print("Invalid input. Please enter a number.")
                continue
        elif choice in ['5', '6', '7', '8', '9', '10']:
            try:
                num1 = float(input("Enter a number: "))
            except ValueError:
                print("Invalid input. Please enter a number.")
                continue

        if choice == '1':
            print("Result:", operations.add(num1, num2))
        elif choice == '2':
            print("Result:", operations.subtract(num1, num2))
        elif choice == '3':
            print("Result:", operations.multiply(num1, num2))
        elif choice == '4':
            try:
                print("Result:", operations.divide(num1, num2))
            except ValueError as e:
                print(e)
        elif choice == '5':
            print("Result:", operations.sin(num1))
        elif choice == '6':
            print("Result:", operations.cos(num1))
        elif choice == '7':
            print("Result:", operations.tan(num1))
        elif choice == '8':
            try:
                print("Result:", operations.log(num1))
            except ValueError as e:
                print(e)
        elif choice == '9':
            try:
                print("Result:", operations.ln(num1))
            except ValueError as e:
                print(e)
        elif choice == '10':
            try:
                print("Result:", operations.sqrt(num1))
            except ValueError as e:
                print(e)
        elif choice == '11':
            print("Result:", operations.power(num1, num2))
        elif choice == '12':
            break
        else:
            print("Invalid input")

if __name__ == "__main__":
    main()
