<<<<<<< HEAD
from . import db
from .models import Expense, Budget

# Helper function to initialize the database
def create_database():
    db.create_all()

# Function to get monthly expenses summary
def get_expenses_summary(user_id, month, year):
    expenses = Expense.query.filter_by(user_id=user_id).all()
    summary = {}
    for expense in expenses:
        category = expense.category
        summary[category] = summary.get(category, 0) + expense.amount
    return summary
=======
from . import db
from .models import Expense, Budget

# Helper function to initialize the database
def create_database():
    db.create_all()

# Function to get monthly expenses summary
def get_expenses_summary(user_id, month, year):
    expenses = Expense.query.filter_by(user_id=user_id).all()
    summary = {}
    for expense in expenses:
        category = expense.category
        summary[category] = summary.get(category, 0) + expense.amount
    return summary
>>>>>>> 11087191ba6c9c67c5ba75a139af05d657e2bf97
