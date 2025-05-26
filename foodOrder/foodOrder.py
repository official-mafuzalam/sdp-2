import csv
from datetime import datetime
import os

# File paths
MENU_FILE = "menu.csv"
ORDERS_FILE = "orders.csv"

def initialize_files():
    """Create CSV files if they don't exist."""
    if not os.path.exists(MENU_FILE):
        with open(MENU_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Item", "Price", "Available"])

    if not os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["OrderID", "Date", "Items", "Total"])

def display_menu():
    """Display the main menu."""
    print("\n=== Campus Cafeteria Ordering System ===")
    print("1. View Menu")
    print("2. Place Order")
    print("3. View Order History")
    print("4. Admin Mode")
    print("5. Exit")

def view_menu():
    """Display all available food items."""
    try:
        with open(MENU_FILE, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            print("\n--- Menu ---")
            for row in reader:
                if row[3] == "True":
                    print(f"{row[0]}. {row[1]} - ${row[2]}")
    except FileNotFoundError:
        print("Menu not found. Please contact admin.")

def place_order():
    """Place a new food order."""
    try:
        with open(MENU_FILE, 'r') as file:
            menu = list(csv.reader(file))[1:]  # Skip header

        order_items = []
        total = 0.0

        while True:
            view_menu()
            item_id = input("Enter item ID (or 'done' to finish): ").strip()
            if item_id.lower() == 'done':
                break

            found = False
            for item in menu:
                if item[0] == item_id and item[3] == "True":
                    order_items.append(item[1])
                    total += float(item[2])
                    found = True
                    print(f"Added {item[1]} to order.")
                    break

            if not found:
                print("Invalid item ID or item not available.")

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

        print(f"Order placed! Order ID: {order_id}")

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
    """Admin functions (add/remove items, view sales)."""
    password = input("Enter admin password: ").strip()
    if password != "admin123":  # Simple password (change in real use)
        print("Access denied.")
        return

    while True:
        print("\n--- Admin Mode ---")
        print("1. Add New Item")
        print("2. Update Item Availability")
        print("3. View Sales Report")
        print("4. Exit Admin Mode")

        choice = input("Enter choice: ").strip()
        if choice == '1':
            add_new_item()
        elif choice == '2':
            update_item_availability()
        elif choice == '3':
            view_sales_report()
        elif choice == '4':
            break
        else:
            print("Invalid choice.")

def add_new_item():
    """Add a new food item to the menu."""
    try:
        item_name = input("Enter item name: ").strip()
        price = float(input("Enter price: "))
        available = input("Available? (y/n): ").strip().lower() == 'y'

        with open(MENU_FILE, 'a', newline='') as file:
            writer = csv.writer(file)
            item_id = str(len(list(csv.reader(open(MENU_FILE)))) - 1)  # Auto-generate ID
            writer.writerow([item_id, item_name, price, available])

        print(f"Added {item_name} to the menu.")

    except ValueError:
        print("Invalid price. Please enter a number.")

def update_item_availability():
    """Toggle item availability (True/False)."""
    view_menu()
    item_id = input("Enter item ID to update: ").strip()

    try:
        with open(MENU_FILE, 'r') as file:
            menu = list(csv.reader(file))

        found = False
        for row in menu[1:]:  # Skip header
            if row[0] == item_id:
                current_status = row[3]
                new_status = "False" if current_status == "True" else "True"
                row[3] = new_status
                found = True
                break

        if not found:
            print("Item not found.")
            return

        with open(MENU_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(menu)

        print("Item availability updated.")

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
            view_menu()
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