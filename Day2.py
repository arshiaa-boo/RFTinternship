# Project 2 - Student Score Analyzer
# GOW AI Academy - Python Internship Day 2

MARKS = [78, 85, 90, 67, 85, 92, 78]

# ── Core Functions ──────────────────────────────────────

def calculate_average(marks):
    return sum(marks) / len(marks)

def get_highest(marks):
    return max(marks)

def get_lowest(marks):
    return min(marks)

def count_above_average(marks, average):
    count = 0
    for mark in marks:
        if mark > average:
            count += 1
    return count

# ── Bonus: Grade Distribution ────────────────────────────

def get_grade(mark):
    if mark >= 90:
        return "A"
    elif mark >= 80:
        return "B"
    elif mark >= 70:
        return "C"
    elif mark >= 60:
        return "D"
    else:
        return "Fail"

def grade_distribution(marks):
    distribution = {"A": 0, "B": 0, "C": 0, "D": 0, "Fail": 0}
    for mark in marks:
        grade = get_grade(mark)
        distribution[grade] += 1
    return distribution

# ── Main Program ─────────────────────────────────────────

average  = calculate_average(MARKS)
highest  = get_highest(MARKS)
lowest   = get_lowest(MARKS)
above    = count_above_average(MARKS, average)
grades   = grade_distribution(MARKS)

print("=" * 35)
print("   STUDENT SCORE ANALYZER")
print("=" * 35)
print(f"Marks         : {MARKS}")
print(f"Average Score : {average:.2f}")
print(f"Highest Score : {highest}")
print(f"Lowest Score  : {lowest}")
print(f"Above Average : {above} student(s)")
print("-" * 35)
print("Grade Distribution:")
for grade, count in grades.items():
    print(f"  {grade:<6}: {count} student(s)")
print("=" * 35)