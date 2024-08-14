from datetime import datetime
import hashlib
import shortuuid
import sqlite3

class Expense:
    def __init__(self, userId, amount_input, categry_input,description_input=None, date_input="None"):
        self.user_id = userId
        self.amount = amount_input
        self.category = categry_input
        self.date = date_input
        self.description = description_input
    
    @classmethod
    def addExpense(self,user_id_input, amount_input, category_input,description_input, date_input,cursor,conn):
        try:
            cursor.execute('''
            INSERT INTO EXPENSES 
            (user_id, amount, category, date, description)
            VALUES (?, ?, ?, ?, ?) ''',
            (user_id_input, amount_input, category_input, date_input, description_input))
        except sqlite3.Error as e:
            print(f"An error occurred: {e}\n")
        else:
            conn.commit()
            print("\nExpense added successfull.\n")

    @classmethod
    def getExpenses(cls, user_id_input,cursor,conn):
        try:
            cursor.execute('''
                SELECT * FROM EXPENSES WHERE user_id = ?''',
                (user_id_input,)
            )
        except sqlite3.Error as e:
            print(f"\nAn error occurred: {e}")
        else:
            conn.commit()
            return [Expense(user_id_input, *row[1:]) for row in cursor.fetchall()]

    @classmethod
    def editExpense(cls,user_id_input, amount_new, amount_old, date_input,cursor,conn):
        try:
            cursor.execute(''' 
            UPDATE EXPENSES SET amount=(?) WHERE  (user_id=(?) AND amount=(?) AND date=(?))''',
            (amount_new,user_id_input,amount_old,date_input))
        except sqlite3.Error as e:
            print(f"\nAn error occurred: {e}")
        else:
            conn.commit()
            print(f"\nAmount updated to: {amount_new}\n")
    
    @classmethod
    def deleteExpense(cls,user_id,amount_input,date_input,cursor,conn):
        try:
            cursor.execute('''
            DELETE FROM EXPENSES WHERE  (user_id=(?) AND amount=(?) AND date=(?))''',
            (user_id,amount_input,date_input))
        except sqlite3.Error as e:
            print(f"\nAn error occurred: {e}")
        else:
            conn.commit()
            print(f"\nSuccessfully deleted record, Amount = {amount_input} on date = {date_input}\n")

class Income:
    def __init__(self, userId, amount_input,description_input=None,date_input="None"):
        self.user_id = userId
        self.amount = amount_input   
        self.date = date_input
        self.description = description_input

    @classmethod
    def addIncome(cls,user_id_input, amount_input,  date_input, description_input,cursor,conn):
        try:
            cursor.execute('''
            INSERT INTO INCOME 
            (user_id, amount, date, description)
            VALUES (?, ?, ?, ?) ''',
            (user_id_input, amount_input, date_input, description_input))
        except sqlite3.Error as e:
            print(f"\nAn error occurred: {e}")
        else:
            conn.commit()
            print("\nIncome added successfull.\n")

    @classmethod
    def getIncome(cls, user_id_input,cursor,conn):
        try:
            cursor.execute('''
                SELECT * FROM INCOME WHERE user_id = ?''',
                (user_id_input,)
            )
        except sqlite3.Error as e:
            print(f"\nAn error occurred: {e}")
        else:
            conn.commit()
            return [cls(user_id_input, *row[1:]) for row in cursor.fetchall()]
        
    @classmethod
    def editIncome(cls,user_id_input, amount_new, amount_old, date_input,cursor,conn):
        try:
            cursor.execute(''' 
            UPDATE INCOME SET amount=(?) WHERE  (user_id=(?) AND amount=(?) AND date=(?))''',
            (amount_new,user_id_input,amount_old,date_input))
        except sqlite3.Error as e:
            print(f"\nAn error occurred: {e}")
        else:
            conn.commit()
            print(f"\nIncome updated to: {amount_new}\n")
    
    @classmethod
    def deleteIncome(cls,user_id_input,amount_input,date_input,cursor,conn):
        try:
            cursor.execute('''
            DELETE FROM INCOME WHERE  (user_id=(?) AND amount=(?) AND date=(?))''',
            (user_id_input,amount_input,date_input))
        except sqlite3.Error as e:
            print(f"\nAn error occurred: {e}")
        else:
            conn.commit()
            print(f"\nSuccessfully deleted income record, Amount = {amount_input} on date = {date_input}\n")

class User:
    def __init__(self, username_input, password_input):
        self.username = username_input
        self.password = self.hash_password(password_input)
        self.user_id = shortuuid.uuid()

    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()

    @classmethod
    def createUser(cls, username_input, password_input,cursor,conn):
        user_one = cls(username_input.lower(), password_input)
        try:
            cursor.execute('''
                INSERT INTO USER (user_id, username, password) VALUES (?,?,?)''',
                (user_one.user_id, user_one.username, user_one.password))
        except sqlite3.Error as e:
            print(f"\nAn error occurred: {e}")
        else:
            conn.commit()
            print(f"\n{user_one.username} successfully created.\n")

    @classmethod
    def loginUser(cls,username_input,password_input,cursor):
        try:
            cursor.execute('''
                SELECT password FROM USER WHERE username=(?)''',
                (username_input.lower(),))
            password_actual = cursor.fetchone()
        except sqlite3.Error as e:
            print(f"\nAn error occurred: {e}")
        else:
            password_hashed = cls.hash_password(password_input)
            if password_hashed == password_actual[0]:
                cursor.execute('''
                SELECT user_id FROM USER WHERE username=? AND password=?''',
                (username_input,password_hashed,))
                userID = cursor.fetchone()
                return userID[0]
            else:
                print("\nWrong Password.")
                return -1

    @classmethod
    def deleteUser(cls,username_input,password_input,cursor,conn):
        try:
            cursor.execute('''
            SELECT password FROM USER WHERE username=(?)''',
            (username_input.lower(),))
            password_actual = cursor.fetchone()
            password_hashed = cls.hash_password(password_input)
            if password_hashed == password_actual[0]:
                cursor.execute('''
                    SELECT user_id FROM USER WHERE username=? AND password=(?)''',
                    (username_input,password_actual[0],))
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
            else:
                print("\nWrong Password.")
                return -1
        except sqlite3.Error as e:
            print(f"\nAn error occurred: {e}")
        else:
            conn.commit()
            print(f"\nUser {username_input} deleted successfully.")