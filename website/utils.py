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
