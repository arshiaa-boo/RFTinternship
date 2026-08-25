
# -----------------------------------------------------
# TASK 1: Function to check whether a number is prime
# -----------------------------------------------------
def is_prime(number):
    """Return True if 'number' is prime, else False."""
    if number < 2:
        return False
    for i in range(2, int(number ** 0.5) + 1):
        if number % i == 0:
            return False
    return True


# -----------------------------------------------------------
# TASK 2: Function using *args that returns the largest number
# -----------------------------------------------------------
def find_largest(*args):
    """Accepts any number of numbers and returns the largest."""
    if not args:
        return None
    return max(args)


# -----------------------------------------------------------------
# TASK 3: Function using **kwargs that prints student information
# -----------------------------------------------------------------
def print_student_info(**kwargs):
    """Accepts any number of keyword arguments and prints them."""
    print("Student Information:")
    for key, value in kwargs.items():
        print(f"  {key}: {value}")


# -----------------------------------------------------------------------
# CHALLENGE: Function that takes a list of numbers and returns
# maximum, minimum, average, and sum
# -----------------------------------------------------------------------
def analyze_numbers(numbers):
    """Takes a list of numbers and returns (max, min, average, sum)."""
    if not numbers:
        return None, None, None, 0

    total = sum(numbers)          # built-in sum() used inside local scope
    maximum = max(numbers)
    minimum = min(numbers)
    average = total / len(numbers)

    return maximum, minimum, average, total


# -----------------------------------------------------
# DEMO / TEST — run this file directly to see output
# -----------------------------------------------------
if __name__ == "__main__":

    print("=" * 50)
    print("TASK 1: Prime Number Check")
    print("=" * 50)
    for n in [2, 15, 17, 1, 29, 100]:
        print(f"{n} is prime: {is_prime(n)}")

    print("\n" + "=" * 50)
    print("TASK 2: Largest number using *args")
    print("=" * 50)
    print("Largest of (4, 9, 2, 17, 6):", find_largest(4, 9, 2, 17, 6))
    print("Largest of (100,):", find_largest(100))

    print("\n" + "=" * 50)
    print("TASK 3: Student info using **kwargs")
    print("=" * 50)
    print_student_info(name="Riya", age=20, course="Python", batch="RFT-2026")

    print("\n" + "=" * 50)
    print("CHALLENGE: Analyze a list of numbers")
    print("=" * 50)
    nums = [12, 45, 7, 89, 23, 56]
    high, low, avg, total = analyze_numbers(nums)
    print(f"Numbers: {nums}")
    print(f"Maximum: {high}")
    print(f"Minimum: {low}")
    print(f"Average: {avg:.2f}")
    print(f"Sum: {total}")