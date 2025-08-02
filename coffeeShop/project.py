import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import random

class CoffeeShopManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Coffee Shop Management System")
        self.root.geometry("1200x700")
        self.root.resizable(False, False)
        
        # Database setup
        self.conn = sqlite3.connect('coffee_shop.db')
        self.cursor = self.conn.cursor()
        self.create_tables()
        
        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TButton', font=('Helvetica', 10), padding=5)
        self.style.configure('TLabel', font=('Helvetica', 10))
        self.style.configure('TEntry', font=('Helvetica', 10))
        
        # Colors
        self.bg_color = "#F5F5DC"  # Beige background
        self.main_color = "#6F4E37"  # Coffee brown
        self.accent_color = "#C4A484"  # Light coffee
        
        # Main frame
        self.main_frame = tk.Frame(self.root, bg=self.bg_color)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self.header_frame = tk.Frame(self.main_frame, bg=self.main_color)
        self.header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.title_label = tk.Label(
            self.header_frame, 
            text="Coffee Shop Management System", 
            font=('Helvetica', 20, 'bold'), 
            bg=self.main_color, 
            fg='white'
        )
        self.title_label.pack(pady=10)
        
        # Navigation
        self.nav_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.nav_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.create_nav_buttons()
        
        # Content area
        self.content_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Show dashboard by default
        self.show_dashboard()
    
    def create_tables(self):
        """Create database tables if they don't exist"""
        # Products table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL,
                cost REAL NOT NULL,
                stock INTEGER NOT NULL
            )
        ''')
        
        # Customers table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                points INTEGER DEFAULT 0
            )
        ''')
        
        # Orders table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                order_date TEXT NOT NULL,
                total_amount REAL NOT NULL,
                status TEXT DEFAULT 'Pending',
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
        ''')
        
        # Order items table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        ''')
        
        self.conn.commit()
    
    def create_nav_buttons(self):
        """Create navigation buttons"""
        buttons = [
            ("Dashboard", self.show_dashboard),
            ("Products", self.show_products),
            ("Customers", self.show_customers),
            ("Orders", self.show_orders),
            ("New Order", self.show_new_order),
            ("Reports", self.show_reports)
        ]
        
        for text, command in buttons:
            btn = ttk.Button(
                self.nav_frame, 
                text=text, 
                command=command,
                style='TButton'
            )
            btn.pack(side=tk.LEFT, padx=5)
    
    def clear_content_frame(self):
        """Clear the content frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_dashboard(self):
        """Show dashboard content"""
        self.clear_content_frame()
        
        # Dashboard title
        title_label = tk.Label(
            self.content_frame, 
            text="Dashboard", 
            font=('Helvetica', 16, 'bold'), 
            bg=self.bg_color
        )
        title_label.pack(pady=10)
        
        # Stats frame
        stats_frame = tk.Frame(self.content_frame, bg=self.bg_color)
        stats_frame.pack(fill=tk.X, pady=10)
        
        # Get stats from database
        total_products = self.cursor.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        total_customers = self.cursor.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
        total_orders = self.cursor.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
        revenue = self.cursor.execute("SELECT SUM(total_amount) FROM orders WHERE status='Completed'").fetchone()[0] or 0
        
        stats = [
            ("Total Products", total_products, "#4E3524"),
            ("Total Customers", total_customers, "#6F4E37"),
            ("Total Orders", total_orders, "#8B6B4D"),
            ("Total Revenue", f"${revenue:.2f}", "#A38B6D")
        ]
        
        for i, (text, value, color) in enumerate(stats):
            stat_frame = tk.Frame(stats_frame, bg=color, bd=1, relief=tk.RAISED)
            stat_frame.grid(row=0, column=i, padx=10, ipadx=20, ipady=20)
            
            value_label = tk.Label(
                stat_frame, 
                text=value, 
                font=('Helvetica', 18, 'bold'), 
                bg=color, 
                fg='white'
            )
            value_label.pack()
            
            text_label = tk.Label(
                stat_frame, 
                text=text, 
                font=('Helvetica', 12), 
                bg=color, 
                fg='white'
            )
            text_label.pack()
        
        # Recent orders frame
        recent_orders_frame = tk.Frame(self.content_frame, bg=self.bg_color)
        recent_orders_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        recent_label = tk.Label(
            recent_orders_frame, 
            text="Recent Orders", 
            font=('Helvetica', 14, 'bold'), 
            bg=self.bg_color
        )
        recent_label.pack(anchor=tk.W)
        
        # Treeview for recent orders
        columns = ("ID", "Customer", "Date", "Amount", "Status")
        self.recent_orders_tree = ttk.Treeview(
            recent_orders_frame, 
            columns=columns, 
            show="headings", 
            height=8
        )
        
        for col in columns:
            self.recent_orders_tree.heading(col, text=col)
            self.recent_orders_tree.column(col, width=120, anchor=tk.CENTER)
        
        self.recent_orders_tree.pack(fill=tk.BOTH, expand=True)
        
        # Populate recent orders
        self.populate_recent_orders()
    
    def populate_recent_orders(self):
        """Populate recent orders in the dashboard"""
        self.recent_orders_tree.delete(*self.recent_orders_tree.get_children())
        
        query = '''
            SELECT o.id, c.name, o.order_date, o.total_amount, o.status 
            FROM orders o
            LEFT JOIN customers c ON o.customer_id = c.id
            ORDER BY o.order_date DESC
            LIMIT 10
        '''
        
        orders = self.cursor.execute(query).fetchall()
        
        for order in orders:
            self.recent_orders_tree.insert("", tk.END, values=order)
    
    def show_products(self):
        """Show products management content"""
        self.clear_content_frame()
        
        # Products title
        title_label = tk.Label(
            self.content_frame, 
            text="Product Management", 
            font=('Helvetica', 16, 'bold'), 
            bg=self.bg_color
        )
        title_label.pack(pady=10)
        
        # Product management frame
        mgmt_frame = tk.Frame(self.content_frame, bg=self.bg_color)
        mgmt_frame.pack(fill=tk.X, pady=10)
        
        # Add product form
        form_frame = tk.Frame(mgmt_frame, bg=self.bg_color, bd=2, relief=tk.GROOVE)
        form_frame.pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        form_label = tk.Label(
            form_frame, 
            text="Add/Edit Product", 
            font=('Helvetica', 12, 'bold'), 
            bg=self.bg_color
        )
        form_label.pack(pady=5)
        
        # Form fields
        fields = [
            ("Name:", "product_name"),
            ("Category:", "product_category"),
            ("Price ($):", "product_price"),
            ("Cost ($):", "product_cost"),
            ("Stock:", "product_stock")
        ]
        
        self.product_entries = {}
        
        for text, field in fields:
            frame = tk.Frame(form_frame, bg=self.bg_color)
            frame.pack(fill=tk.X, pady=5)
            
            label = tk.Label(frame, text=text, width=10, anchor=tk.W, bg=self.bg_color)
            label.pack(side=tk.LEFT)
            
            entry = ttk.Entry(frame)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            self.product_entries[field] = entry
        
        # Buttons frame
        buttons_frame = tk.Frame(form_frame, bg=self.bg_color)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        add_button = ttk.Button(
            buttons_frame, 
            text="Add Product", 
            command=self.add_product
        )
        add_button.pack(side=tk.LEFT, padx=5)
        
        update_button = ttk.Button(
            buttons_frame, 
            text="Update Product", 
            command=self.update_product
        )
        update_button.pack(side=tk.LEFT, padx=5)
        
        clear_button = ttk.Button(
            buttons_frame, 
            text="Clear", 
            command=self.clear_product_form
        )
        clear_button.pack(side=tk.LEFT, padx=5)
        
        # Products list
        list_frame = tk.Frame(mgmt_frame, bg=self.bg_color, bd=2, relief=tk.GROOVE)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        list_label = tk.Label(
            list_frame, 
            text="Product List", 
            font=('Helvetica', 12, 'bold'), 
            bg=self.bg_color
        )
        list_label.pack(pady=5)
        
        # Search frame
        search_frame = tk.Frame(list_frame, bg=self.bg_color)
        search_frame.pack(fill=tk.X, pady=5)
        
        search_entry = ttk.Entry(search_frame)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        search_button = ttk.Button(
            search_frame, 
            text="Search", 
            command=lambda: self.search_products(search_entry.get())
        )
        search_button.pack(side=tk.LEFT, padx=5)
        
        # Treeview for products
        columns = ("ID", "Name", "Category", "Price", "Cost", "Stock")
        self.products_tree = ttk.Treeview(
            list_frame, 
            columns=columns, 
            show="headings", 
            height=15
        )
        
        for col in columns:
            self.products_tree.heading(col, text=col)
            self.products_tree.column(col, width=100, anchor=tk.CENTER)
        
        self.products_tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind selection event
        self.products_tree.bind("<<TreeviewSelect>>", self.on_product_select)
        
        # Populate products
        self.populate_products()
    
    def populate_products(self, search_term=None):
        """Populate products in the treeview"""
        self.products_tree.delete(*self.products_tree.get_children())
        
        if search_term:
            query = '''
                SELECT * FROM products 
                WHERE name LIKE ? OR category LIKE ?
                ORDER BY name
            '''
            params = (f"%{search_term}%", f"%{search_term}%")
        else:
            query = "SELECT * FROM products ORDER BY name"
            params = ()
        
        products = self.cursor.execute(query, params).fetchall()
        
        for product in products:
            self.products_tree.insert("", tk.END, values=product)
    
    def search_products(self, search_term):
        """Search products by name or category"""
        self.populate_products(search_term)
    
    def on_product_select(self, event):
        """Handle product selection from treeview"""
        selected = self.products_tree.focus()
        if not selected:
            return
        
        product = self.products_tree.item(selected, "values")
        
        # Fill form with selected product
        self.clear_product_form()
        
        self.product_entries["product_name"].insert(0, product[1])
        self.product_entries["product_category"].insert(0, product[2])
        self.product_entries["product_price"].insert(0, product[3])
        self.product_entries["product_cost"].insert(0, product[4])
        self.product_entries["product_stock"].insert(0, product[5])
    
    def clear_product_form(self):
        """Clear the product form"""
        for entry in self.product_entries.values():
            entry.delete(0, tk.END)
    
    def add_product(self):
        """Add a new product"""
        try:
            name = self.product_entries["product_name"].get().strip()
            category = self.product_entries["product_category"].get().strip()
            price = float(self.product_entries["product_price"].get())
            cost = float(self.product_entries["product_cost"].get())
            stock = int(self.product_entries["product_stock"].get())
            
            if not name or not category:
                messagebox.showerror("Error", "Name and category are required!")
                return
            
            query = '''
                INSERT INTO products (name, category, price, cost, stock)
                VALUES (?, ?, ?, ?, ?)
            '''
            self.cursor.execute(query, (name, category, price, cost, stock))
            self.conn.commit()
            
            messagebox.showinfo("Success", "Product added successfully!")
            self.clear_product_form()
            self.populate_products()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values for price, cost and stock!")
    
    def update_product(self):
        """Update selected product"""
        selected = self.products_tree.focus()
        if not selected:
            messagebox.showerror("Error", "Please select a product to update!")
            return
        
        product_id = self.products_tree.item(selected, "values")[0]
        
        try:
            name = self.product_entries["product_name"].get().strip()
            category = self.product_entries["product_category"].get().strip()
            price = float(self.product_entries["product_price"].get())
            cost = float(self.product_entries["product_cost"].get())
            stock = int(self.product_entries["product_stock"].get())
            
            if not name or not category:
                messagebox.showerror("Error", "Name and category are required!")
                return
            
            query = '''
                UPDATE products 
                SET name=?, category=?, price=?, cost=?, stock=?
                WHERE id=?
            '''
            self.cursor.execute(query, (name, category, price, cost, stock, product_id))
            self.conn.commit()
            
            messagebox.showinfo("Success", "Product updated successfully!")
            self.populate_products()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values for price, cost and stock!")
    
    def show_customers(self):
        """Show customers management content"""
        self.clear_content_frame()
        
        # Customers title
        title_label = tk.Label(
            self.content_frame, 
            text="Customer Management", 
            font=('Helvetica', 16, 'bold'), 
            bg=self.bg_color
        )
        title_label.pack(pady=10)
        
        # Customer management frame
        mgmt_frame = tk.Frame(self.content_frame, bg=self.bg_color)
        mgmt_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Add customer form
        form_frame = tk.Frame(mgmt_frame, bg=self.bg_color, bd=2, relief=tk.GROOVE)
        form_frame.pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        form_label = tk.Label(
            form_frame, 
            text="Add/Edit Customer", 
            font=('Helvetica', 12, 'bold'), 
            bg=self.bg_color
        )
        form_label.pack(pady=5)
        
        # Form fields
        fields = [
            ("Name:", "customer_name"),
            ("Phone:", "customer_phone"),
            ("Email:", "customer_email"),
            ("Points:", "customer_points")
        ]
        
        self.customer_entries = {}
        
        for text, field in fields:
            frame = tk.Frame(form_frame, bg=self.bg_color)
            frame.pack(fill=tk.X, pady=5)
            
            label = tk.Label(frame, text=text, width=10, anchor=tk.W, bg=self.bg_color)
            label.pack(side=tk.LEFT)
            
            entry = ttk.Entry(frame)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            self.customer_entries[field] = entry
        
        # Buttons frame
        buttons_frame = tk.Frame(form_frame, bg=self.bg_color)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        add_button = ttk.Button(
            buttons_frame, 
            text="Add Customer", 
            command=self.add_customer
        )
        add_button.pack(side=tk.LEFT, padx=5)
        
        update_button = ttk.Button(
            buttons_frame, 
            text="Update Customer", 
            command=self.update_customer
        )
        update_button.pack(side=tk.LEFT, padx=5)
        
        clear_button = ttk.Button(
            buttons_frame, 
            text="Clear", 
            command=self.clear_customer_form
        )
        clear_button.pack(side=tk.LEFT, padx=5)
        
        # Customers list
        list_frame = tk.Frame(mgmt_frame, bg=self.bg_color, bd=2, relief=tk.GROOVE)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        list_label = tk.Label(
            list_frame, 
            text="Customer List", 
            font=('Helvetica', 12, 'bold'), 
            bg=self.bg_color
        )
        list_label.pack(pady=5)
        
        # Search frame
        search_frame = tk.Frame(list_frame, bg=self.bg_color)
        search_frame.pack(fill=tk.X, pady=5)
        
        search_entry = ttk.Entry(search_frame)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        search_button = ttk.Button(
            search_frame, 
            text="Search", 
            command=lambda: self.search_customers(search_entry.get())
        )
        search_button.pack(side=tk.LEFT, padx=5)
        
        # Treeview for customers
        columns = ("ID", "Name", "Phone", "Email", "Points")
        self.customers_tree = ttk.Treeview(
            list_frame, 
            columns=columns, 
            show="headings", 
            height=15
        )
        
        for col in columns:
            self.customers_tree.heading(col, text=col)
            self.customers_tree.column(col, width=120, anchor=tk.CENTER)
        
        self.customers_tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind selection event
        self.customers_tree.bind("<<TreeviewSelect>>", self.on_customer_select)
        
        # Populate customers
        self.populate_customers()
    
    def populate_customers(self, search_term=None):
        """Populate customers in the treeview"""
        self.customers_tree.delete(*self.customers_tree.get_children())
        
        if search_term:
            query = '''
                SELECT * FROM customers 
                WHERE name LIKE ? OR phone LIKE ? OR email LIKE ?
                ORDER BY name
            '''
            params = (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%")
        else:
            query = "SELECT * FROM customers ORDER BY name"
            params = ()
        
        customers = self.cursor.execute(query, params).fetchall()
        
        for customer in customers:
            self.customers_tree.insert("", tk.END, values=customer)
    
    def search_customers(self, search_term):
        """Search customers by name, phone or email"""
        self.populate_customers(search_term)
    
    def on_customer_select(self, event):
        """Handle customer selection from treeview"""
        selected = self.customers_tree.focus()
        if not selected:
            return
        
        customer = self.customers_tree.item(selected, "values")
        
        # Fill form with selected customer
        self.clear_customer_form()
        
        self.customer_entries["customer_name"].insert(0, customer[1])
        self.customer_entries["customer_phone"].insert(0, customer[2])
        self.customer_entries["customer_email"].insert(0, customer[3])
        self.customer_entries["customer_points"].insert(0, customer[4])
    
    def clear_customer_form(self):
        """Clear the customer form"""
        for entry in self.customer_entries.values():
            entry.delete(0, tk.END)
    
    def add_customer(self):
        """Add a new customer"""
        try:
            name = self.customer_entries["customer_name"].get().strip()
            phone = self.customer_entries["customer_phone"].get().strip()
            email = self.customer_entries["customer_email"].get().strip()
            points = int(self.customer_entries["customer_points"].get() or 0)
            
            if not name:
                messagebox.showerror("Error", "Name is required!")
                return
            
            query = '''
                INSERT INTO customers (name, phone, email, points)
                VALUES (?, ?, ?, ?)
            '''
            self.cursor.execute(query, (name, phone, email, points))
            self.conn.commit()
            
            messagebox.showinfo("Success", "Customer added successfully!")
            self.clear_customer_form()
            self.populate_customers()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric value for points!")
    
    def update_customer(self):
        """Update selected customer"""
        selected = self.customers_tree.focus()
        if not selected:
            messagebox.showerror("Error", "Please select a customer to update!")
            return
        
        customer_id = self.customers_tree.item(selected, "values")[0]
        
        try:
            name = self.customer_entries["customer_name"].get().strip()
            phone = self.customer_entries["customer_phone"].get().strip()
            email = self.customer_entries["customer_email"].get().strip()
            points = int(self.customer_entries["customer_points"].get() or 0)
            
            if not name:
                messagebox.showerror("Error", "Name is required!")
                return
            
            query = '''
                UPDATE customers 
                SET name=?, phone=?, email=?, points=?
                WHERE id=?
            '''
            self.cursor.execute(query, (name, phone, email, points, customer_id))
            self.conn.commit()
            
            messagebox.showinfo("Success", "Customer updated successfully!")
            self.populate_customers()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric value for points!")
    
    def show_orders(self):
        """Show orders management content"""
        self.clear_content_frame()
        
        # Orders title
        title_label = tk.Label(
            self.content_frame, 
            text="Order Management", 
            font=('Helvetica', 16, 'bold'), 
            bg=self.bg_color
        )
        title_label.pack(pady=10)
        
        # Orders frame
        orders_frame = tk.Frame(self.content_frame, bg=self.bg_color)
        orders_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Search frame
        search_frame = tk.Frame(orders_frame, bg=self.bg_color)
        search_frame.pack(fill=tk.X, pady=5)
        
        search_entry = ttk.Entry(search_frame)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        search_button = ttk.Button(
            search_frame, 
            text="Search", 
            command=lambda: self.search_orders(search_entry.get())
        )
        search_button.pack(side=tk.LEFT, padx=5)
        
        # Filter frame
        filter_frame = tk.Frame(orders_frame, bg=self.bg_color)
        filter_frame.pack(fill=tk.X, pady=5)
        
        status_label = tk.Label(filter_frame, text="Status:", bg=self.bg_color)
        status_label.pack(side=tk.LEFT, padx=5)
        
        self.status_var = tk.StringVar(value="All")
        status_options = ["All", "Pending", "Completed", "Cancelled"]
        
        for option in status_options:
            rb = ttk.Radiobutton(
                filter_frame, 
                text=option, 
                variable=self.status_var, 
                value=option,
                command=self.filter_orders
            )
            rb.pack(side=tk.LEFT, padx=5)
        
        # Treeview for orders
        columns = ("ID", "Customer", "Date", "Amount", "Status")
        self.orders_tree = ttk.Treeview(
            orders_frame, 
            columns=columns, 
            show="headings", 
            height=15
        )
        
        for col in columns:
            self.orders_tree.heading(col, text=col)
            self.orders_tree.column(col, width=120, anchor=tk.CENTER)
        
        self.orders_tree.pack(fill=tk.BOTH, expand=True)
        
        # Buttons frame
        buttons_frame = tk.Frame(orders_frame, bg=self.bg_color)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        view_button = ttk.Button(
            buttons_frame, 
            text="View Details", 
            command=self.view_order_details
        )
        view_button.pack(side=tk.LEFT, padx=5)
        
        complete_button = ttk.Button(
            buttons_frame, 
            text="Mark as Completed", 
            command=lambda: self.update_order_status("Completed")
        )
        complete_button.pack(side=tk.LEFT, padx=5)
        
        cancel_button = ttk.Button(
            buttons_frame, 
            text="Cancel Order", 
            command=lambda: self.update_order_status("Cancelled")
        )
        cancel_button.pack(side=tk.LEFT, padx=5)
        
        # Populate orders
        self.filter_orders()
    
    def filter_orders(self):
        """Filter orders by status"""
        status = self.status_var.get()
        
        if status == "All":
            query = '''
                SELECT o.id, c.name, o.order_date, o.total_amount, o.status 
                FROM orders o
                LEFT JOIN customers c ON o.customer_id = c.id
                ORDER BY o.order_date DESC
            '''
            params = ()
        else:
            query = '''
                SELECT o.id, c.name, o.order_date, o.total_amount, o.status 
                FROM orders o
                LEFT JOIN customers c ON o.customer_id = c.id
                WHERE o.status = ?
                ORDER BY o.order_date DESC
            '''
            params = (status,)
        
        self.populate_orders(query, params)
    
    def search_orders(self, search_term):
        """Search orders by customer name or order ID"""
        if not search_term:
            self.filter_orders()
            return
        
        query = '''
            SELECT o.id, c.name, o.order_date, o.total_amount, o.status 
            FROM orders o
            LEFT JOIN customers c ON o.customer_id = c.id
            WHERE c.name LIKE ? OR o.id = ?
            ORDER BY o.order_date DESC
        '''
        params = (f"%{search_term}%", search_term)
        
        self.populate_orders(query, params)
    
    def populate_orders(self, query, params):
        """Populate orders in the treeview"""
        self.orders_tree.delete(*self.orders_tree.get_children())
        
        orders = self.cursor.execute(query, params).fetchall()
        
        for order in orders:
            self.orders_tree.insert("", tk.END, values=order)
    
    def view_order_details(self):
        """View details of selected order"""
        selected = self.orders_tree.focus()
        if not selected:
            messagebox.showerror("Error", "Please select an order to view!")
            return
        
        order_id = self.orders_tree.item(selected, "values")[0]
        
        # Get order details
        order_query = '''
            SELECT o.id, c.name, o.order_date, o.total_amount, o.status 
            FROM orders o
            LEFT JOIN customers c ON o.customer_id = c.id
            WHERE o.id = ?
        '''
        order = self.cursor.execute(order_query, (order_id,)).fetchone()
        
        # Get order items
        items_query = '''
            SELECT p.name, oi.quantity, oi.price, (oi.quantity * oi.price) as total
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = ?
        '''
        items = self.cursor.execute(items_query, (order_id,)).fetchall()
        
        # Create details window
        details_window = tk.Toplevel(self.root)
        details_window.title(f"Order Details - #{order_id}")
        details_window.geometry("600x400")
        
        # Order info frame
        info_frame = tk.Frame(details_window, bd=2, relief=tk.GROOVE)
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            info_frame, 
            text=f"Order #: {order[0]}", 
            font=('Helvetica', 12, 'bold')
        ).pack(anchor=tk.W)
        
        tk.Label(
            info_frame, 
            text=f"Customer: {order[1]}"
        ).pack(anchor=tk.W)
        
        tk.Label(
            info_frame, 
            text=f"Date: {order[2]}"
        ).pack(anchor=tk.W)
        
        tk.Label(
            info_frame, 
            text=f"Status: {order[4]}", 
            font=('Helvetica', 10, 'bold')
        ).pack(anchor=tk.W)
        
        # Items frame
        items_frame = tk.Frame(details_window)
        items_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        columns = ("Product", "Qty", "Price", "Total")
        items_tree = ttk.Treeview(
            items_frame, 
            columns=columns, 
            show="headings", 
            height=8
        )
        
        for col in columns:
            items_tree.heading(col, text=col)
            items_tree.column(col, width=100, anchor=tk.CENTER)
        
        items_tree.pack(fill=tk.BOTH, expand=True)
        
        # Add items to treeview
        for item in items:
            items_tree.insert("", tk.END, values=item)
        
        # Total frame
        total_frame = tk.Frame(details_window, bd=2, relief=tk.GROOVE)
        total_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            total_frame, 
            text=f"Total Amount: ${order[3]:.2f}", 
            font=('Helvetica', 12, 'bold')
        ).pack(anchor=tk.E)
    
    def update_order_status(self, status):
        """Update status of selected order"""
        selected = self.orders_tree.focus()
        if not selected:
            messagebox.showerror("Error", "Please select an order to update!")
            return
        
        order_id = self.orders_tree.item(selected, "values")[0]
        
        query = "UPDATE orders SET status = ? WHERE id = ?"
        self.cursor.execute(query, (status, order_id))
        self.conn.commit()
        
        messagebox.showinfo("Success", f"Order status updated to {status}!")
        self.filter_orders()
    
    def show_new_order(self):
        """Show new order form"""
        self.clear_content_frame()
        
        # New order title
        title_label = tk.Label(
            self.content_frame, 
            text="New Order", 
            font=('Helvetica', 16, 'bold'), 
            bg=self.bg_color
        )
        title_label.pack(pady=10)
        
        # Main order frame
        order_frame = tk.Frame(self.content_frame, bg=self.bg_color)
        order_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Customer selection frame
        customer_frame = tk.Frame(order_frame, bg=self.bg_color, bd=2, relief=tk.GROOVE)
        customer_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            customer_frame, 
            text="Customer:", 
            font=('Helvetica', 12), 
            bg=self.bg_color
        ).pack(side=tk.LEFT, padx=5)
        
        # Customer combobox
        self.customer_var = tk.StringVar()
        customers = self.cursor.execute("SELECT id, name FROM customers ORDER BY name").fetchall()
        customer_options = [f"{id} - {name}" for id, name in customers]
        
        self.customer_combobox = ttk.Combobox(
            customer_frame, 
            textvariable=self.customer_var, 
            values=customer_options,
            state="readonly"
        )
        self.customer_combobox.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # New customer button
        new_customer_button = ttk.Button(
            customer_frame, 
            text="New Customer", 
            command=self.add_new_customer
        )
        new_customer_button.pack(side=tk.LEFT, padx=5)
        
        # Products frame
        products_frame = tk.Frame(order_frame, bg=self.bg_color)
        products_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left frame - product selection
        left_frame = tk.Frame(products_frame, bg=self.bg_color)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        tk.Label(
            left_frame, 
            text="Add Product to Order", 
            font=('Helvetica', 12), 
            bg=self.bg_color
        ).pack(pady=5)
        
        # Category filter
        categories = self.cursor.execute("SELECT DISTINCT category FROM products ORDER BY category").fetchall()
        categories = [cat[0] for cat in categories]
        
        self.category_var = tk.StringVar(value="All")
        category_label = tk.Label(left_frame, text="Filter by Category:", bg=self.bg_color)
        category_label.pack(anchor=tk.W)
        
        category_menu = ttk.OptionMenu(
            left_frame, 
            self.category_var, 
            "All", 
            *["All"] + categories,
            command=self.filter_products_for_order
        )
        category_menu.pack(fill=tk.X, pady=5)
        
        # Products listbox
        self.products_listbox = tk.Listbox(
            left_frame, 
            height=15, 
            selectmode=tk.SINGLE
        )
        self.products_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Bind double click event
        self.products_listbox.bind("<Double-Button-1>", self.add_product_to_order)
        
        # Right frame - order items
        right_frame = tk.Frame(products_frame, bg=self.bg_color, bd=2, relief=tk.GROOVE)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        tk.Label(
            right_frame, 
            text="Order Items", 
            font=('Helvetica', 12), 
            bg=self.bg_color
        ).pack(pady=5)
        
        # Order items treeview
        columns = ("Product", "Price", "Qty", "Total")
        self.order_items_tree = ttk.Treeview(
            right_frame, 
            columns=columns, 
            show="headings", 
            height=10
        )
        
        for col in columns:
            self.order_items_tree.heading(col, text=col)
            self.order_items_tree.column(col, width=80, anchor=tk.CENTER)
        
        self.order_items_tree.pack(fill=tk.BOTH, expand=True)
        
        # Quantity frame
        quantity_frame = tk.Frame(right_frame, bg=self.bg_color)
        quantity_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            quantity_frame, 
            text="Quantity:", 
            bg=self.bg_color
        ).pack(side=tk.LEFT, padx=5)
        
        self.quantity_var = tk.IntVar(value=1)
        quantity_spin = ttk.Spinbox(
            quantity_frame, 
            from_=1, 
            to=10, 
            textvariable=self.quantity_var,
            width=5
        )
        quantity_spin.pack(side=tk.LEFT, padx=5)
        
        # Buttons frame
        buttons_frame = tk.Frame(right_frame, bg=self.bg_color)
        buttons_frame.pack(fill=tk.X, pady=5)
        
        add_button = ttk.Button(
            buttons_frame, 
            text="Add Item", 
            command=self.add_product_to_order
        )
        add_button.pack(side=tk.LEFT, padx=5)
        
        remove_button = ttk.Button(
            buttons_frame, 
            text="Remove Item", 
            command=self.remove_order_item
        )
        remove_button.pack(side=tk.LEFT, padx=5)
        
        # Total frame
        total_frame = tk.Frame(right_frame, bg=self.bg_color, bd=2, relief=tk.GROOVE)
        total_frame.pack(fill=tk.X, pady=10)
        
        self.total_var = tk.StringVar(value="Total: $0.00")
        total_label = tk.Label(
            total_frame, 
            textvariable=self.total_var, 
            font=('Helvetica', 12, 'bold'), 
            bg=self.bg_color
        )
        total_label.pack(anchor=tk.E, padx=10)
        
        # Submit button
        submit_button = ttk.Button(
            order_frame, 
            text="Submit Order", 
            command=self.submit_order,
            style='TButton'
        )
        submit_button.pack(pady=10)
        
        # Initialize order items list
        self.order_items = []
        
        # Populate products list
        self.filter_products_for_order()
    
    def filter_products_for_order(self, *args):
        """Filter products by category for order"""
        category = self.category_var.get()
        
        if category == "All":
            query = "SELECT id, name, price FROM products WHERE stock > 0 ORDER BY name"
            params = ()
        else:
            query = "SELECT id, name, price FROM products WHERE category = ? AND stock > 0 ORDER BY name"
            params = (category,)
        
        products = self.cursor.execute(query, params).fetchall()
        
        self.products_listbox.delete(0, tk.END)
        
        for product in products:
            self.products_listbox.insert(tk.END, f"{product[1]} - ${product[2]:.2f}")
            self.products_listbox.items = products  # Store product data with listbox
    
    def add_product_to_order(self, event=None):
        """Add selected product to order"""
        selection = self.products_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select a product to add!")
            return
        
        product = self.products_listbox.items[selection[0]]
        product_id, product_name, product_price = product
        quantity = self.quantity_var.get()
        
        # Check if product already in order
        for item in self.order_items:
            if item["id"] == product_id:
                item["quantity"] += quantity
                self.update_order_items_tree()
                return
        
        # Add new item
        self.order_items.append({
            "id": product_id,
            "name": product_name,
            "price": product_price,
            "quantity": quantity
        })
        
        self.update_order_items_tree()
    
    def remove_order_item(self):
        """Remove selected item from order"""
        selection = self.order_items_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select an item to remove!")
            return
        
        item_index = self.order_items_tree.index(selection[0])
        del self.order_items[item_index]
        
        self.update_order_items_tree()
    
    def update_order_items_tree(self):
        """Update the order items treeview"""
        self.order_items_tree.delete(*self.order_items_tree.get_children())
        
        total = 0
        
        for item in self.order_items:
            item_total = item["price"] * item["quantity"]
            total += item_total
            
            self.order_items_tree.insert("", tk.END, values=(
                item["name"],
                f"${item['price']:.2f}",
                item["quantity"],
                f"${item_total:.2f}"
            ))
        
        self.total_var.set(f"Total: ${total:.2f}")
    
    def add_new_customer(self):
        """Open a dialog to add a new customer"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Customer")
        dialog.geometry("400x300")
        
        # Form fields
        fields = [
            ("Name:", "new_customer_name"),
            ("Phone:", "new_customer_phone"),
            ("Email:", "new_customer_email")
        ]
        
        entries = {}
        
        for text, field in fields:
            frame = tk.Frame(dialog)
            frame.pack(fill=tk.X, padx=10, pady=5)
            
            label = tk.Label(frame, text=text, width=10, anchor=tk.W)
            label.pack(side=tk.LEFT)
            
            entry = ttk.Entry(frame)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            entries[field] = entry
        
        # Buttons frame
        buttons_frame = tk.Frame(dialog)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        save_button = ttk.Button(
            buttons_frame, 
            text="Save", 
            command=lambda: self.save_new_customer(dialog, entries)
        )
        save_button.pack(side=tk.LEFT, padx=10)
        
        cancel_button = ttk.Button(
            buttons_frame, 
            text="Cancel", 
            command=dialog.destroy
        )
        cancel_button.pack(side=tk.LEFT)
    
    def save_new_customer(self, dialog, entries):
        """Save new customer and update combobox"""
        name = entries["new_customer_name"].get().strip()
        phone = entries["new_customer_phone"].get().strip()
        email = entries["new_customer_email"].get().strip()
        
        if not name:
            messagebox.showerror("Error", "Name is required!")
            return
        
        query = '''
            INSERT INTO customers (name, phone, email)
            VALUES (?, ?, ?)
        '''
        self.cursor.execute(query, (name, phone, email))
        self.conn.commit()
        
        # Get the new customer ID
        customer_id = self.cursor.lastrowid
        
        # Update the combobox
        current_values = list(self.customer_combobox["values"])
        current_values.append(f"{customer_id} - {name}")
        self.customer_combobox["values"] = current_values
        self.customer_combobox.set(f"{customer_id} - {name}")
        
        dialog.destroy()
        messagebox.showinfo("Success", "Customer added successfully!")
    
    def submit_order(self):
        """Submit the current order"""
        if not self.order_items:
            messagebox.showerror("Error", "Please add items to the order!")
            return
        
        customer = self.customer_var.get()
        if not customer:
            if not messagebox.askyesno("No Customer", "No customer selected. Continue as walk-in customer?"):
                return
            customer_id = None
        else:
            customer_id = int(customer.split(" - ")[0])
        
        # Calculate total
        total = sum(item["price"] * item["quantity"] for item in self.order_items)
        
        # Create order
        order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        query = '''
            INSERT INTO orders (customer_id, order_date, total_amount, status)
            VALUES (?, ?, ?, ?)
        '''
        self.cursor.execute(query, (customer_id, order_date, total, "Pending"))
        order_id = self.cursor.lastrowid
        
        # Add order items
        for item in self.order_items:
            query = '''
                INSERT INTO order_items (order_id, product_id, quantity, price)
                VALUES (?, ?, ?, ?)
            '''
            self.cursor.execute(query, (order_id, item["id"], item["quantity"], item["price"]))
            
            # Update product stock
            query = "UPDATE products SET stock = stock - ? WHERE id = ?"
            self.cursor.execute(query, (item["quantity"], item["id"]))
        
        # Update customer points if applicable
        if customer_id:
            points = int(total)  # 1 point per dollar
            query = "UPDATE customers SET points = points + ? WHERE id = ?"
            self.cursor.execute(query, (points, customer_id))
        
        self.conn.commit()
        
        # Generate receipt
        self.generate_receipt(order_id, customer_id, order_date, total)
        
        # Reset order form
        self.order_items = []
        self.update_order_items_tree()
        self.customer_var.set("")
        
        messagebox.showinfo("Success", f"Order #{order_id} submitted successfully!")
    
    def generate_receipt(self, order_id, customer_id, order_date, total):
        """Generate a receipt for the order"""
        receipt_window = tk.Toplevel(self.root)
        receipt_window.title(f"Receipt - Order #{order_id}")
        receipt_window.geometry("400x600")
        
        # Receipt content
        receipt_frame = tk.Frame(receipt_window)
        receipt_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        tk.Label(
            receipt_frame, 
            text="COFFEE SHOP", 
            font=('Helvetica', 18, 'bold')
        ).pack(pady=5)
        
        tk.Label(
            receipt_frame, 
            text="123 Coffee Street, Java City", 
            font=('Helvetica', 10)
        ).pack(pady=2)
        
        tk.Label(
            receipt_frame, 
            text="Tel: (123) 456-7890", 
            font=('Helvetica', 10)
        ).pack(pady=2)
        
        # Order info
        tk.Label(
            receipt_frame, 
            text="-" * 40, 
            font=('Helvetica', 10)
        ).pack(pady=5)
        
        tk.Label(
            receipt_frame, 
            text=f"Order #: {order_id}", 
            font=('Helvetica', 10)
        ).pack(anchor=tk.W, pady=2)
        
        tk.Label(
            receipt_frame, 
            text=f"Date: {order_date}", 
            font=('Helvetica', 10)
        ).pack(anchor=tk.W, pady=2)
        
        if customer_id:
            customer = self.cursor.execute(
                "SELECT name FROM customers WHERE id = ?", 
                (customer_id,)
            ).fetchone()
            
            if customer:
                tk.Label(
                    receipt_frame, 
                    text=f"Customer: {customer[0]}", 
                    font=('Helvetica', 10)
                ).pack(anchor=tk.W, pady=2)
        
        tk.Label(
            receipt_frame, 
            text="-" * 40, 
            font=('Helvetica', 10)
        ).pack(pady=5)
        
        # Order items
        items = self.cursor.execute('''
            SELECT p.name, oi.quantity, oi.price 
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = ?
        ''', (order_id,)).fetchall()
        
        for item in items:
            item_frame = tk.Frame(receipt_frame)
            item_frame.pack(fill=tk.X, pady=2)
            
            name_label = tk.Label(
                item_frame, 
                text=f"{item[0]} x{item[1]}", 
                font=('Helvetica', 10),
                anchor=tk.W
            )
            name_label.pack(side=tk.LEFT)
            
            price_label = tk.Label(
                item_frame, 
                text=f"${item[2] * item[1]:.2f}", 
                font=('Helvetica', 10),
                anchor=tk.E
            )
            price_label.pack(side=tk.RIGHT)
        
        tk.Label(
            receipt_frame, 
            text="-" * 40, 
            font=('Helvetica', 10)
        ).pack(pady=5)
        
        # Total
        total_frame = tk.Frame(receipt_frame)
        total_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            total_frame, 
            text="TOTAL:", 
            font=('Helvetica', 12, 'bold'),
            anchor=tk.W
        ).pack(side=tk.LEFT)
        
        tk.Label(
            total_frame, 
            text=f"${total:.2f}", 
            font=('Helvetica', 12, 'bold'),
            anchor=tk.E
        ).pack(side=tk.RIGHT)
        
        # Footer
        tk.Label(
            receipt_frame, 
            text="-" * 40, 
            font=('Helvetica', 10)
        ).pack(pady=5)
        
        tk.Label(
            receipt_frame, 
            text="Thank you for your order!", 
            font=('Helvetica', 10, 'italic')
        ).pack(pady=10)
        
        # Print button
        print_button = ttk.Button(
            receipt_frame, 
            text="Print Receipt", 
            command=lambda: self.print_receipt(receipt_window)
        )
        print_button.pack(pady=10)
    
    def print_receipt(self, window):
        """Print the receipt (simulated)"""
        messagebox.showinfo("Print", "Receipt sent to printer!")
        window.destroy()
    
    def show_reports(self):
        """Show reports section"""
        self.clear_content_frame()
        
        # Reports title
        title_label = tk.Label(
            self.content_frame, 
            text="Reports", 
            font=('Helvetica', 16, 'bold'), 
            bg=self.bg_color
        )
        title_label.pack(pady=10)
        
        # Reports frame
        reports_frame = tk.Frame(self.content_frame, bg=self.bg_color)
        reports_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Sales report
        sales_frame = tk.Frame(reports_frame, bg=self.bg_color, bd=2, relief=tk.GROOVE)
        sales_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        tk.Label(
            sales_frame, 
            text="Sales Report", 
            font=('Helvetica', 12, 'bold'), 
            bg=self.bg_color
        ).pack(pady=5)
        
        # Date range selection
        date_frame = tk.Frame(sales_frame, bg=self.bg_color)
        date_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            date_frame, 
            text="From:", 
            bg=self.bg_color
        ).pack(side=tk.LEFT, padx=5)
        
        self.from_date_entry = ttk.Entry(date_frame)
        self.from_date_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(
            date_frame, 
            text="To:", 
            bg=self.bg_color
        ).pack(side=tk.LEFT, padx=5)
        
        self.to_date_entry = ttk.Entry(date_frame)
        self.to_date_entry.pack(side=tk.LEFT, padx=5)
        
        generate_button = ttk.Button(
            date_frame, 
            text="Generate", 
            command=self.generate_sales_report
        )
        generate_button.pack(side=tk.LEFT, padx=10)
        
        # Sales report treeview
        columns = ("Date", "Total Orders", "Total Sales")
        self.sales_report_tree = ttk.Treeview(
            sales_frame, 
            columns=columns, 
            show="headings", 
            height=8
        )
        
        for col in columns:
            self.sales_report_tree.heading(col, text=col)
            self.sales_report_tree.column(col, width=120, anchor=tk.CENTER)
        
        self.sales_report_tree.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Summary frame
        summary_frame = tk.Frame(sales_frame, bg=self.bg_color)
        summary_frame.pack(fill=tk.X, pady=5)
        
        self.summary_var = tk.StringVar(value="Total Sales: $0.00 | Average Daily Sales: $0.00")
        summary_label = tk.Label(
            summary_frame, 
            textvariable=self.summary_var, 
            font=('Helvetica', 10, 'bold'), 
            bg=self.bg_color
        )
        summary_label.pack(anchor=tk.E)
        
        # Popular products report
        popular_frame = tk.Frame(reports_frame, bg=self.bg_color, bd=2, relief=tk.GROOVE)
        popular_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        tk.Label(
            popular_frame, 
            text="Popular Products", 
            font=('Helvetica', 12, 'bold'), 
            bg=self.bg_color
        ).pack(pady=5)
        
        # Popular products treeview
        columns = ("Product", "Category", "Total Sold", "Total Revenue")
        self.popular_products_tree = ttk.Treeview(
            popular_frame, 
            columns=columns, 
            show="headings", 
            height=8
        )
        
        for col in columns:
            self.popular_products_tree.heading(col, text=col)
            self.popular_products_tree.column(col, width=100, anchor=tk.CENTER)
        
        self.popular_products_tree.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Generate initial reports
        self.generate_sales_report()
        self.generate_popular_products_report()
    
    def generate_sales_report(self):
        """Generate sales report based on date range"""
        from_date = self.from_date_entry.get()
        to_date = self.to_date_entry.get()
        
        if from_date and to_date:
            query = '''
                SELECT 
                    date(order_date) as day,
                    COUNT(*) as total_orders,
                    SUM(total_amount) as total_sales
                FROM orders
                WHERE date(order_date) BETWEEN ? AND ?
                GROUP BY day
                ORDER BY day
            '''
            params = (from_date, to_date)
        else:
            query = '''
                SELECT 
                    date(order_date) as day,
                    COUNT(*) as total_orders,
                    SUM(total_amount) as total_sales
                FROM orders
                GROUP BY day
                ORDER BY day DESC
                LIMIT 30
            '''
            params = ()
        
        sales_data = self.cursor.execute(query, params).fetchall()
        
        self.sales_report_tree.delete(*self.sales_report_tree.get_children())
        
        total_sales = 0
        days = 0
        
        for day in sales_data:
            self.sales_report_tree.insert("", tk.END, values=day)
            total_sales += day[2]
            days += 1
        
        avg_sales = total_sales / days if days > 0 else 0
        self.summary_var.set(
            f"Total Sales: ${total_sales:.2f} | Average Daily Sales: ${avg_sales:.2f}"
        )
    
    def generate_popular_products_report(self):
        """Generate popular products report"""
        query = '''
            SELECT 
                p.name,
                p.category,
                SUM(oi.quantity) as total_sold,
                SUM(oi.quantity * oi.price) as total_revenue
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            JOIN orders o ON oi.order_id = o.id
            WHERE o.status = 'Completed'
            GROUP BY p.id
            ORDER BY total_sold DESC
            LIMIT 10
        '''
        
        products = self.cursor.execute(query).fetchall()
        
        self.popular_products_tree.delete(*self.popular_products_tree.get_children())
        
        for product in products:
            self.popular_products_tree.insert("", tk.END, values=product)

if __name__ == "__main__":
    root = tk.Tk()
    app = CoffeeShopManagementSystem(root)
    root.mainloop()