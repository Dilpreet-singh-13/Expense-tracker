from datetime import datetime

def validate_date(date):
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_date_obj = datetime.strptime(current_date, "%Y-%m-%d")
        
        if date_obj > current_date_obj:
            print("The date cannot be in the future.")
            return False
        
        return True
    except ValueError:
        print("Invalid date format or non-existent date.")
        return False