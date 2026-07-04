"""
Expense Tracker
A command-line app to log, view, and analyze personal expenses.
Uses Python's built-in sqlite3 module — no external packages needed.
"""

import sqlite3
from datetime import datetime

DB_FILE = "expenses.db"


def get_connection():
    """Open a connection to the SQLite database (creates the file if it doesn't exist)."""
    return sqlite3.connect(DB_FILE)


def setup_database():
    """Create the expenses table if it doesn't already exist."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            date TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def add_expense():
    """Prompt the user for expense details and save it to the database."""
    print("\n--- Add New Expense ---")

    # Validate amount is a real number
    while True:
        amount_str = input("Amount (e.g. 12.50): ").strip()
        try:
            amount = float(amount_str)
            if amount <= 0:
                print("Amount must be greater than 0.")
                continue
            break
        except ValueError:
            print("Please enter a valid number.")

    category = input("Category (e.g. Food, Rent, Travel): ").strip().title()
    if not category:
        category = "Uncategorized"

    description = input("Description (optional): ").strip()
    date = datetime.now().strftime("%Y-%m-%d")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO expenses (amount, category, description, date) VALUES (?, ?, ?, ?)",
        (amount, category, description, date)
    )
    conn.commit()
    conn.close()

    print(f"✅ Added: ${amount:.2f} in '{category}' on {date}")


def view_expenses():
    """Show every expense recorded, newest first."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, amount, category, description, date FROM expenses ORDER BY date DESC, id DESC")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("\nNo expenses recorded yet.")
        return

    print("\n--- All Expenses ---")
    print(f"{'ID':<4} {'Date':<12} {'Category':<15} {'Amount':<10} {'Description'}")
    print("-" * 60)
    for row in rows:
        exp_id, amount, category, description, date = row
        print(f"{exp_id:<4} {date:<12} {category:<15} ${amount:<9.2f} {description or ''}")


def view_summary():
    """Show total spending and a breakdown by category."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(amount) FROM expenses")
    total = cursor.fetchone()[0] or 0

    cursor.execute("""
        SELECT category, SUM(amount) as cat_total
        FROM expenses
        GROUP BY category
        ORDER BY cat_total DESC
    """)
    by_category = cursor.fetchall()
    conn.close()

    print("\n--- Spending Summary ---")
    print(f"Total spent: ${total:.2f}\n")

    if not by_category:
        print("No data to summarize yet.")
        return

    print(f"{'Category':<15} {'Amount':<10} {'% of Total'}")
    print("-" * 40)
    for category, cat_total in by_category:
        percent = (cat_total / total * 100) if total else 0
        bar = "█" * int(percent / 5)  # simple text bar chart, 1 block per 5%
        print(f"{category:<15} ${cat_total:<9.2f} {percent:5.1f}%  {bar}")


def delete_expense():
    """Delete an expense by its ID."""
    view_expenses()
    conn = get_connection()
    cursor = conn.cursor()

    id_str = input("\nEnter the ID of the expense to delete (or 'c' to cancel): ").strip()
    if id_str.lower() == 'c':
        return

    try:
        exp_id = int(id_str)
    except ValueError:
        print("Invalid ID.")
        conn.close()
        return

    cursor.execute("SELECT id FROM expenses WHERE id = ?", (exp_id,))
    if not cursor.fetchone():
        print(f"No expense found with ID {exp_id}.")
        conn.close()
        return

    cursor.execute("DELETE FROM expenses WHERE id = ?", (exp_id,))
    conn.commit()
    conn.close()
    print(f"🗑️  Deleted expense with ID {exp_id}.")


def main_menu():
    """The main loop that shows options and routes to the right function."""
    setup_database()

    while True:
        print("\n===== Expense Tracker =====")
        print("1. Add expense")
        print("2. View all expenses")
        print("3. View summary by category")
        print("4. Delete an expense")
        print("5. Exit")

        choice = input("Choose an option (1-5): ").strip()

        if choice == "1":
            add_expense()
        elif choice == "2":
            view_expenses()
        elif choice == "3":
            view_summary()
        elif choice == "4":
            delete_expense()
        elif choice == "5":
            print("Goodbye! 👋")
            break
        else:
            print("Please enter a number from 1 to 5.")


if __name__ == "__main__":
    main_menu()