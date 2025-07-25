import tkinter as tk
from tkinter import messagebox, simpledialog
import serial
import threading
import mysql.connector

# Create a connection to the MySQL database
db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root@123",
    database="Test_Retail"
)

# Create a cursor object to interact with the database
db_cursor = db_connection.cursor()

# Configure Arduino communication settings
arduino_port = 'COM9'
baud_rate = 9600

# Establish communication with Arduino
arduino = serial.Serial(arduino_port, baud_rate, timeout=1)

# Define mapping of RFID UIDs to product names
uid_to_product = {
    "C3C86842": "Milk",
    "037F3F43": "Bread",
    "03385043": "Eggs",
    "D30EE042": "Cereal",
    "F3BDE442": "Juice"
}

# Information about products including price and description
products = {
    "Milk": {"price": 30.00, "description": "Fresh, locally sourced dairy essential for a healthy diet."},
    "Eggs": {"price": 80.00, "description": "One Dozen of Grade A eggs, a high-quality protein source perfect for breakfast and baking."},
    "Bread": {"price": 40.00, "description": "Soft and delicious freshly baked bread, ideal for sandwiches and toasts."},
    "Cereal": {"price": 140.00, "description": "Nutritious breakfast cereal, rich in vitamins and fiber, a great way to start your day."}
}

# Shopping list with predefined items
shopping_list = [
    {"item": "Milk", "quantity": "0.5 Litre", "checked": False},
    {"item": "Eggs", "quantity": "0.3 kg", "checked": False},
    {"item": "Bread", "quantity": "0.4 kg", "checked": False},
    {"item": "Cereal", "quantity": "1.0 kg", "checked": False}
]

# Green color for GUI buttons
green_color = "#4CAF50"

# GUI class for the Smart Shopping Cart
class MyCustomGUI:
    def __init__(self, root):
        # Initialize the GUI window
        self.root = root
        self.root.title("Smart Shopping Cart")
        self.root.configure(bg='white')

        # Initialize variables for scanned products and total amount
        self.scanned_products = []
        self.total_amount = tk.DoubleVar()

        # Create buttons for each product
        self.product_buttons = []
        for product_name, product_info in products.items():
            product_button = tk.Button(root, text=f"{product_name}: ₹{product_info['price']:.2f}",
                                       command=lambda name=product_name: self.add_to_cart(name), bg=green_color, fg='white')
            self.product_buttons.append(product_button)

        # Create text field for displaying the shopping cart
        self.cart_display = tk.Text(root, height=15, width=40, bg='white')
        # Create buttons for checkout and viewing the shopping list
        self.checkout_button = tk.Button(root, text="Checkout", command=self.open_checkout_window, bg=green_color, fg='white')
        self.shopping_list_button = tk.Button(root, text="Shopping List", command=self.open_shopping_list_window, bg=green_color, fg='white')

        # Place GUI elements in the layout
        for i in range(len(self.product_buttons)):
            self.product_buttons[i].grid(row=i, column=0, padx=10, pady=5)
            description_label = tk.Label(root, text=products[list(products.keys())[i]]["description"], bg='white')
            description_label.grid(row=i, column=1, padx=10, pady=5)

        self.cart_display.grid(row=len(products), column=0, columnspan=3, padx=10, pady=10)
        self.checkout_button.grid(row=len(products) + 1, column=0, columnspan=3, padx=10, pady=10)
        self.shopping_list_button.grid(row=len(products) + 2, column=0, padx=10, pady=10)

        # Create a separate thread for Arduino communication
        self.serial_thread = threading.Thread(target=self.setup_serial)
        self.serial_thread.start()

    def setup_serial(self):
        try:
            while True:
                # Read RFID data from Arduino
                # arduino_data = arduino.readline().decode().strip()
                arduino_data = arduino.readline().decode('latin1').strip()

                # Process RFID data
                if arduino_data.startswith("Scanned RFID Tag:"):
                    uid_info = arduino_data.split(":")[1].strip().split()
                    uid = ''.join(uid_info)

                    # Check if the item is already in the cart
                    existing_item_index = next((i for i, item in enumerate(self.scanned_products) if item['uid'] == uid), None)

                    if existing_item_index is not None:
                        product_name = self.scanned_products[existing_item_index]['product_name']
                        self.remove_from_cart(uid, product_name)
                        self.update_inventory(product_name, 1)
                        print(f"Inventory updated: {product_name} +1. Remaining quantity: {self.get_inventory_quantity(product_name)}")

                        if product_name == "Milk":
                            self.root.after(0, lambda: self.recommend_cereal())

                    else:
                        product_name = uid_to_product.get(uid, 'Unknown Product')
                        self.add_to_cart(product_name, uid)
                        self.update_inventory(product_name, -1)
                        print(f"Inventory updated: {product_name} -1. Remaining quantity: {self.get_inventory_quantity(product_name)}")

                    self.root.after(0, self.update_cart_display)

        except KeyboardInterrupt:
            print("Program terminated by user.")
        finally:
            arduino.close()

    def recommend_cereal(self):
        recommendation_popup = tk.Toplevel(self.root)
        recommendation_popup.title("Recommended Product")
        recommendation_popup.geometry("300x100")

        recommendation_label = tk.Label(recommendation_popup, text="We recommend adding Cereal to your cart!", padx=20, pady=20)
        recommendation_label.pack()

        # Update the cart display
        self.root.after(5000, recommendation_popup.destroy)

    def get_inventory_quantity(self, product_name):
        try:
            query_select = "SELECT quantity FROM products WHERE name = %s"
            db_cursor.execute(query_select, (product_name,))
            current_quantity = db_cursor.fetchone()[0]
            return current_quantity

        except mysql.connector.Error as err:
            print(f"Error fetching inventory quantity: {err}")
            return 0

    def add_to_cart(self, product_name, uid):
        self.scanned_products.append({'product_name': product_name, 'uid': uid})
        self.root.after(0, self.update_cart_display)

        if product_name == "Milk":
            self.root.after(0, lambda: self.recommend_cereal())

    def remove_from_cart(self, uid, product_name):
        self.scanned_products[:] = [item for item in self.scanned_products if item['uid'] != uid]
        self.update_inventory(product_name, 1)  # Increase the inventory when an item is removed
        self.root.after(0, self.update_cart_display)

    def update_cart_display(self):
        self.cart_display.delete(1.0, tk.END)
        total_price = 0

        for item in self.scanned_products:
            product_name, uid = item['product_name'], item['uid']
            quantity = sum(1 for i in self.scanned_products if i['uid'] == uid)
            price = products[product_name]['price']

            self.cart_display.insert(tk.END, f"{product_name} (Qty: {quantity}): ₹{price * quantity:.2f}\n")

            remove_button = tk.Button(self.cart_display, text="Remove", command=lambda uid=uid, product_name=product_name: self.remove_from_cart(uid, product_name))
            self.cart_display.window_create(tk.END, window=remove_button)
            self.cart_display.insert(tk.END, "\n")

            total_price += price * quantity

        total_with_tax = total_price * 1.16
        if getattr(self, "discount_applied", False):
            total_with_tax *= (1 - self.discount_percentage)

        self.cart_display.insert(tk.END, f"\nTotal (with 16% tax): ₹{total_with_tax:.2f}\n")

    def open_shopping_list_window(self):
        shopping_list_str = "\n".join([f"{item['item']} ({item['quantity']})" for item in shopping_list])
        messagebox.showinfo("Shopping List", shopping_list_str)

    def update_inventory(self, product_name, quantity_change):
        try:
            query_select = "SELECT quantity FROM products WHERE name = %s"
            db_cursor.execute(query_select, (product_name,))
            current_quantity = db_cursor.fetchone()[0]

            query_update = "UPDATE products SET quantity = %s WHERE name = %s"
            new_quantity = max(0, current_quantity + quantity_change)
            db_cursor.execute(query_update, (new_quantity, product_name))
            db_connection.commit()

            print(f"Inventory updated: {product_name} {quantity_change}. Remaining quantity: {new_quantity}")

        except mysql.connector.Error as err:
            print(f"Error updating inventory: {err}")

    def open_checkout_window(self):
        checkout_window = tk.Toplevel(self.root)
        checkout_window.title("Checkout Options")

        # Discount section
        discount_label = tk.Label(checkout_window, text="Discount Codes:", padx=20, pady=20)
        discount_code_entry = tk.Entry(checkout_window)
        apply_discount_button = tk.Button(checkout_window, text="Apply Discount", command=lambda: self.apply_discount(checkout_window, discount_code_entry), bg=green_color, fg='white')

        # Display available coupon codes
        coupon_label = tk.Label(checkout_window, text="Available Codes: OFF20, OFF30", padx=20, pady=20)

        # Payment section
        payment_label = tk.Label(checkout_window, text="Payment Options:", padx=20, pady=20)
        payment_buttons = [
            tk.Button(checkout_window, text="Cash", command=lambda method="Cash": self.complete_checkout(checkout_window, method)),
            tk.Button(checkout_window, text="Credit Card", command=lambda method="Credit Card": self.complete_checkout(checkout_window, method)),
            tk.Button(checkout_window, text="Debit Card", command=lambda method="Debit Card": self.complete_checkout(checkout_window, method)),
            tk.Button(checkout_window, text="Online", command=lambda method="Online": self.complete_checkout(checkout_window, method))
        ]

        discount_label.grid(row=0, column=0, padx=10, pady=10)
        discount_code_entry.grid(row=0, column=1, padx=10, pady=10)
        apply_discount_button.grid(row=0, column=2, padx=10, pady=10)
        coupon_label.grid(row=0, column=3, padx=10, pady=10)

        payment_label.grid(row=1, column=0, padx=10, pady=10, columnspan=4)

        for i, payment_button in enumerate(payment_buttons):
            payment_button.grid(row=2, column=i, padx=10, pady=10)

    def apply_discount(self, checkout_window, discount_code_entry):
        discount_code = discount_code_entry.get()

        discount_codes = {
            "OFF20": 0.20,
            "OFF30": 0.30
        }

        if discount_code in discount_codes:
            discount_percentage = discount_codes[discount_code]
            self.calculate_discount(checkout_window, discount_percentage)
        else:
            messagebox.showwarning("Invalid Discount Code", "The entered discount code is not valid. Available codes: OFF20, OFF30")

    def calculate_discount(self, checkout_window, discount_percentage):
        self.discount_percentage = discount_percentage
        self.discount_applied = True
        total_price = sum(products[item['product_name']]['price'] for item in self.scanned_products)
        discounted_amount = total_price * self.discount_percentage
        new_total_price = total_price - discounted_amount

        discount_info = f"\nDiscount Applied: {discount_percentage * 100}%\nDiscount Amount: ₹{discounted_amount:.2f}\nNew Total Amount: ₹{new_total_price:.2f}"

        messagebox.showinfo("Discount Applied", f"A {discount_percentage * 100}% discount has been applied.{discount_info}")
        self.root.after(0, self.update_cart_display)

    def complete_checkout(self, checkout_window, payment_method):
        total_price = sum(products[item['product_name']]['price'] for item in self.scanned_products)

        # Check if a discount is applied
        discount_applied = getattr(self, "discount_applied", False)
        if discount_applied:
            total_price *= (1 - self.discount_percentage)

        total_with_tax = total_price * 1.16
        messagebox.showinfo("Checkout", f"Total amount with tax: ₹{total_with_tax:.2f}\nPayment Method: {payment_method}")
        self.scanned_products.clear()
        self.discount_applied = False  # Reset discount_applied flag
        self.root.after(0, self.update_cart_display)

# Main program
if __name__ == "__main__":
    root = tk.Tk()
    app = MyCustomGUI(root)
    root.mainloop()