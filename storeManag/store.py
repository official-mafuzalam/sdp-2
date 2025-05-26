import csv
from datetime import datetime
import os

# File paths
PRODUCTS_FILE = "products.csv"
ORDERS_FILE = "orders.csv"

def initialize_files():
    """Create CSV files if they don't exist."""
    if not os.path.exists(PRODUCTS_FILE):
        with open(PRODUCTS_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Name", "Price", "Stock"])

    if not os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["OrderID", "Date", "Items", "Total"])

def display_menu():
    """Display the main menu."""
    print("\n=== Departmental Store Ordering System ===")
    print("1. View Products")
    print("2. Place Order")
    print("3. View Order History")
    print("4. Admin Mode")
    print("5. Exit")

def view_products():
    """Display all available products."""
    try:
        with open(PRODUCTS_FILE, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            print("\n--- Available Products ---")
            for row in reader:
                print(f"{row[0]}. {row[1]} - ${row[2]} (Stock: {row[3]})")
    except FileNotFoundError:
        print("Product database not found. Please contact admin.")

def place_order():
    """Place a new order."""
    try:
        with open(PRODUCTS_FILE, 'r') as file:
            products = list(csv.reader(file))[1:]  # Skip header

        order_items = []
        total = 0.0

        while True:
            view_products()
            product_id = input("Enter product ID (or 'done' to finish): ").strip()
            if product_id.lower() == 'done':
                break

            found = False
            for product in products:
                if product[0] == product_id and int(product[3]) > 0:
                    quantity = int(input(f"How many {product[1]}? (Available: {product[3]}): "))
                    if quantity <= int(product[3]):
                        order_items.append(f"{product[1]} x{quantity}")
                        total += float(product[2]) * quantity
                        found = True
                        # Update stock in memory
                        product[3] = str(int(product[3]) - quantity)
                        break
                    else:
                        print("Not enough stock!")
                        break

            if not found:
                print("Invalid product ID or out of stock.")

        if not order_items:
            print("No items selected. Order canceled.")
            return

        print(f"\nTotal: ${total:.2f}")
        confirm = input("Confirm order? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Order canceled.")
            return

        # Save order
        order_id = str(datetime.now().timestamp()).replace('.', '')[-6:]
        order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(ORDERS_FILE, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([order_id, order_date, ", ".join(order_items), total])

        # Update product stock in file
        with open(PRODUCTS_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Name", "Price", "Stock"])  # Header
            writer.writerows(products)

        print(f"Order placed! Order ID: {order_id}")

    except ValueError:
        print("Invalid input. Please enter a number.")
    except Exception as e:
        print(f"Error: {e}")

def view_order_history():
    """Display past orders."""
    try:
        with open(ORDERS_FILE, 'r') as file:
            orders = list(csv.reader(file))[1:]  # Skip header

        if not orders:
            print("No orders found.")
            return

        print("\n--- Order History ---")
        for order in orders:
            print(f"Order ID: {order[0]}")
            print(f"Date: {order[1]}")
            print(f"Items: {order[2]}")
            print(f"Total: ${order[3]}\n")

    except FileNotFoundError:
        print("No order history found.")

def admin_mode():
    """Admin functions (add/remove products, view sales)."""
    password = input("Enter admin password: ").strip()
    if password != "admin123":  # Simple password (change in real use)
        print("Access denied.")
        return

    while True:
        print("\n--- Admin Mode ---")
        print("1. Add New Product")
        print("2. Update Product Stock")
        print("3. View Sales Report")
        print("4. Exit Admin Mode")

        choice = input("Enter choice: ").strip()
        if choice == '1':
            add_new_product()
        elif choice == '2':
            update_product_stock()
        elif choice == '3':
            view_sales_report()
        elif choice == '4':
            break
        else:
            print("Invalid choice.")

def add_new_product():
    """Add a new product to the inventory."""
    try:
        name = input("Enter product name: ").strip()
        price = float(input("Enter price: "))
        stock = int(input("Enter initial stock: "))

        with open(PRODUCTS_FILE, 'a', newline='') as file:
            writer = csv.writer(file)
            product_id = str(len(list(csv.reader(open(PRODUCTS_FILE)))) - 1)  # Auto-generate ID
            writer.writerow([product_id, name, price, stock])

        print(f"Added {name} to inventory.")

    except ValueError:
        print("Invalid input. Please enter numbers for price and stock.")

def update_product_stock():
    """Update product stock."""
    view_products()
    product_id = input("Enter product ID to update: ").strip()
    new_stock = int(input("Enter new stock: "))

    try:
        with open(PRODUCTS_FILE, 'r') as file:
            products = list(csv.reader(file))

        found = False
        for row in products[1:]:  # Skip header
            if row[0] == product_id:
                row[3] = str(new_stock)
                found = True
                break

        if not found:
            print("Product not found.")
            return

        with open(PRODUCTS_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(products)

        print("Stock updated successfully.")

    except ValueError:
        print("Invalid stock value.")
    except Exception as e:
        print(f"Error: {e}")

def view_sales_report():
    """Display total sales."""
    try:
        with open(ORDERS_FILE, 'r') as file:
            orders = list(csv.reader(file))[1:]  # Skip header

        if not orders:
            print("No sales yet.")
            return

        total_sales = sum(float(order[3]) for order in orders)
        print(f"\nTotal Sales: ${total_sales:.2f}")

    except FileNotFoundError:
        print("No sales data found.")

def main():
    """Main program loop."""
    initialize_files()
    while True:
        display_menu()
        choice = input("Enter choice (1-5): ").strip()
        if choice == '1':
            view_products()
        elif choice == '2':
            place_order()
        elif choice == '3':
            view_order_history()
        elif choice == '4':
            admin_mode()
        elif choice == '5':
            print("Exiting. Thank you!")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()