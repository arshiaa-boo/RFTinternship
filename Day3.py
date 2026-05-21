# Project 3 - Dictionary-Based Phonebook
# GOW AI Academy - Python Internship Day 3

# ── Initial Phonebook Data ───────────────────────────────
phonebook = {
    "AMIT": "9876543210",
    "RIYA": "9123456780"
}

# ── Core Functions ───────────────────────────────────────

def add_contact(name, number):
    name = name.upper()
    if name in phonebook:
        print(f" '{name}' already exists! Use update option.")
    else:
        phonebook[name] = number
        print(f" Contact '{name}' added successfully!")

def search_contact(name):
    name = name.upper()
    # Exact match
    if name in phonebook:
        print(f" Found: {name} → {phonebook[name]}")
    else:
        # Bonus: Partial name search
        results = {k: v for k, v in phonebook.items() if name in k}
        if results:
            print(f"🔍 Partial matches for '{name}':")
            for k, v in results.items():
                print(f"   {k} → {v}")
        else:
            print(f" No contact found for '{name}'")

def delete_contact(name):
    name = name.upper()
    if name in phonebook:
        del phonebook[name]
        print(f"  Contact '{name}' deleted successfully!")
    else:
        print(f" Contact '{name}' not found!")

def view_all():
    if not phonebook:
        print(" Phonebook is empty!")
    else:
        print("\n All Contacts:")
        print("-" * 30)
        for name, number in sorted(phonebook.items()):
            print(f"  {name:<15} → {number}")
        print("-" * 30)

# ── Menu ─────────────────────────────────────────────────

def menu():
    while True:
        print("\n╔══════════════════════════╗")
        print("║      📱 PHONEBOOK        ║")
        print("╠══════════════════════════╣")
        print("║  1. View All Contacts    ║")
        print("║  2. Add Contact          ║")
        print("║  3. Search Contact       ║")
        print("║  4. Delete Contact       ║")
        print("║  5. Exit                 ║")
        print("╚══════════════════════════╝")

        choice = input("Enter your choice (1-5): ")

        if choice == "1":
            view_all()

        elif choice == "2":
            name   = input("Enter name   : ").strip()
            number = input("Enter number : ").strip()
            add_contact(name, number)

        elif choice == "3":
            name = input("Enter name to search: ").strip()
            search_contact(name)

        elif choice == "4":
            name = input("Enter name to delete: ").strip()
            delete_contact(name)

        elif choice == "5":
            print(" Goodbye!")
            break

        else:
            print("  Invalid choice! Enter 1-5.")
menu()