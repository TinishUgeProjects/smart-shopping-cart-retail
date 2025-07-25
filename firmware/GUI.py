import tkinter as tk
from tkinter import simpledialog
from tkinter import ttk

# Create the main window
root = tk.Tk()
root.title("Smart Shopping Cart")
root.configure(bg='white')  # Set the main window background color to white

# Define colors
green_color = "#4CAF50"  # A shade of green

# Initialize variables to store product information
products = {
    "Milk": {"price": 30.00, "description": "Fresh, locally sourced dairy essential for a healthy diet."},
    "Eggs": {"price": 80.00, "description": "One Dozen of Grade A eggs, a high-quality protein source perfect for breakfast and baking."},
    "Bread": {"price": 40.00, "description": "Soft and delicious freshly baked bread, ideal for sandwiches and toasts."},
    "Cereal": {"price": 140.00, "description": "Nutritious breakfast cereal, rich in vitamins and fiber, a great way to start your day."}
}

cart = []

# Initialize the shopping list with the scanning items and quantities in kgs
shopping_list = [
    {"item": "Milk", "quantity": "1 Litre", "checked": False},
    {"item": "Eggs", "quantity": "0.5 kg", "checked": False},
    {"item": "Bread", "quantity": "0.5 kg", "checked": False},
    {"item": "Cereal", "quantity": "1.0 kg", "checked": False}
]

# Create a global variable for shopping_list_display
shopping_list_display = None

# Function to add a product to the cart
def add_to_cart(product_name, product_price):
    cart.append((product_name, product_price))
    update_cart_display()

# Function to remove a product from the cart
def remove_from_cart(product_name):
    cart[:] = [item for item in cart if item[0] != product_name]
    update_cart_display()

# Function to update the cart display
def update_cart_display():
    cart_display.delete(1.0, tk.END)  # Clear the existing text
    total_price = 0

    for item in cart:
        product_name, product_price = item
        cart_display.insert(tk.END, f"{product_name}: ₹{product_price:.2f}\n")

        # Add a "Remove" button for each item in the cart
        remove_button = tk.Button(cart_display, text="Remove", command=lambda name=product_name: remove_from_cart(name))
        cart_display.window_create(tk.END, window=remove_button)
        cart_display.insert(tk.END, "\n")  # Add a line break to separate items

        total_price += product_price

    # Calculate total price with tax (16%)
    total_with_tax = total_price * 1.16
    cart_display.insert(tk.END, f"\nTotal (with 16% tax): ₹{total_with_tax:.2f}\n")

# Function to handle the checkout process
def checkout():
    # Create a new window for payment options with increased size
    payment_window = tk.Toplevel(root)
    payment_window.title("Payment Options")
    payment_window.geometry("400x200")  # Set the dimensions (width x height)

    # Function to handle payment confirmation
    def confirm_payment(payment_option):
        # Calculate the total amount with tax
        total_price = sum(item[1] for item in cart)
        total_with_tax = total_price * 1.16

        # Display a confirmation message on a separate popup window with increased size
        confirmation_popup = tk.Toplevel(root)
        confirmation_popup.title("Thank You!")
        confirmation_popup.geometry("400x200")  # Set the dimensions (width x height)

        confirmation_message = f"Thank you for your purchase!\nTotal amount with tax: ₹{total_with_tax:.2f}\nPayment method: {payment_option}"
        confirmation_label = tk.Label(confirmation_popup, text=confirmation_message)
        confirmation_label.pack()

    # Payment options
    payment_options = ["Credit Card", "Debit Card", "PayPal", "Cash"]
    for option in payment_options:
        payment_button = tk.Button(payment_window, text=option, command=lambda opt=option: confirm_payment(opt))
        payment_button.pack()

# Function to add an item to the shopping list
def add_to_shopping_list():
    item = simpledialog.askstring("Add to Shopping List", "Enter an item to add to your shopping list:")
    if item:
        shopping_list.append({"item": item, "quantity": "1 kg", "checked": False})
        update_shopping_list_display()

# Function to update the shopping list display
def update_shopping_list_display():
    global shopping_list_display  # Access the global variable
    shopping_list_display.delete(1.0, tk.END)  # Clear the existing text
    for i, item_info in enumerate(shopping_list, start=1):
        item = item_info["item"]
        quantity = item_info["quantity"]
        checked = item_info["checked"]
        checkbox = "[X]" if checked else "[ ]"
        shopping_list_display.insert(tk.END, f"{i}. {checkbox} {item} ({quantity})\n")

# Function to open the shopping list window
def open_shopping_list_window():
    global shopping_list_display  # Access the global variable
    shopping_list_window = tk.Toplevel(root)
    shopping_list_window.title("Shopping List")

    # Create the Shopping List display
    shopping_list_display = tk.Text(shopping_list_window, height=10, width=40)
    shopping_list_display.pack()

    # Update the shopping list display in the new window
    update_shopping_list_display()

# Create and configure GUI elements with green color
product_buttons = []
for product_name, product_info in products.items():
    product_button = tk.Button(root, text=f"{product_name}: ₹{product_info['price']:.2f}", command=lambda name=product_name, price=product_info["price"]: add_to_cart(name, price), bg=green_color, fg='white')
    product_buttons.append(product_button)

cart_display = tk.Text(root, height=15, width=40, bg='white')  # Set the cart display background color to white
checkout_button = tk.Button(root, text="Checkout", command=checkout, bg=green_color, fg='white')

# Shopping List button with green color
shopping_list_button = tk.Button(root, text="Shopping List", command=open_shopping_list_window, bg=green_color, fg='white')

# Arrange GUI elements using grid layout
for i in range(len(product_buttons)):
    product_buttons[i].grid(row=i, column=0, padx=10, pady=5)
    description_label = tk.Label(root, text=products[list(products.keys())[i]]["description"], bg='white')
    description_label.grid(row=i, column=1, padx=10, pady=5)

cart_display.grid(row=len(products), column=0, columnspan=3, padx=10, pady=10)  # Adjusted the columnspan
checkout_button.grid(row=len(products) + 1, column=0, columnspan=3, padx=10, pady=10)  # Adjusted the columnspan

# Place the Shopping List button
shopping_list_button.grid(row=len(products) + 2, column=0, padx=10, pady=10)

# Start the GUI main loop
root.mainloop()
