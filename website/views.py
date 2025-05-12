from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask import make_response
from flask import send_file
from jinja2 import Template
from flask_login import login_required, current_user
from .models import Expense, Budget, Savings
from . import db
import io
import pdfkit
import tempfile
import json
import csv
from io import StringIO
from flask import Response
from datetime import datetime

views = Blueprint('views', __name__)
 
@views.route('/export_csv')
@login_required
def export_csv():
    expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).all()

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Date', 'Time', 'Category', 'Amount'])

    for expense in expenses:
        writer.writerow([expense.date.strftime('%Y-%m-%d'), expense.date.strftime('%H:%M:%S'), expense.category, expense.amount])
    
    output.seek(0)
    return Response(output, mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=expenses.csv"})

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    from datetime import datetime
    from collections import defaultdict


    # ✅ Set date/time variables once, used across logic
    
    current_month = datetime.now().strftime("%B")          # for budget
    current_year = datetime.now().year

    # 🟨 Handle POST requests (form submissions)
    if request.method == 'POST':
        # --- Expense Form Submission ---
        if 'expense_amount' in request.form:
            amount = float(request.form['expense_amount'])
            category = request.form.get('category')
            custom_category = request.form.get('custom_category')

            if category == 'Others' and custom_category:
                category = custom_category.strip()

            budget = Budget.query.filter_by(user_id=current_user.id, month=current_month, year=current_year).first()
            budget_amount = budget.amount if budget else 0

            savings = Savings.query.filter_by(user_id=current_user.id, month=f"{current_month} {current_year}").first()
            savings_amount = savings.amount if savings else 0.0

            # Calculate total existing expenses
            all_expenses = Expense.query.filter_by(user_id=current_user.id).all()
            total_existing_expenses = sum(e.amount for e in all_expenses)

            new_total_expenses = total_existing_expenses + amount
            excess = new_total_expenses - budget_amount

            if budget_amount >= new_total_expenses:
                # Budget covers everything
                new_expense = Expense(user_id=current_user.id, category=category, amount=amount)
                db.session.add(new_expense)
                db.session.commit()
                flash('Expense added successfully!', category='success')

            elif budget_amount < new_total_expenses and (budget_amount + savings_amount) >= new_total_expenses:
                # Need to use savings
                excess = new_total_expenses - budget_amount
                savings.amount -= excess

                new_expense = Expense(user_id=current_user.id, category=category, amount=amount)
                db.session.add(new_expense)
                db.session.commit()
                flash(f'Your expense exceeded the budget by ₱{excess:.2f}, which was deducted from your savings.', category='warning')

            else:
                flash('Your monthly budget and savings are not enough to cover this expense.', category='error')
                return redirect('/')

                
            return redirect('/')
        
        elif 'savings_amount' in request.form:
            amount = float(request.form['savings_amount'])
            savings_month = f"{current_month} {current_year}"

            savings = Savings.query.filter_by(user_id=current_user.id, month=savings_month).first()

            if savings:
                savings.amount += amount
            else:
                savings = Savings(user_id=current_user.id, amount=amount, month=savings_month)
                db.session.add(savings)

            db.session.commit()
            flash('Savings added successfully!', category='success')
            return redirect('/')
    
    expenses = Expense.query.filter_by(user_id=current_user.id).all()
    total_expenses = sum(e.amount for e in expenses)
    savings = Savings.query.filter_by(user_id=current_user.id, month=f"{current_month} {current_year}").first()
    savings_amount = savings.amount if savings else 0.0

    budget = Budget.query.filter_by(user_id=current_user.id, month=current_month, year=current_year).first()
    budget_amount = budget.amount if budget else 0

    remaining_budget = budget_amount - total_expenses
    if remaining_budget < 0:
        remaining_budget = 0


    # Expense summary by category for chart
    summary = {}
    for expense in expenses:
        summary[expense.category] = summary.get(expense.category, 0) + expense.amount

    # Group expenses by day
    grouped_expenses = defaultdict(list)
    for expense in expenses:
        date_str = expense.date.strftime('%Y-%m-%d')
        grouped_expenses[date_str].append(expense)

    # Calculate percentage per day
    percentage_by_day = {}
    for date, exps in grouped_expenses.items():
        daily_total = sum(e.amount for e in exps)
        percentage = (daily_total / total_expenses) * 100 if total_expenses > 0 else 0
        percentage_by_day[date] = round(percentage, 2)

    return render_template(
        "home.html",
        user=current_user,
        expenses=expenses,
        summary=summary,
        total_expenses=total_expenses,
        budget_amount=budget_amount,
        savings=savings_amount,
        remaining_budget=remaining_budget,
        current_month=current_month,
        summary_json=json.dumps(summary),
        grouped_expenses=grouped_expenses,
        percentage_by_day=percentage_by_day
    )


@views.route('/report')
@login_required
def report():
    # Get all expenses for current user
    expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).all()

    # Group expenses by date (formatted as YYYY-MM-DD)
    from collections import defaultdict
    from datetime import datetime

    grouped_expenses = defaultdict(list)
    total_expenses = 0
    for expense in expenses:
        date_str = expense.date.strftime('%Y-%m-%d')
        grouped_expenses[date_str].append(expense)
        total_expenses += expense.amount
    
    # Calculate percentage per date
    percentage_by_day = {}
    for date, exps in grouped_expenses.items():
        daily_total = sum(e.amount for e in exps)
        percentage = (daily_total / total_expenses) * 100 if total_expenses > 0 else 0
        percentage_by_day[date] = round(percentage, 2)

    return render_template("report.html", user=current_user, grouped_expenses=grouped_expenses, percentage_by_day=percentage_by_day, total_expenses=total_expenses)    
 
@views.route('/download_report')
@login_required
def download_report():
    from datetime import datetime

    now = datetime.now()
    current_month = now.strftime("%B")
    current_year = now.year

    # Fetch data
    expenses = Expense.query.filter_by(user_id=current_user.id).all()
    savings = Savings.query.filter_by(user_id=current_user.id, month=f"{current_month} {current_year}").first()
    savings_amount = savings.amount if savings else 0.0

    budget = Budget.query.filter_by(user_id=current_user.id, month=current_month, year=current_year).first()
    budget_amount = budget.amount if budget else 0.0

    total_expenses = sum(e.amount for e in expenses)

    # Calculate how much of the savings was used
    used_savings = max(0, total_expenses - budget_amount)

    # Prepare the HTML receipt template
    rendered = render_template("pdf_receipt.html",
                                    user=current_user,
                                    expenses=expenses,
                                    total_expenses=total_expenses,
                                    budget_amount=budget_amount,
                                    used_savings=used_savings,
                                    savings_remaining=savings_amount,
                                    now=now)
    
    # Set path to wkhtmltopdf binary
    config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')

    # Create temporary PDF file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
        pdfkit.from_string(rendered, f.name, configuration=config)
        return send_file(f.name, as_attachment=True, download_name='Expenses_Report.pdf')



@views.route('/reset', methods=['POST'])
@login_required
def reset_budget():
    from datetime import datetime

    current_month = datetime.now().strftime('%B')
    current_year = datetime.now().year
    savings_month = f"{current_month} {current_year}"

    # Delete budget entry for current month
    budget = Budget.query.filter_by(user_id=current_user.id, month=current_month, year=current_year).first()
    if budget:
        db.session.delete(budget)

    # Delete savings entry for current month
    savings = Savings.query.filter_by(user_id=current_user.id, month=savings_month).first()
    if savings:
        db.session.delete(savings)

    db.session.commit()
    flash('Budget and savings reset successfully!', category='success')
    return redirect(url_for('views.home'))


@views.route('/set-budget', methods=['POST'])
@login_required
def set_budget():
    try:
        amount = float(request.form.get('budget'))
        if amount <= 0:
            flash('Budget must be greater than 0.', category='error')
            return redirect(url_for('views.home'))

        current_month = datetime.now().strftime('%B')
        current_year = datetime.now().year
    
        existing_budget = Budget.query.filter_by(
            user_id=current_user.id,
            month=current_month,
            year=current_year
        ).first()

        if existing_budget:
            existing_budget.amount = amount
        else:
            new_budget = Budget(
                amount=amount,
                month=current_month,
                year=current_year,
                user_id=current_user.id
            )
            db.session.add(new_budget)

        db.session.commit()
        flash('Monthly budget set/updated successfully!', category='success')

    except ValueError:
        flash('Invalid budget amount entered.', category='error')
    return redirect(url_for('views.home'))