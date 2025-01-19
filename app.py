from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
import csv
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)

# Save expenses function
def save_expenses(expenses, filename='expenses.csv'):
    with open(filename, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['category', 'amount', 'date'])
        writer.writeheader()
        writer.writerows(expenses)
    print("Expenses saved to file.")

# Load expenses function
def load_expenses(filename='expenses.csv'):
    try:
        with open(filename, 'r') as file:
            reader = csv.DictReader(file)
            # Convert amount to float for proper handling
            return [
                {'category': row['category'], 'amount': float(row['amount']), 'date': row['date']}
                for row in reader
            ]
    except FileNotFoundError:
        return []

# Route for the homepage
@app.route('/', methods=['GET', 'POST'])
def home():
    expenses = load_expenses()

    if request.method == 'POST':  # Handle the form submission
        category = request.form['category']
        try:
            amount = float(request.form['amount'])
        except ValueError:
            amount = 0.0  # Default to 0.0 if conversion fails
        date = request.form['date'] or datetime.now().strftime('%Y-%m-%d')  # Default to today if no date provided
        expenses.append({'category': category, 'amount': amount, 'date': date})
        save_expenses(expenses)  # Save the updated expenses to the CSV file
        return redirect(url_for('home'))  # Redirect to the homepage to view updated expenses

    return render_template('index.html', expenses=expenses)

# Route to download the CSV file
@app.route('/download')
def download_file():
    return send_file('expenses.csv', as_attachment=True)

# Route to provide expenses as JSON for dynamic loading
@app.route('/expenses')
def get_expenses():
    expenses = load_expenses()
    return jsonify(expenses)

# Route to return grouped expenses based on category or date
@app.route('/grouped_expenses')
def grouped_expenses():
    group_by = request.args.get('groupBy', 'none')  # Default to 'none'

    expenses = load_expenses()

    grouped_data = defaultdict(float)  # Using defaultdict to simplify sum logic

    if group_by == 'category':
        # Group expenses by category
        for expense in expenses:
            grouped_data[expense['category']] += expense['amount']
    elif group_by == 'date':
        # Group expenses by date
        for expense in expenses:
            grouped_data[expense['date']] += expense['amount']

    # Prepare data to send to the frontend
    grouped_expenses = [{'category': key, 'amount': value} for key, value in grouped_data.items()]

    return jsonify(grouped_expenses)

# Route to handle clearing data
@app.route('/clear_expenses', methods=['POST'])
def clear_expenses():
    # Clear all expenses by writing an empty list to the file
    with open('expenses.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['category', 'amount', 'date'])
        writer.writeheader()  # This will overwrite the file with just the header
    print("All expenses have been cleared.")
    return redirect(url_for('home'))  # Redirect back to the homepage

if __name__ == "__main__":
    app.run(debug=True)
