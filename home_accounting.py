import csv
import sqlite3
import hashlib
from datetime import datetime
from tkinter import *
from tkinter import filedialog
from tkinter import ttk, messagebox

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class FinanceApp:
    def __init__(self):
        self.root = root
        self.root.title('Home accounting app')
        self.root.geometry("400x500")
        self.setup_database()
        # Initialize sort_reverse
        self.sort_reverse = False

        # Initialize authenticated status
        self.authenticated = False
        # Add a label for displaying the authenticated user's name
        self.user_label = Label(self.root, text='User: Not Authenticated')
        self.user_label.config(foreground='red')
        self.user_label.pack(pady=10)

        # Init matplotlib figure and subplot
        self.fig, self.ax = plt.subplots()
        # Initialize matplotlib figure and subplot
        self.fig, self.ax = plt.subplots()

        # Set up the main GUI
        self.create_gui()

    def setup_database(self):
        self.connection = sqlite3.connect('finance.sqlite')
        self.cur = self.connection.cursor()

        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions 
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            amount REAL,
            description TEXT,
            datetime DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create user table if not exists
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users
            (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL 
            )
            """
        )

        self.connection.commit()

    @staticmethod
    def hash_password(password):
        # Hash the password using a secure hash function (e.g., SHA-256)
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        return hashed_password

    def register_user(self):
        # Create registration window
        register_window = Toplevel(self.root)
        register_window.title('Register')

        # Create anf pack labels and entry widgets for registration
        username_label = Label(register_window, text='Username')
        username_label.pack(pady=10)
        username_entry = Entry(register_window)
        username_entry.pack()

        password_label = Label(register_window, text='Password')
        password_label.pack(pady=10)
        password_entry = Entry(register_window, show='*')
        password_entry.pack()

        def register():
            # Create a func to handle user registration
            username = username_entry.get()
            password = password_entry.get()

            # Check if both username and password are entered
            if not username or not password:
                messagebox.showerror('Error', 'Please enter both username and password.')
                return

            # Check if the username is unique
            self.cur.execute("SELECT * FROM users WHERE username=?", (username,))
            existing_user = self.cur.fetchone()
            if existing_user:
                messagebox.showerror('Error', 'Username already exists. Please choose a different username.')
                return

            # HAsh the password before storing it
            hashed_password = self.hash_password(password)

            # Insert user data into the users table
            self.cur.execute(
                """
                INSERT INTO users (
                username, password) VALUES (?, ?)
                """, (username, hashed_password)
            )
            self.connection.commit()
            messagebox.showinfo('Success', 'Registration successful!')
            register_window.destroy()

        # Create and pack the registration button
        register_button = Button(register_window, text='Register', command=register)
        register_button.pack(pady=10)

    # Add a login method to your FinanceApp class
    def login_user(self):
        # Create a login window
        login_window = Toplevel(self.root)
        login_window.title('Login')
        self.authenticated = True

        # Create and pack labels and entry widgets for login
        username_label = Label(login_window, text='Username:')
        username_label.pack(pady=10)
        username_entry = Entry(login_window)
        username_entry.pack()

        password_label = Label(login_window, text='Password:')
        password_label.pack(pady=10)
        password_entry = Entry(login_window, show='*')  # Use show='*' to hide the password
        password_entry.pack()

        self.update_button_states()



        def login():
            # Create a function to handle user login
            username = username_entry.get()
            password = password_entry.get()

            # Retrieve the hashed password from the database
            self.cur.execute("SELECT password FROM users WHERE username=?", (username,))
            stored_password = self.cur.fetchone()

            if stored_password:
                # Check if the entered password matches the stored hash
                if self.check_password(password, stored_password[0]):
                    # Update authenticated status and current user
                    self.authenticated = True
                    self.current_user = username
                    # Update the user label
                    self.update_user_label()
                    messagebox.showinfo('Success', 'Login successful!')
                    login_window.destroy()
                else:
                    messagebox.showerror('Error', 'Invalid password!')
            else:
                messagebox.showerror('Error', 'User not found!')

        # Create and pack the login button
        login_button = Button(login_window, text='Login', command=login)
        login_button.pack(pady=10)

    def update_user_label(self):
        # Update the text of the user label based on authentication status
        if self.authenticated:
            self.user_label.config(text=f'User: {self.current_user} Authenticated')
        else:
            self.user_label.config(text='User: Not Authenticated')

    def update_button_states(self):
        for widget in self.root.winfo_children():
            if isinstance(widget, Button):
                if widget['text'] in ('Login', 'Register'):
                    # Disable Login and Register buttons when authenticated
                    widget['state'] = 'disabled' if self.authenticated else 'normal'
                else:
                    widget['state'] = 'normal' if self.authenticated else 'disabled'


    @staticmethod
    def check_password(input_password, stored_password):
        # Hash the input password
        hashed_input_password = hashlib.sha256(input_password.encode()).hexdigest()

        # Compare the hashed input password with the stored password
        return hashed_input_password == stored_password

    def logout_user(self):
        # Reset the authenticated status
        self.authenticated = False
        messagebox.showinfo('Success', 'Logout successful!')
        # Perform any other cleanup or actions needed for logout
        self.root.destroy()


    def add_transaction(self):
        if self.type_combobox.get() and self.amount_entry.get() and self.description_combobox.get():
            # Срабатывает, если введена сумма и выбран тип. В переменные записываем данные из полей ввода и записываем
            # в базу данных.
            try:
                transaction_type = self.type_combobox.get()
                amount = float(self.amount_entry.get())
                description = self.description_combobox.get()

                self.cur.execute("""
                INSERT INTO transactions (type, amount, description)
                VALUES (?, ?, ?) 
                """, (transaction_type, amount, description))
                self.connection.commit()

                # after adding to the database, all fields are cleared
                self.type_combobox.set("")
                self.amount_entry.delete(0, END)
                self.description_combobox.set("")
                messagebox.showinfo('Success', 'Data added!')

            except ValueError:
                messagebox.showerror('Error', 'Invalid amount!')
        else:
            messagebox.showinfo('Error', 'Please enter all fields!')

    def show_transaction(self):
        # create a child window to display the information
        view_window = Toplevel(self.root)
        view_window.title('Show transactions')

        # Create a table view
        treeview = ttk.Treeview(view_window)
        treeview.pack()

        # Define table columns
        treeview['columns'] = ('id', 'type', 'amount', 'description', 'datetime')
        treeview.column('id', width=20)
        treeview.column('type', anchor=W, width=100)
        treeview.column('amount', anchor=W, width=100)
        treeview.column('description', anchor=W, width=200)
        treeview.column('datetime', anchor=W, width=200)

        # Creating headers in the table
        treeview.heading('id', text='ID', command=lambda: self.sort_treeview(treeview, 'id'))
        treeview.heading('type', text='Type', command=lambda: self.sort_treeview(treeview, 'type'))
        treeview.heading('amount', text='Amount', command=lambda col='amount': self.sort_amount_treeview(treeview, col))
        treeview.heading('description', text='Description', command=lambda: self.sort_treeview(treeview, 'description'))
        treeview.heading('datetime', text='Datetime', command=lambda: self.sort_treeview(treeview, 'datetime'))

        # get data from the database and save it to variables
        self.cur.execute("""SELECT * FROM transactions""")
        rows = self.cur.fetchall()

        # insert data to database
        for row in rows:
            treeview.insert('', END, values=row)

        # Bind double-click event to the edit_transaction function
        treeview.bind("<Double-1>", lambda event: self.edit_transaction(treeview))

        # Add a button for deleting selected transaction
        delete_button = Button(view_window, text='Delete', command=lambda: self.delete_transaction(treeview))
        delete_button.pack(side=LEFT, padx=10, pady=10)

        # Add a button for export transaction to csv file
        export_button = Button(view_window, text='Export to file', command=self.export_to_csv)
        export_button.pack(side=LEFT, padx=10, pady=10)

        # Add a button for showing the spending patterns chat
        chart_button = Button(view_window, text='Show Chart', command=self.show_chart)
        chart_button.pack(side=LEFT, padx=10, pady=10)

    def show_chart(self):
        # Create a new window for the chart
        chart_window = Toplevel(self.root)
        chart_window.title('Spending Patterns Chart')

        # Initialize canvas in the chart window
        canvas = FigureCanvasTkAgg(self.fig, master=chart_window)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack()

        # Get data for spending patterns (replace this with your actual data)
        self.cur.execute("""SELECT type, SUM(amount) FROM transactions GROUP BY type""")
        data = self.cur.fetchall()
        types, amounts = zip(*data)

        # Clear previous chart
        self.ax.clear()

        # Plot bar chart
        self.ax.bar(types, amounts)
        self.ax.set_xlabel('Transaction Type')
        self.ax.set_ylabel('Total Amount')
        self.ax.set_title('Spending Patterns')

        # Update the canvas
        canvas.draw()

    def delete_transaction(self, treeview):
        selected_item = treeview.selection()

        if not selected_item:
            messagebox.showinfo('Error', 'Please select a transaction to delete.')
            return

        confirmation = messagebox.askyesno('Confirmation', 'Are you sure you want to delete this transaction?')

        if confirmation:
            # Extract the ID of the selected item
            transaction_id = treeview.item(selected_item, 'values')[0]
            try:
                # Delete the selected transaction from the database
                self.cur.execute("DELETE FROM transactions WHERE id=?", (transaction_id,))
                self.connection.commit()
                print("Transaction deleted from the database.")
            except Exception as e:
                print(f"Error deleting transaction from the database: {e}")

            # Delete the selected item from the treeview
            treeview.delete(selected_item)

            messagebox.showinfo('Success', 'Transaction deleted!')

    def edit_transaction(self, treeview):
        selected_item = treeview.selection()

        if not selected_item:
            messagebox.showinfo('Error', 'Please select a transaction to update.')
            return

        # Extract the values of the selected item
        values = treeview.item(selected_item, 'values')

        # Create a new window for editing transaction details
        edit_window = Toplevel(self.root)
        edit_window.title('Edit Transaction')

        # Create and pack labels and entry widgets for editing
        type_label = Label(edit_window, text='Type:')
        type_label.pack(pady=10)
        type_entry = ttk.Combobox(edit_window, values=['Income', 'Expense'])
        type_entry.set(values[1])
        type_entry.pack()

        amount_label = Label(edit_window, text='Amount:')
        amount_label.pack(pady=10)
        amount_entry = Entry(edit_window)
        amount_entry.insert(0, values[2])
        amount_entry.pack()

        description_label = Label(edit_window, text='Description:')
        description_label.pack(pady=10)
        description_combobox = ttk.Combobox(edit_window, values=['Fixed Expenses',
                                                                 'Free Time',
                                                                 'Groceries & Household',
                                                                 'Health & Wellness',
                                                                 'Other',
                                                                 'Restaurants & Bars',
                                                                 'Shopping',
                                                                 'Transport & Travel'
                                                                 'Returns',
                                                                 'Salary Income',
                                                                 'Other Income'
                                                                 ])

        description_combobox.set(values[3])
        description_combobox.pack()

        def update_details():
            try:
                transaction_id = values[0]
                transaction_type = type_entry.get()
                amount = float(amount_entry.get())
                description = description_combobox.get()

                # Get the current timestamp in the desired format
                formatted_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Update the database with the new values
                self.cur.execute("""
                    UPDATE transactions
                    SET type=?, amount=?, description=?,datetime=?
                    WHERE id=?

                """, (transaction_type, amount, description, formatted_datetime, transaction_id))

                self.connection.commit()

                # Update the values in the treeview
                treeview.item(selected_item,
                              values=(transaction_id, transaction_type, amount, description, formatted_datetime))

                messagebox.showinfo('Success', 'Transaction updated!')
                edit_window.destroy()

            except ValueError:
                messagebox.showerror('Error', 'Invalid amount!')

        # Create and pack the update button
        update_button = Button(edit_window, text='Update', command=update_details)
        update_button.pack(pady=10)

    def export_to_csv(self, file_path=None):
        if file_path is None:

            try:
                # Get all transactions from the database
                self.cur.execute("""SELECT * FROM transactions""")
                rows = self.cur.fetchall()

                # Specify the CSV file path
                csv_file_path = filedialog.asksaveasfilename(
                    filetypes=(
                        ('CSV files', '*.csv'),

                    )
                )

                # Write transaction data to the CSV file
                with open(csv_file_path, 'w', newline='') as csv_file:
                    csv_writer = csv.writer(csv_file)

                    # Write header
                    csv_writer.writerow(['ID', 'Type', 'Amount', 'Description', 'Datetime'])

                    # Write data
                    csv_writer.writerows(rows)

                messagebox.showinfo('Success', f'Data exported to {csv_file_path}!')

            except Exception as e:
                messagebox.showerror('Error', f'Error exporting data: {e}')

    def create_gui(self):
        # Add a button for user registration
        register_button = Button(self.root, text='Register', command=self.register_user)
        register_button.pack(pady=10)

        # Add a button for user login
        login_button = Button(self.root, text='Login', command=self.login_user)
        login_button.pack(pady=10)

        # Add a logout button
        logout_button = Button(self.root, text='Logout', command=self.logout_user)
        logout_button.pack(pady=10)

        type_label = Label(self.root, text='Type:')
        type_label.pack(pady=10)
        self.type_combobox = ttk.Combobox(self.root, values=['Income', 'Expense'])
        self.type_combobox.pack()

        amount_label = Label(self.root, text='Amount:')
        amount_label.pack(pady=10)
        self.amount_entry = Entry(self.root)
        self.amount_entry.pack()

        description_label = Label(self.root, text='Description:')
        description_label.pack(pady=10)
        self.description_combobox = ttk.Combobox(self.root, values=['Fixed Expenses',
                                                                    'Free Time',
                                                                    'Groceries & Household',
                                                                    'Health & Wellness',
                                                                    'Other',
                                                                    'Restaurants & Bars',
                                                                    'Shopping',
                                                                    'Transport & Travel'
                                                                    'Returns',
                                                                    'Salary Income',
                                                                    'Other Income'
                                                                    ])
        self.description_combobox.pack()

        # Add a button for adding transactions (only available to authenticated users)
        add_button = Button(self.root, text='Add', command=self.add_transaction, state='disabled')
        add_button.pack(pady=10)

        # Add a button for showing transactions (only available to authenticated users)
        view_button = Button(self.root, text='Show', command=self.show_transaction, state='disabled')
        view_button.pack(pady=10)

    @staticmethod
    def sort_amount_treeview(treeview, col):
        data = [(treeview.set(item, col), item) for item in treeview.get_children('')]
        data.sort(key=lambda x: float(x[0]) if x[0] else 0)

        for index, item in enumerate(data):
            treeview.move(item[1], '', index)

    def sort_treeview(self, treeview, column):
        data = [(treeview.set(child, column), child) for child in treeview.get_children('')]

        # Toggle sorting order
        data.sort(reverse=self.sort_reverse)

        for index, item in enumerate(data):
            treeview.move(item[1], '', index)

        # Toggle sorting order for the next click
        self.sort_reverse = not self.sort_reverse

    def run(self):
        self.root.mainloop()
        self.connection.close()


# Instantiate and run the FinanceApp
if __name__ == "__main__":
    root = Tk()
    app = FinanceApp()
    app.run()

# TODO Transactions:

# Add a search function to easily find specific transactions.
