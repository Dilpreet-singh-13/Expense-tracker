import sqlite3
import os
from datetime import datetime
from classes import Expense, Income, User
from utils import validate_date
from database import create_tables

def adminMenu(cursor,conn):
    while True:
        print(f"\nAdmin Menu\n{'1. List all users':<20} {'3. Delete user':^25}\n{'2. Clear all data':<20} {'4. Logout admin':^25}")
        option = int(input("Enter your option: "))
        match option:
            case 1:
                try:
                    cursor.execute('''
                    SELECT username FROM USER'''
                    )
                except sqlite3.Error as e:
                    print(f"An error occurred: {e}")
                else:
                    all_users = cursor.fetchone()
                    if all_users:
                        print("\nAll users - ")
                        for user in all_users:
                            print(f"{user} ")
                    else:
                        print("No users.\n")
            case 2:
                ack = input("All the data will be permanently deleted.\nDo you still want to continue? (y/n) : ")
                if ack.lower() == 'y':
                    try:
                        cursor.execute('''
                            DELETE FROM USER
                        ''')
                        cursor.execute('''
                            DELETE FROM EXPENSES
                        ''')
                        cursor.execute('''
                            DELETE FROM INCOME
                        ''')
                    except sqlite3.Error as e:
                        print(f"An error occurred: {e}")
                    else:
                        conn.commit()
                        print("Data deleted successfully.\n")

            case 3:
                userDel = input("Enter username to delete: ")
                cursor.execute('''SELECT COUNT(*) FROM USER WHERE username = ?''', (userDel,))
                result = cursor.fetchone()
                if result[0] > 0:
                    try:
                        cursor.execute('''
                            SELECT user_id FROM USER WHERE username=?''',
                        (userDel,))
                        userID = cursor.fetchone()
                        cursor.execute('''
                            DELETE FROM USER WHERE user_id=?''',
                        (userID[0],))
                        cursor.execute('''
                            DELETE FROM EXPENSES WHERE user_id=(?)''',
                        (userID[0],))
                        cursor.execute('''
                            DELETE FROM INCOME WHERE user_id=(?)''',
                        (userID[0],))
                    except sqlite3.Error as e:
                        print(f"An error occurred: {e}")
                    else:
                        conn.commit()
                        print(f"User {userDel} deleted successfully.")

                else:
                    print("No such user exists.\n")
                    continue
            case 4:
                return
            case _:
                print("Invalid option.\n")

def userMenu(username, user_id, cursor, conn):
    while True:
        print(f"\n{'EXPENSES':<25} {'INCOME':<25} {'SEARCH':<25}   {'OTHERS':<25}")
        print(f"1. Add expense           {'6. Add income':<25} {'11. Search expenses by dates':<25} {'14. Delete user':<25}")
        print(f"2. Edit expense          {'7. Edit income':<25} {'12. Search income by dates':<25}   {'15. Logout':<25}")
        print(f"3. Delete expense        {'8. Delete income':<25} {'13. Saving between dates':<25}")
        print(f"4. View expense records  {'9. View income records':<25}")
        print(f"5. Total expenditure     {'10. Total income':<25}")
        option_2 = int(input("Enter your option: "))

        match option_2:
            case 1:
                #Add expense
                amount = float(input("\nEnter amount: "))
                category = input("Category should be one of - food, entertainment, transport, academics, other\nEnter category: ")
                description = input("Enter description (optional): ")
                date_input = input("Enter date in format YYYY-MM-DD, if empty it takes the current date: ")

                if not date_input:
                    date_input = datetime.today()
                    date_input = date_input.strftime("%Y-%m-%d")
                else:
                    result = validate_date(date_input)
                    if not result:
                        continue

                Expense.addExpense(user_id, amount, category, description, date_input, cursor, conn)
            case 2:
                #Edit expense
                amount_old = float(input("\nAdd old amount: "))
                amount_new = float(input("Add new amount: "))
                date_input = input("Enter date in format YYYY-MM-DD: ")
                if not date_input:
                    date_input = datetime.today()
                    date_input = date_input.strftime("%Y-%m-%d")
                else:
                    result = validate_date(date_input)
                    if not result:
                        continue

                cursor.execute('''
                    SELECT COUNT(*) FROM EXPENSES WHERE amount=? AND date=?''',
                (amount_old,date_input))
                count = cursor.fetchone()

                if count[0]:
                    Expense.editExpense(user_id, amount_new, amount_old, date_input, cursor, conn)
                else:
                    print("Amount and date don't match the records.\n")
            case 3:
                #delete expense
                amount = float(input("\nEnter amount: "))
                date_input = input("Enter date in format YYYY-MM-DD: ")
                if not date_input:
                    date_input = datetime.today()
                    date_input = date_input.strftime("%Y-%m-%d")
                else:
                    result = validate_date(date_input)
                    if not result:
                        continue

                cursor.execute('''
                    SELECT COUNT(*) FROM EXPENSES WHERE amount=? AND date=?''',
                (amount,date_input))
                count = cursor.fetchone()

                if count[0]:
                    Expense.deleteExpense(user_id, amount, date_input, cursor, conn)
                else:
                    print("Amount and date don't match the records.\n")
            case 4:
                #view all expense records
                user_expenses = Expense.getExpenses(user_id, cursor, conn)
                if user_expenses:
                    print(*('-' for i in range(25)))
                    print("Amount\tDate\t\tCategory\tDescription\t")
                    for expense in user_expenses:
                        print(f"{expense.amount}\t{expense.date}\t{expense.category}\t\t{expense.description}")
                    print(*('-' for i in range(25)))
                else:
                    print("No expenses found for this user.")
            case 5:
                #Total expenditure
                cursor.execute('''
                    SELECT SUM(amount) FROM EXPENSES WHERE user_id=?''',
                    (user_id,))
                amount = cursor.fetchone()
                if amount:
                    print(f"\nTotal expenses: {amount[0]}\n")
                else:
                    print("\nNo enpense record for this user.\n")
            case 6:
                #Add income
                amount = float(input("\nEnter amount: "))
                description = input("Enter description (optional): ")
                date_input = input("Enter date in format YYYY-MM-DD,if left empty it takes the current date: ")
                
                if not date_input:
                    date_input = datetime.today()
                    date_input = date_input.strftime("%Y-%m-%d")
                else:
                    result = validate_date(date_input)
                    if not result:
                        continue

                Income.addIncome(user_id, amount, date_input, description, cursor, conn)
            case 7:
                #edit income
                amount_old = float(input("\nAdd old amount: "))
                amount_new = float(input("Add new amount: "))
                date_input = input("Enter date in format YYYY-MM-DD: ")
                if not date_input:
                    date_input = datetime.today()
                    date_input = date_input.strftime("%Y-%m-%d")
                else:
                    result = validate_date(date_input)
                    if not result:
                        continue

                cursor.execute('''
                    SELECT COUNT(*) FROM INCOME WHERE amount=? AND date=?''',
                (amount_old,date_input))
                count = cursor.fetchone()

                if count[0]:
                    Income.editIncome(user_id, amount_new, amount_old, date_input, cursor, conn)
                else:
                    print("Amount and date don't match the records.\n")
            case 8:
                #delete income
                amount = float(input("\nEnter amount: "))
                date_input = input("Enter date in format YYYY-MM-DD: ")
                if not date_input:
                    date_input = datetime.today()
                    date_input = date_input.strftime("%Y-%m-%d")
                else:
                    result = validate_date(date_input)
                    if not result:
                        continue
                
                cursor.execute('''
                    SELECT COUNT(*) FROM INCOME WHERE amount=? AND date=?''',
                (amount,date_input))
                count = cursor.fetchone()

                if count[0]:
                    Income.deleteIncome(user_id, amount, date_input, cursor, conn)
                else:
                    print("Amount and date don't match the records.\n")
            case 9:
                #view income records
                user_income = Income.getIncome(user_id, cursor, conn)
                if user_income:
                    print(*('-' for i in range(25)))
                    print("Amount\tDate\t\tDescription\t")
                    for income in user_income:
                        print(f"{income.amount}\t{income.date}\t{income.description}")
                    print(*('-' for i in range(25)))
                else:
                    print("No income found for this user.\n")
            case 10:
                #total income
                cursor.execute('''
                    SELECT SUM(amount) FROM INCOME WHERE user_id=?''',
                    (user_id,))
                amount = cursor.fetchone()
                if amount:
                    print(f"\nTotal income: {amount[0]}\n")
                else:
                    print("\nNo income record for this user.\n")
            case 11:
                print("If date is left empty, it takes the current date by default. Fill atleast 1 date.\nDATE FORMAT - YYYY-MM-DD.")
                start_date = input("Enter date 1: ")
                end_date = input("Enter date 2: ")

                if not start_date:
                    start_date = datetime.today()
                    start_date = start_date.strftime("%Y-%m-%d")
                elif not end_date:
                    end_date = datetime.today()
                    end_date = end_date.strftime("%Y-%m-%d")
                else:
                    result = validate_date(start_date)
                    result_2 = validate_date(end_date)
                    if (not result) or (not result_2):
                        continue
                
                cursor.execute('''
                    SELECT * FROM EXPENSES WHERE user_id = ? AND date BETWEEN ? AND ?
                    ''',(user_id, start_date, end_date))
                income_all = cursor.fetchall()
                if income_all:
                    print(*('-' for i in range(25)))
                    print("Amount\tDate\t\tCategory\tDescription\t")
                    for expense in income_all:
                        print(f"{expense[1]}\t{expense[2]}\t{expense[3]}\t\t{expense[4]}")
                    print(*('-' for i in range(25)))
                else:
                    print("No expenses found for this user.")
            case 12:
                print("If date is left empty, it takes the current date by default. Fill atleast 1 date.\nDATE FORMAT - YYYY-MM-DD.")
                start_date = input("Enter date 1: ")
                end_date = input("Enter date 2: ")

                if not start_date:
                    start_date = datetime.today()
                    start_date = start_date.strftime("%Y-%m-%d")
                elif not end_date:
                    end_date = datetime.today()
                    end_date = end_date.strftime("%Y-%m-%d")
                else:
                    result = validate_date(start_date)
                    result_2 = validate_date(end_date)
                    if (not result) or (not result_2):
                        continue
                
                cursor.execute('''
                    SELECT * FROM INCOME WHERE user_id = ? AND date BETWEEN ? AND ?
                    ''',(user_id, start_date, end_date))
                income_all = cursor.fetchall()
                if income_all:
                    print(*('-' for i in range(25)))
                    print("Amount\tDate\t\tDescription\t")
                    for income in income_all:
                        print(f"{income[1]}\t{income[2]}\t{income[3]}")
                    print(*('-' for i in range(25)))
                else:
                    print("\nNo income found for this user.\n")
            case 13:
                print("If date is left empty, it takes the current date by default. Fill atleast 1 date.\nDATE FORMAT - YYYY-MM-DD.")
                start_date = input("Enter date 1: ")
                end_date = input("Enter date 2: ")

                if not start_date:
                    start_date = datetime.today()
                    start_date = start_date.strftime("%Y-%m-%d")
                elif not end_date:
                    end_date = datetime.today()
                    end_date = end_date.strftime("%Y-%m-%d")
                else:
                    result = validate_date(start_date)
                    result_2 = validate_date(end_date)
                    if (not result) or (not result_2):
                        continue
                
                cursor.execute('''
                    SELECT SUM(amount) FROM EXPENSES WHERE user_id = ? AND date BETWEEN ? AND ?
                    ''',(user_id, start_date, end_date))
                expenses_total = cursor.fetchone()
                cursor.execute('''
                    SELECT SUM(amount) FROM INCOME WHERE user_id = ? AND date BETWEEN ? AND ?
                    ''',(user_id, start_date, end_date))
                income_total = cursor.fetchone()
                if expenses_total[0]:
                    if income_total[0]:
                        saving = income_total[0] - expenses_total[0]
                        print(f"\nSaving = {saving}\n")
                    else:
                        print(f"\nNo income between {start_date} and {end_date}.\nTotal expenditure between these dates = {expenses_total[0]}\n")
                elif (not expenses_total[0]) and (not income_total):
                    print("No expense and income records for this user.")
                else:
                    print(f"\nNo expense between {start_date} and {end_date}.\nTotal income between these dates = {income_total[0]}")
            case 14:
                print(f"Deleting user {username}")
                password = input("Enter password: ")

                if not password:
                    print("Username or password can't be empty.\n")
                    continue

                print("\nAll the user data will be deleted permanently.")
                ack = input("Do you still wish to delete this user? ")
                if ack.lower() == "yes" or ack.lower() == "y":
                    User.deleteUser(username, password, cursor,conn)
                return
            case 15:
                return
            case _:
                print("Invalid option.\n")

def main():
    db_path = os.path.join(os.path.dirname(__file__), 'expense_tracker.db')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    create_tables(cursor)

    try:
        cursor.execute('''
        SELECT COUNT(*) FROM ADMIN'''
        )
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    else:
        if cursor.fetchone()[0] == 0:
            print("You seem new here. Setup a admin password to start using the expense tracker.")
            password_input = input("Enter new admin password: ")
            password = User.hash_password(password_input)

            cursor.execute('''
            INSERT INTO ADMIN (sno, password) VALUES (?, ?)''',
            (1, password))
            conn.commit()

    while True:
        print(f"\nMENU")
        print(f"1. {'Create user':<20} {'3. Admin Login':^15}")
        print(f"2. {'Login user':<20}{'4. Exit':^10}")

        option = int(input("Enter you option: "))
        match option:
            case 1:
                username = input("\nEnter new username: ")
                password = input("Enter new password: ")

                if (not username) or (not password):
                    print("Username or password can't be empty.\n")
                    continue
                
                User.createUser(username,password,cursor,conn)
            case 2:
                username = input("\nEnter username: ").lower()
                cursor.execute('''SELECT COUNT(*) FROM USER WHERE username = ?''', (username,))
                result = cursor.fetchone()
                
                if result[0] > 0:
                    password = input("Enter password: ")
                else:
                    print("No such user exists.\n")
                    continue

                if (not username) or (not password):
                    print("Username or password can't be empty.\n")
                    continue
                
                user_id = User.loginUser(username, password, cursor)
                userMenu(username, user_id,cursor,conn)
            case 3:
                password = input("Enter admin password: ")
                password_hash = User.hash_password(password)

                cursor.execute('''
                    SELECT password FROM ADMIN WHERE sno = ?''', (1,)
                )
                password_actual = cursor.fetchone()
                if password_actual[0] == password_hash:
                    print("\nAdmin login successfull.\n")
                    adminMenu(cursor, conn)
                else:
                    print("Incorrect password.")
                    continue
            case 4:
                try:
                    conn.commit()
                    conn.close()
                except sqlite3.Error as e:
                    print(f"An error occurred: {e}")
                else:
                    print("\nConnection closed.")
                    return
            case _:
                print("Invalid option.\n")

if __name__ == "__main__":
    main()