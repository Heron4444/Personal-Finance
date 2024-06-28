#		WITHOUT USING OOPS		#

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

# Connect to the SQLite database
conn = sqlite3.connect('finance.db')
c = conn.cursor()

# Create tables for incomes and expenses
c.execute('''CREATE TABLE IF NOT EXISTS incomes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                description TEXT,
                amount REAL
             )''')

c.execute('''CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                description TEXT,
                amount REAL
             )''')

conn.commit()

def update_dashboard():
    c.execute('SELECT SUM(amount) FROM incomes')
    total_income = c.fetchone()[0]
    c.execute('SELECT SUM(amount) FROM expenses')
    total_expense = c.fetchone()[0]

    total_income = total_income if total_income else 0
    total_expense = total_expense if total_expense else 0

    balance = total_income - total_expense

    income_var.set(f'Total Income: ${total_income:.2f}')
    expense_var.set(f'Total Expense: ${total_expense:.2f}')
    balance_var.set(f'Balance: ${balance:.2f}')

def add_record(record_type):
    date = date_entry.get()
    description = description_entry.get()
    amount = amount_entry.get()

    if not date or not description or not amount:
        messagebox.showerror("Error", "All fields are required!")
        return

    try:
        amount = float(amount)
    except ValueError:
        messagebox.showerror("Error", "Invalid amount!")
        return

    if record_type == 'income':
        c.execute('INSERT INTO incomes (date, description, amount) VALUES (?, ?, ?)', (date, description, amount))
    else:
        c.execute('INSERT INTO expenses (date, description, amount) VALUES (?, ?, ?)', (date, description, amount))

    conn.commit()
    update_dashboard()
    populate_treeview()
    save_data_to_file()

    messagebox.showinfo("Success", f"{record_type.capitalize()} added successfully!")
    date_entry.delete(0, tk.END)
    description_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)

def populate_treeview():
    for row in tree.get_children():
        tree.delete(row)

    c.execute('SELECT date, description, amount FROM incomes')
    for row in c.fetchall():
        tree.insert('', 'end', values=(row[0], row[1], f'+${row[2]:.2f}'))

    c.execute('SELECT date, description, amount FROM expenses')
    for row in c.fetchall():
        tree.insert('', 'end', values=(row[0], row[1], f'-${row[2]:.2f}'))

def save_data_to_file():
    with open('data.txt', 'w') as f:
        f.write('Incomes:\n')
        c.execute('SELECT date, description, amount FROM incomes')
        for row in c.fetchall():
            f.write(f'{row[0]}, {row[1]}, {row[2]:.2f}\n')

        f.write('\nExpenses:\n')
        c.execute('SELECT date, description, amount FROM expenses')
        for row in c.fetchall():
            f.write(f'{row[0]}, {row[1]}, {row[2]:.2f}\n')

def plot_visualization():
    # Query the database for income and expense data
    c.execute('SELECT date, amount FROM incomes')
    incomes = c.fetchall()
    c.execute('SELECT date, amount FROM expenses')
    expenses = c.fetchall()

    # Convert date strings to datetime objects and extract amounts
    income_dates = [row[0] for row in incomes]
    income_amounts = [row[1] for row in incomes]
    expense_dates = [row[0] for row in expenses]
    expense_amounts = [row[1] for row in expenses]

    # Plot the data
    plot.clear()
    plot.bar(income_dates, income_amounts, label='Income', color='green', alpha=0.7)
    plot.bar(expense_dates, expense_amounts, label='Expense', color='red', alpha=0.7)
    plot.set_xlabel('Date')
    plot.set_ylabel('Amount')
    plot.set_title('Income vs Expense Over Time')
    plot.legend()
    canvas.draw()

# Initialize the main window
root = tk.Tk()
root.title("Personal Finance Manager")
root.geometry("800x600")
root.resizable(0, 0)
root.configure(bg="#f0f0f0")  # Set background color

# Create style configurations
style = ttk.Style()
style.configure('TButton', background='#4CAF50', foreground='#4CAF50', font=('Arial', 12), padding=5)  # Button style
style.configure('TLabel', background='#f0f0f0', font=('Arial', 12))  # Label style
style.configure('Treeview', background='white', font=('Arial', 10))  # Treeview style

# Create tab control
tab_control = ttk.Notebook(root)

tab1 = ttk.Frame(tab_control)
tab2 = ttk.Frame(tab_control)
tab3 = ttk.Frame(tab_control)
tab4 = ttk.Frame(tab_control)

tab_control.add(tab1, text='Dashboard')
tab_control.add(tab2, text='Add Income/Expense')
tab_control.add(tab3, text='View Transactions')
tab_control.add(tab4, text='Visualize Data')  # Add new tab for visualization

tab_control.pack(expand=1, fill="both")

# Create dashboard elements
income_var = tk.DoubleVar()
expense_var = tk.DoubleVar()
balance_var = tk.DoubleVar()

income_label = tk.Label(tab1, textvariable=income_var, font=("Arial", 18), bg="#f0f0f0")
income_label.pack(pady=10)

expense_label = tk.Label(tab1, textvariable=expense_var, font=("Arial", 18), bg="#f0f0f0")
expense_label.pack(pady=10)

balance_label = tk.Label(tab1, textvariable=balance_var, font=("Arial", 18), bg="#f0f0f0")
balance_label.pack(pady=10)

update_dashboard()

# Create elements for adding records
date_label = tk.Label(tab2, text="Date (YYYY-MM-DD):", font=("Arial", 14), bg="#f0f0f0")
date_label.pack(pady=5)
date_entry = tk.Entry(tab2, font=("Arial", 14))
date_entry.pack(pady=5)

description_label = tk.Label(tab2, text="Description:", font=("Arial", 14), bg="#f0f0f0")
description_label.pack(pady=5)
description_entry = tk.Entry(tab2, font=("Arial", 14))
description_entry.pack(pady=5)

amount_label = tk.Label(tab2, text="Amount:", font=("Arial", 14), bg="#f0f0f0")
amount_label.pack(pady=5)
amount_entry = tk.Entry(tab2, font=("Arial", 14))
amount_entry.pack(pady=5)

# Create custom styles for the buttons
style.configure('Income.TButton', background='#4CAF50', foreground='black', font=('Arial', 12), padding=5)
style.map('Income.TButton', background=[('active', '#45a049')])  # Change color when hovered

style.configure('Expense.TButton', background='#f44336', foreground='black', font=('Arial', 12), padding=5)
style.map('Expense.TButton', background=[('active', '#e53935')])  # Change color when hovered

add_income_button = ttk.Button(tab2, text="Add Income", style='Income.TButton', command=lambda: add_record('income'))
add_income_button.pack(pady=10)

add_expense_button = ttk.Button(tab2, text="Add Expense", style='Expense.TButton', command=lambda: add_record('expense'))
add_expense_button.pack(pady=10)


# Create treeview for viewing transactions
columns = ('Date', 'Description', 'Amount')
tree = ttk.Treeview(tab3, columns=columns, show='headings')

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=100)

tree.pack(fill='both', expand=True)
populate_treeview()

# Create visualization tab
figure = Figure(figsize=(5, 4), dpi=100)
plot = figure.add_subplot(111)
canvas = FigureCanvasTkAgg(figure, tab4)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

plot_visualization()

# Start the main loop
root.mainloop()
conn.close()

