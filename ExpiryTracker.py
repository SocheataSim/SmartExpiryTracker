import customtkinter as ctk
import pandas as pd
import os
from datetime import datetime
from tabulate import tabulate
from tkinter import simpledialog, messagebox
from tkcalendar import Calendar
class SmartGroceryTrackerUI:
    def __init__(self, root, filename='grocery_data.csv'):
        self.filename = filename
        self.load_data()
        self.root = root

        # Set the window size and appearance
        root.title("Smart Grocery Expiry Tracker")
        root.geometry("800x500")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Configure root grid layout for responsiveness
        root.grid_rowconfigure(1, weight=1)      
        root.grid_columnconfigure(0, weight=1)   
        root.protocol("WM_DELETE_WINDOW", self.on_closing)
        # --- Top Controls (Search + Button + Dropdown) ---
        top_frame = ctk.CTkFrame(root)
        top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        top_frame.grid_columnconfigure(0, weight=1)
        top_frame.grid_columnconfigure(1, weight=0)
        top_frame.grid_columnconfigure(2, weight=0)

        # Search Entry
        self.search_entry = ctk.CTkEntry(top_frame, placeholder_text="Search item...")
        self.search_entry.grid(row=0, column=0, padx=5, sticky="ew")

        # Search Button
        self.search_button = ctk.CTkButton(top_frame, text="Search", command=self.search_item)
        self.search_button.grid(row=0, column=1, padx=5)

        # Dropdown Menu
        self.function_var = ctk.StringVar(value="Menu")
        self.function_menu = ctk.CTkOptionMenu(top_frame, variable=self.function_var, values=[
        "Add Item", "Display Items", "Check Expiry", "Sort Items", "Filter by Category",
        "Check Low Stock", "Update Quantity"
        ], command=self.handle_function)
        self.function_menu.grid(row=0, column=2, padx=5)

        # --- Main Frame (Textbox + Scrollbar) ---
        self.frame = ctk.CTkFrame(root, corner_radius=10)
        self.frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

        # Textbox for Display
        self.textbox = ctk.CTkTextbox(self.frame, width=730, height=380, font=("Courier New", 13))
        self.textbox.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Initialize update fields as None - they will be created only when needed
        self.entry_name = None
        self.entry_quantity = None
        self.quantity_var = None
        self.confirm_button = None
        self.update_frame = None  
        self.minus_btn = None     
        self.plus_btn = None      
        
        # Exit Button 
        exit_button = ctk.CTkButton(root, 
                         text="Exit", 
                         fg_color="#bf3a3a",  # Red color
                         hover_color="#8f2b2b",  
                         command=self.on_closing)  
        exit_button.grid(row=2, column=0, pady=(0, 10), padx=10, sticky="se")
       
        self.display_items()
        
        # Check for alerts (low stock and expiring items) on startup
        root.after(500, self.check_alerts)  # Add small delay to ensure UI is fully loaded first

    def on_closing(self):
        """Handle window closing event with confirmation dialog."""
        if messagebox.askokcancel("Exit", "Are you sure you want to exit the application?"):
            self.root.destroy()
    def check_alerts(self):
        """Check for low stock and expiring items on startup and show alerts if needed."""
        if self.df.empty:
            return  # No data to check
        
        alerts = []
        
        # Check for low stock items (quantity <= 2)
        try:
            # Convert quantity column to numeric to ensure proper comparison
            self.df['Quantity'] = pd.to_numeric(self.df['Quantity'], errors='coerce')
            low_stock_items = self.df[self.df['Quantity'] <= 2]
            
            if not low_stock_items.empty:
                if len(low_stock_items) == 1:
                    alerts.append(f"⚠️ 1 item is running low on stock")
                else:
                    alerts.append(f"⚠️ {len(low_stock_items)} items are running low on stock")
        except Exception as e:
            print(f"Error checking low stock: {e}")
        
        # Check for expiring items (3 days or less)
        try:
            
            self.df["Expiry_Date"] = pd.to_datetime(self.df["Expiry_Date"], errors='coerce')
            today = pd.Timestamp.now()
            self.df["Days_To_Expiry"] = (self.df["Expiry_Date"] - today).dt.days
            
            # Find items expiring soon (within 3 days) or already expired
            expiring_soon = self.df[(self.df["Days_To_Expiry"] >= 0) & (self.df["Days_To_Expiry"] <= 3)]
            expired_items = self.df[self.df["Days_To_Expiry"] < 0]
            
            if not expiring_soon.empty:
                if len(expiring_soon) == 1:
                    alerts.append(f"⚠️ 1 item is expiring within 3 days")
                else:
                    alerts.append(f"⚠️ {len(expiring_soon)} items are expiring within 3 days")
            
            if not expired_items.empty:
                if len(expired_items) == 1:
                    alerts.append(f"❌ 1 item has already expired")
                else:
                    alerts.append(f"❌ {len(expired_items)} items have already expired")
        except Exception as e:
            print(f"Error checking expiry dates: {e}")
        
        # If there are alerts, show them to the user
        if alerts:
            alert_message = "\n".join(alerts)
            alert_message += "\n\nWould you like to view the details?"
            
            show_details = messagebox.askyesno("Important Alerts", alert_message)
            
            if show_details:
                # Show the detailed alerts
                self.show_detailed_alerts(low_stock_items, expiring_soon, expired_items)  
    def show_detailed_alerts(self, low_stock_items, expiring_soon, expired_items):
        """Show detailed information about alerts in the main textbox."""
        self.textbox.delete("1.0", "end")
        self.textbox.insert("end", "🚨 GROCERY ALERTS 🚨\n")
        self.textbox.insert("end", "=" * 50 + "\n\n")
        
        # Show low stock items
        if not low_stock_items.empty:
            self.textbox.insert("end", "📉 LOW STOCK ITEMS:\n")
            self.textbox.insert("end", "-" * 50 + "\n")
            
            for _, row in low_stock_items.iterrows():
                self.textbox.insert("end", f"• {row['Name']} - Quantity: {row['Quantity']}\n")
            
            self.textbox.insert("end", "\n")
        
        # Show expiring soon items
        if not expiring_soon.empty:
            self.textbox.insert("end", "⏳ EXPIRING SOON (WITHIN 3 DAYS):\n")
            self.textbox.insert("end", "-" * 50 + "\n")
            
            for _, row in expiring_soon.iterrows():
                days = int(row["Days_To_Expiry"])
                day_text = "today" if days == 0 else f"in {days} day{'s' if days != 1 else ''}"
                self.textbox.insert("end", f"• {row['Name']} - Expires {day_text} ({row['Expiry_Date'].strftime('%Y-%m-%d')})\n")
            
            self.textbox.insert("end", "\n")
        
        # Show expired items
        if not expired_items.empty:
            self.textbox.insert("end", "🛑 EXPIRED ITEMS:\n")
            self.textbox.insert("end", "-" * 50 + "\n")
            
            for _, row in expired_items.iterrows():
                days = abs(int(row["Days_To_Expiry"]))
                self.textbox.insert("end", f"• {row['Name']} - Expired {days} day{'s' if days != 1 else ''} ago ({row['Expiry_Date'].strftime('%Y-%m-%d')})\n")
            
            self.textbox.insert("end", "\n")
        
        self.textbox.insert("end", "=" * 50 + "\n")
        self.textbox.insert("end", "Use the menu options above to manage these items.")  
    def load_data(self):
        """Loads existing data or creates a new CSV file if not found."""
        # Define expected columns
        expected_columns = ['Name', 'Quantity', 'Category', 'Compartment', 'Expiry_Date']
        
        if os.path.exists(self.filename):
            self.df = pd.read_csv(self.filename)
            
            
            unwanted_columns = [col for col in self.df.columns if col not in expected_columns]
            if unwanted_columns:
                self.df = self.df.drop(columns=unwanted_columns)
                
            # Ensure all expected columns exist
            for col in expected_columns:
                if col not in self.df.columns:
                    self.df[col] = ''
        else:
            self.df = pd.DataFrame(columns=expected_columns)
        
        # Save the cleaned dataframe
        self.df.to_csv(self.filename, index=False)

    def save_data(self):
        """Saves the DataFrame to CSV."""
        self.df.to_csv(self.filename, index=False)

    def display_items(self):
        """Displays all items in a clean tabular format without grid lines."""
        self.textbox.delete("1.0", "end")

        if self.df.empty:
            self.textbox.insert("end", "No items found.\n")
        else:
            # Header - adjust column widths and add proper spacing
            header = f"{'Name':<20}{'Quantity':<12}{'Category':<15}{'Compartment':<20}{'Expiry Date'}\n"
            self.textbox.insert("end", header)
            self.textbox.insert("end", "-" * 75 + "\n")  # Adjusted length of separator line

            # Convert expiry_date to datetime if it's not already
            try:
                self.df['Expiry_Date'] = pd.to_datetime(self.df['Expiry_Date'], errors='coerce')
            except:
                pass  

            # Rows
            for _, row in self.df.iterrows():
                # Format expiry date nicely if it's a datetime, otherwise use as is
                expiry_date = row['Expiry_Date']
                if isinstance(expiry_date, pd.Timestamp):
                    expiry_formatted = expiry_date.strftime('%Y-%m-%d')
                else:
                    expiry_formatted = str(expiry_date)
                
    
                line = f"{str(row['Name']):<20}{str(row['Quantity']):<12}{str(row['Category']):<15}{str(row['Compartment']):<20}{expiry_formatted}\n"
                self.textbox.insert("end", line) 

    def search_item(self):
        """Searches for an item by name."""
        search_name = self.search_entry.get().strip().lower()
        
        self.df['Name'] = self.df['Name'].fillna('').astype(str)
        
        # Perform the search
        results = self.df[self.df['Name'].str.lower().str.contains(search_name, na=False)]
        
        results = results.copy()
        
        if 'Days_To_Expiry' in results.columns:
            results = results.drop(columns=['Days_To_Expiry'])
        
        if 'Expiry_Date' in results.columns:
          
            if pd.api.types.is_datetime64_any_dtype(results['Expiry_Date']):
                results['Expiry_Date'] = results['Expiry_Date'].dt.strftime('%Y-%m-%d')
        
        # Clear the textbox
        self.textbox.delete("1.0", "end")
        
        # Show results
        if results.empty:
            self.textbox.insert("end", f"No items found matching '{search_name}'.\n")
        else:
            self.textbox.insert("end", tabulate(results, headers='keys', tablefmt='plain'))

    def handle_function(self, choice):
        """Calls the selected function from the dropdown menu."""
        
        self.clear_update_ui()
        
        if choice == "Add Item":
            self.add_item()
        elif choice == "Display Items":
            self.display_items()
        elif choice == "Check Expiry":
            self.check_expiry()
        elif choice == "Sort Items":
            self.sort_items()
        elif choice == "Filter by Category":
            self.filter_items()
        elif choice == "Check Low Stock":
            self.check_low_stock()
        elif choice == "Update Quantity":
            self.show_update_shopping_list_ui()
    
    
    def add_item(self):
        # Define standard categories
        categories = ["Food", "Vegetable", "Drink", "Fruit", "Dessert and Cake", "Snack", "Meat", "Other"]
        
        # Define standard compartments
        compartments = ["Refrigerator", "Freezer", "Pantry", "Kitchen Cabinet", "Counter Top", "Other"]
        
        # Create popup window
        popup = ctk.CTkToplevel()
        popup.title("Add New Item")
        popup.geometry("400x550")  # Increased height to accommodate calendar
        popup.grab_set()  # Make it modal to prevent interaction with main window

        form_frame = ctk.CTkFrame(popup)
        form_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Entry fields
        name_entry = ctk.CTkEntry(form_frame, width=300, placeholder_text="Name")
        name_entry.pack(pady=5)

        quantity_entry = ctk.CTkEntry(form_frame, width=300, placeholder_text="Quantity")
        quantity_entry.pack(pady=5)

        # Category dropdown instead of text entry
        category_var = ctk.StringVar(value=categories[0])
        category_label = ctk.CTkLabel(form_frame, text="Category:")
        category_label.pack(pady=(5, 0), anchor="w", padx=10)
        
        category_dropdown = ctk.CTkOptionMenu(form_frame, variable=category_var, values=categories, width=300)
        category_dropdown.pack(pady=5)

        # Custom category entry - shown when "Other" is selected
        custom_category_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        custom_category_entry = ctk.CTkEntry(custom_category_frame, width=300, placeholder_text="Enter custom category")
        
        def on_category_change(choice):
            if choice == "Other":
                custom_category_frame.pack(pady=0)
                custom_category_entry.pack(fill="x")
            else:
                custom_category_frame.pack_forget()
        
        # Bind the category change event
        category_dropdown.configure(command=on_category_change)

        # Compartment dropdown instead of text entry
        compartment_var = ctk.StringVar(value=compartments[0])
        compartment_label = ctk.CTkLabel(form_frame, text="Compartment:")
        compartment_label.pack(pady=(5, 0), anchor="w", padx=10)
        
        compartment_dropdown = ctk.CTkOptionMenu(form_frame, variable=compartment_var, values=compartments, width=300)
        compartment_dropdown.pack(pady=5)

        # Custom compartment entry - shown when "Other" is selected
        custom_compartment_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        custom_compartment_entry = ctk.CTkEntry(custom_compartment_frame, width=300, placeholder_text="Enter custom compartment")
        
        def on_compartment_change(choice):
            if choice == "Other":
                custom_compartment_frame.pack(pady=0)
                custom_compartment_entry.pack(fill="x")
            else:
                custom_compartment_frame.pack_forget()
        
        # Bind the compartment change event
        compartment_dropdown.configure(command=on_compartment_change)

        # Expiry date field and storage variable
        expiry_var = ctk.StringVar()  # Store the selected date
        expiry_entry = ctk.CTkEntry(form_frame, width=300, placeholder_text="Expiry Date (YYYY-MM-DD)", 
                                textvariable=expiry_var)
        expiry_entry.pack(pady=5)

        # Create a frame for the calendar
        calendar_frame = ctk.CTkFrame(form_frame)
        cal = Calendar(calendar_frame, selectmode='day', date_pattern='yyyy-mm-dd')
        cal.pack(pady=10)
        
        # Calendar visibility state
        calendar_visible = False
        
        def toggle_calendar():
            nonlocal calendar_visible
            if calendar_visible:
                calendar_frame.pack_forget()
                calendar_button.configure(text="📅")
            else:
                calendar_frame.pack(pady=10)
                calendar_button.configure(text="▲")
            calendar_visible = not calendar_visible
        
        def select_date(event):
            selected_date = cal.selection_get()
            selected_date_str = selected_date.strftime("%Y-%m-%d")
            expiry_var.set(selected_date_str)  # Set the date to our StringVar
            # Optionally hide calendar after selection
            if calendar_visible:
                toggle_calendar()
        
        # Bind the calendar selection event
        cal.bind("<<CalendarSelected>>", select_date)
        
        # Calendar toggle button
        calendar_button = ctk.CTkButton(form_frame, text="📅", width=40, command=toggle_calendar)
        calendar_button.pack(pady=5)

        def submit():
            name = name_entry.get().strip()
            quantity = quantity_entry.get().strip()
            
            # Get category from dropdown or custom entry
            selected_category = category_var.get()
            if selected_category == "Other":
                category = custom_category_entry.get().strip()
                if not category:
                    messagebox.showwarning("Input Error", "Please enter a custom category.")
                    return
            else:
                category = selected_category
            
            # Get compartment from dropdown or custom entry
            selected_compartment = compartment_var.get()
            if selected_compartment == "Other":
                compartment = custom_compartment_entry.get().strip()
                if not compartment:
                    messagebox.showwarning("Input Error", "Please enter a custom compartment.")
                    return
            else:
                compartment = selected_compartment
                
            expiry_date = expiry_var.get().strip()  # Get from our StringVar

            if not all([name, quantity, category, compartment, expiry_date]):
                messagebox.showwarning("Input Error", "All fields are required.")
                return

            try:
                quantity = int(quantity)
            except ValueError:
                messagebox.showwarning("Input Error", "Quantity must be an integer.")
                return

            # Create a new dictionary with the correct number of columns
            new_item = {}
            for col in self.df.columns:
                if col == 'Name':
                    new_item[col] = name
                elif col == 'Quantity':
                    new_item[col] = quantity
                elif col == 'Category':
                    new_item[col] = category
                elif col == 'Compartment':
                    new_item[col] = compartment
                elif col == 'Expiry_Date':
                    new_item[col] = expiry_date
                else:
                    # For any extra columns, set a default value
                    new_item[col] = ''
                    
            # Convert to DataFrame and concatenate
            new_data = pd.DataFrame([new_item])
            self.df = pd.concat([self.df, new_data], ignore_index=True)
            
            self.save_data()
            self.display_items()
            messagebox.showinfo("Success", "Item added successfully!")
            popup.destroy()

        ctk.CTkButton(popup, text="Add Item", command=submit).pack(pady=10)
    def check_expiry(self):
        """Checks for expired and expiring items."""
        if self.df.empty:
            self.textbox.delete("1.0", "end")
            self.textbox.insert("end", "❌ No items available to check for expiry.\n")
            return
    
        try:
            self.textbox.delete("1.0", "end")
            self.textbox.insert("end", "📅 EXPIRY STATUS OF ALL ITEMS:\n")
            self.textbox.insert("end", "-" * 50 + "\n\n")
            
            # Convert expiry dates to datetime
            self.df["Expiry_Date"] = pd.to_datetime(self.df["Expiry_Date"], errors='coerce')
            today = pd.Timestamp.now()
            self.df["Days_To_Expiry"] = (self.df["Expiry_Date"] - today).dt.days
            
            # Sort by days to expiry (expired items first)
            sorted_df = self.df.sort_values(by="Days_To_Expiry")
            
            # Display expiry status for each item
            for _, row in sorted_df.iterrows():
                expiry_date = row["Days_To_Expiry"]
                item_name = row['Name']
                
                if pd.isnull(expiry_date):
                    status = "⚠️ No expiry date provided"
                elif expiry_date < 0:
                    days = abs(int(expiry_date))
                    status = f"❌ Expired ({days} day{'s' if days != 1 else ''} ago)"
                elif expiry_date == 0:
                    status = " Expires TODAY"
                elif expiry_date <= 3:
                    status = f" Almost expired ({int(expiry_date)} day{'s' if expiry_date != 1 else ''} left)"
                elif expiry_date <= 7:
                    status = f" Expiring Soon ({int(expiry_date)} days left)"
                else:
                    status = f" Fresh ({int(expiry_date)} days left)"
                
                # Format the display line
                if isinstance(row["Expiry_Date"], pd.Timestamp):
                    date_str = row["Expiry_Date"].strftime("%Y-%m-%d")
                else:
                    date_str = "Unknown"
                    
                line = f"{item_name}: {status} (Date: {date_str})\n"
                self.textbox.insert("end", line)
        
        except Exception as e:
            self.textbox.insert("end", f"❌ An error occurred: {e}\n")

    def check_low_stock(self):
        """Checks for low-stock items (quantity <= 2)."""
        try:
            # Convert quantity to numeric to ensure proper comparison
            self.df['Quantity'] = pd.to_numeric(self.df['Quantity'], errors='coerce')
            low_stock_items = self.df[self.df['Quantity'] <= 2]

            self.textbox.delete("1.0", "end")
            
            if low_stock_items.empty:
                self.textbox.insert("end", "✅ No low-stock items found.\n")
            else:
                self.textbox.insert("end", "📉 LOW STOCK ITEMS:\n")
                self.textbox.insert("end", "-" * 50 + "\n\n")
                
                # Display each low stock item 
                for _, row in low_stock_items.iterrows():
                    item_name = row['Name']
                    quantity = int(row['Quantity'])
                    category = row['Category']
                    
                    status = "OUT OF STOCK!" if quantity == 0 else f"Only {quantity} left"
                    
                    line = f"• {item_name} ({category}): {status}\n"
                    self.textbox.insert("end", line)
                
                # Add a note at the bottom
                self.textbox.insert("end", "\n")
                self.textbox.insert("end", "⚠️ Consider restocking these items soon.\n")
        except Exception as e:
            self.textbox.insert("end", f"❌ An error occurred: {e}\n")
    def sort_items(self):
        """Enhanced sorting function with multiple sorting options."""
        if self.df.empty:
            messagebox.showwarning("Warning", "No items available to sort.")
            return

        # Create a custom dialog for selecting sort option
        sort_dialog = ctk.CTkToplevel()
        sort_dialog.title("Sort Items")
        sort_dialog.geometry("400x500")
        sort_dialog.grab_set()  # Make it modal
        
        # Create and configure the frame
        sort_frame = ctk.CTkFrame(sort_dialog)
        sort_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Add label
        ctk.CTkLabel(sort_frame, text="Select how to sort your items:", 
                    font=("Helvetica", 16, "bold")).pack(pady=(0, 20))
        
        # Create scrollable frame for sort options
        scrollable_frame = ctk.CTkScrollableFrame(sort_frame, width=350, height=400)
        scrollable_frame.pack(fill="both", expand=True, pady=5)
        
        # --- Sort by Name ---
        name_frame = ctk.CTkFrame(scrollable_frame)
        name_frame.pack(pady=10, fill="x", padx=5)
        
        ctk.CTkLabel(name_frame, text="Sort by Name", font=("Helvetica", 14, "bold")).pack(pady=5)
        
        # Standard alphabetical sorting
        alpha_btn_frame = ctk.CTkFrame(name_frame, fg_color="transparent")
        alpha_btn_frame.pack(fill="x", pady=5)
        alpha_btn_frame.grid_columnconfigure(0, weight=1)
        alpha_btn_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkButton(
            alpha_btn_frame, 
            text="A → Z", 
            command=lambda: self.sort_by_name_alphabetical(True),
            fg_color="#3a7ebf"
        ).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        ctk.CTkButton(
            alpha_btn_frame, 
            text="Z → A", 
            command=lambda: self.sort_by_name_alphabetical(False),
            fg_color="#3a7ebf"
        ).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Prioritize specific item
        priority_frame = ctk.CTkFrame(name_frame, fg_color="transparent")
        priority_frame.pack(fill="x", pady=5)
        priority_frame.grid_columnconfigure(0, weight=3)
        priority_frame.grid_columnconfigure(1, weight=1)
        
        priority_entry = ctk.CTkEntry(priority_frame, placeholder_text="Enter item name to prioritize")
        priority_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        ctk.CTkButton(
            priority_frame, 
            text="Prioritize", 
            command=lambda: self.sort_with_item_priority(priority_entry.get()),
            fg_color="#3a7ebf"
        ).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # --- Sort by Quantity ---
        quantity_frame = ctk.CTkFrame(scrollable_frame)
        quantity_frame.pack(pady=10, fill="x", padx=5)
        
        ctk.CTkLabel(quantity_frame, text="Sort by Quantity", font=("Helvetica", 14, "bold")).pack(pady=5)
        
        qty_btn_frame = ctk.CTkFrame(quantity_frame, fg_color="transparent")
        qty_btn_frame.pack(fill="x", pady=5)
        qty_btn_frame.grid_columnconfigure(0, weight=1)
        qty_btn_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkButton(
            qty_btn_frame, 
            text="Lowest → Highest", 
            command=lambda: self.sort_by_quantity(True),
            fg_color="#3a7ebf"
        ).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        ctk.CTkButton(
            qty_btn_frame, 
            text="Highest → Lowest", 
            command=lambda: self.sort_by_quantity(False),
            fg_color="#3a7ebf"
        ).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # --- Sort by Category ---
        category_frame = ctk.CTkFrame(scrollable_frame)
        category_frame.pack(pady=10, fill="x", padx=5)
        
        ctk.CTkLabel(category_frame, text="Sort by Category", font=("Helvetica", 14, "bold")).pack(pady=5)
        
        # Button for grouping by category
        ctk.CTkButton(
            category_frame, 
            text="Group Items by Category", 
            command=self.sort_by_category,
            fg_color="#3a7ebf"
        ).pack(pady=5, fill="x", padx=10)
        
        # --- Sort by Compartment ---
        compartment_frame = ctk.CTkFrame(scrollable_frame)
        compartment_frame.pack(pady=10, fill="x", padx=5)
        
        ctk.CTkLabel(compartment_frame, text="Sort by Compartment", font=("Helvetica", 14, "bold")).pack(pady=5)
        
        # Button for grouping by compartment
        ctk.CTkButton(
            compartment_frame, 
            text="Group Items by Compartment", 
            command=self.sort_by_compartment,
            fg_color="#3a7ebf"
        ).pack(pady=5, fill="x", padx=10)
        
       
        expiry_frame = ctk.CTkFrame(scrollable_frame)
        expiry_frame.pack(pady=10, fill="x", padx=5)
        
        ctk.CTkLabel(expiry_frame, text="Sort by Expiry Date", font=("Helvetica", 14, "bold")).pack(pady=5)
        
        ctk.CTkButton(
            expiry_frame, 
            text="Soonest Expiry First", 
            command=self.sort_by_expiry_date,
            fg_color="#bf3a3a",  
            hover_color="#8f2b2b"
        ).pack(pady=5, fill="x", padx=10)

    def sort_by_name_alphabetical(self, ascending=True):
        """Sort items alphabetically by name (case-insensitive)."""
        try:
            # Create a temporary lowercase column for sorting to ignore case
            self.df['temp_name_lower'] = self.df['Name'].str.lower()
            
            # Sort by the lowercase column
            self.df = self.df.sort_values(by='temp_name_lower', ascending=ascending)
            
            # Remove the temporary column
            self.df = self.df.drop('temp_name_lower', axis=1)
            
            self.save_data()
            self.display_items()
            
            direction = "A to Z" if ascending else "Z to A"
            messagebox.showinfo("Success", f"Items sorted by name ({direction})!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while sorting: {e}")

    def sort_with_item_priority(self, priority_item):
        """Sort with a specific item at the top."""
        if not priority_item.strip():
            messagebox.showwarning("Warning", "Please enter an item name to prioritize.")
            return
        
        try:
            # Create a new column for sorting priority
            priority_item = priority_item.strip().lower()
            self.df['temp_priority'] = self.df['Name'].str.lower() == priority_item
            
            # Sort by priority (True first) then by name
            self.df = self.df.sort_values(by=['temp_priority', 'Name'], ascending=[False, True])
            
            # Remove temporary column
            self.df = self.df.drop('temp_priority', axis=1)
            
            self.save_data()
            self.display_items()
            
            # Check if the priority item was found
            if any(self.df['Name'].str.lower() == priority_item):
                messagebox.showinfo("Success", f"Items sorted with '{priority_item}' at the top!")
            else:
                messagebox.showinfo("Note", f"Item '{priority_item}' not found, but list is sorted alphabetically.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while sorting: {e}")

    def sort_by_quantity(self, ascending=True):
        """Sort items by quantity."""
        try:
            # Ensure quantity is numeric
            self.df['Quantity'] = pd.to_numeric(self.df['Quantity'], errors='coerce').fillna(0)
            
            # Sort by quantity
            self.df = self.df.sort_values(by='Quantity', ascending=ascending)
            self.save_data()
            self.display_items()
            
            direction = "lowest to highest" if ascending else "highest to lowest"
            messagebox.showinfo("Success", f"Items sorted by quantity ({direction})!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while sorting: {e}")

    def sort_by_category(self):
        """Sort items by grouping them by category."""
        try:
            # Sort by category first, then by name within each category
            self.df = self.df.sort_values(by=['Category', 'Name'])
            self.save_data()
            
            # Display items with category headers
            self.textbox.delete("1.0", "end")
            
            if self.df.empty:
                self.textbox.insert("end", "No items found.\n")
                return
            
            categories = self.df['Category'].unique()
            
            self.textbox.insert("end", "ITEMS GROUPED BY CATEGORY\n")
            self.textbox.insert("end", "=" * 50 + "\n\n")
            
            for category in categories:
                # Display category header
                self.textbox.insert("end", f"CATEGORY: {category}\n")
                self.textbox.insert("end", "-" * 50 + "\n")
                
                # Get items in this category
                category_items = self.df[self.df['Category'] == category]
                
                # Display items in this category
                for _, row in category_items.iterrows():
                    # Format expiry date if it's a datetime
                    if isinstance(row['Expiry_Date'], pd.Timestamp):
                        expiry_formatted = row['Expiry_Date'].strftime('%Y-%m-%d')
                    else:
                        expiry_formatted = str(row['Expiry_Date'])
                    
                    line = f"{row['Name']:<20}{row['Quantity']:<12}{row['Compartment']:<20}{expiry_formatted}\n"
                    self.textbox.insert("end", line)
                
                self.textbox.insert("end", "\n")
            
            messagebox.showinfo("Success", "Items sorted and grouped by category!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while sorting: {e}")

    def sort_by_compartment(self):
        """Sort items by grouping them by compartment."""
        try:
            # Sort by compartment first, then by name within each compartment
            self.df = self.df.sort_values(by=['Compartment', 'Name'])
            self.save_data()
            
            # Display items with compartment headers
            self.textbox.delete("1.0", "end")
            
            if self.df.empty:
                self.textbox.insert("end", "No items found.\n")
                return
            
            # Get unique compartments in sorted order
            compartments = self.df['Compartment'].unique()
            
            self.textbox.insert("end", "ITEMS GROUPED BY COMPARTMENT\n")
            self.textbox.insert("end", "=" * 50 + "\n\n")
            
            for compartment in compartments:
                # Display compartment header
                self.textbox.insert("end", f"COMPARTMENT: {compartment}\n")
                self.textbox.insert("end", "-" * 50 + "\n")
                
                # Get items in this compartment
                compartment_items = self.df[self.df['Compartment'] == compartment]
                
                # Display items in this compartment
                for _, row in compartment_items.iterrows():
                    # Format expiry date if it's a datetime
                    if isinstance(row['Expiry_Date'], pd.Timestamp):
                        expiry_formatted = row['Expiry_Date'].strftime('%Y-%m-%d')
                    else:
                        expiry_formatted = str(row['Expiry_Date'])
                    
                    line = f"{row['Name']:<20}{row['Quantity']:<12}{row['Category']:<15}{expiry_formatted}\n"
                    self.textbox.insert("end", line)
                
                self.textbox.insert("end", "\n")
            
            messagebox.showinfo("Success", "Items sorted and grouped by compartment!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while sorting: {e}")

    def sort_by_expiry_date(self):
        """Sort items by days remaining until expiry."""
        try:
            # Convert expiry dates to datetime
            self.df["Expiry_Date"] = pd.to_datetime(self.df["Expiry_Date"], errors='coerce')
            today = pd.Timestamp.now()
            self.df["Days_To_Expiry"] = (self.df["Expiry_Date"] - today).dt.days
            
            # Sort by days to expiry (ascending so soonest expiry comes first)
            self.df = self.df.sort_values(by="Days_To_Expiry", ascending=True)
            
            # Drop the temporary column
            self.df = self.df.drop("Days_To_Expiry", axis=1)
            
            self.save_data()
            self.display_items()
            messagebox.showinfo("Success", "Items sorted by expiry date (soonest expiry first)!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while sorting: {e}")
    def filter_items(self):
        """Filters items by category with dropdown selection."""
        # Get all unique categories from the dataframe
        categories = ["All Categories"]
        if not self.df.empty:
            unique_categories = self.df['Category'].unique().tolist()
            categories.extend(sorted(unique_categories))
        
        def apply_filter(selected_category):
            # Close the filter dialog
            filter_dialog.destroy()
            
            if selected_category == "All Categories":
             
                self.display_items()
            else:
              
                filtered_items = self.df[self.df['Category'] == selected_category]
                
                self.textbox.delete("1.0", "end")
                if filtered_items.empty:
                    self.textbox.insert("end", f"No items found in category '{selected_category}'.\n")
                else:
                 
                    self.textbox.insert("end", f"Items in category: {selected_category}\n\n")
                    
                    header = f"{'Name':<20}{'Quantity':<12}{'Category':<15}{'Compartment':<20}{'Expiry Date'}\n"
                    self.textbox.insert("end", header)
                    self.textbox.insert("end", "-" * 75 + "\n")

                    for _, row in filtered_items.iterrows():
     
                        expiry_date = row['Expiry_Date']
                        if isinstance(expiry_date, pd.Timestamp):
                            expiry_formatted = expiry_date.strftime('%Y-%m-%d')
                        else:
                            expiry_formatted = str(expiry_date)
                        
                        line = f"{str(row['Name']):<20}{str(row['Quantity']):<12}{str(row['Category']):<15}{str(row['Compartment']):<20}{expiry_formatted}\n"
                        self.textbox.insert("end", line)
        
        # Create a custom dialog for selecting category
        filter_dialog = ctk.CTkToplevel()
        filter_dialog.title("Filter by Category")
        filter_dialog.geometry("300x400")
        filter_dialog.grab_set()  
        
        # Create and configure the frame
        filter_frame = ctk.CTkFrame(filter_dialog)
        filter_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Add label
        ctk.CTkLabel(filter_frame, text="Select a category to filter:").pack(pady=(0, 10))
        
        scrollable_frame = ctk.CTkScrollableFrame(filter_frame, width=250, height=300)
        scrollable_frame.pack(fill="both", expand=True, pady=5)
        
        # Add buttons for each category
        for category in categories:
            ctk.CTkButton(
                scrollable_frame, 
                text=category,
                command=lambda cat=category: apply_filter(cat)
            ).pack(pady=2, fill="x")
    
    def update_shopping_list(self):
        """Updates the quantity of an existing item to a new specified amount."""
        if self.df.empty:
            self.textbox.delete("1.0", "end")
            self.textbox.insert("end", "❌ No items available to update.\n")
            return

        name = self.entry_name.get().strip()
        if not name:
            messagebox.showwarning("Input Error", "Please enter an item name.")
            return

        # Filter items matching the name (case-insensitive)
        name_matches = self.df[self.df['Name'].str.lower() == name.lower()]
        if name_matches.empty:
            messagebox.showwarning("Item Not Found", f"Item '{name}' not found in inventory.")
            return

        try:
            new_quantity = int(self.quantity_var.get())
            if new_quantity < 0:
                messagebox.showwarning("Input Error", "New quantity must be a non-negative number.")
                return
        except ValueError:
            messagebox.showwarning("Input Error", "Please enter a valid number for quantity.")
            return

      
        if len(name_matches) > 1:
            # Convert any datetime columns to string for display
            display_matches = name_matches.copy()
            if 'Expiry_Date' in display_matches.columns:
                display_matches['Expiry_Date'] = display_matches['Expiry_Date'].astype(str)
          
            options_text = ""
            for idx, row in display_matches.iterrows():
                category = row['Category'] if 'Category' in row else 'N/A'
                compartment = row['Compartment'] if 'Compartment' in row else 'N/A'
                expiry = row['Expiry_Date'] if 'Expiry_Date' in row else 'N/A'
                
                options_text += f"Index {idx}: {row['Name']} - Qty: {row['Quantity']}, Category: {category}\n"
                options_text += f"       Location: {compartment}, Expires: {expiry}\n\n"
        
            index_to_update = simpledialog.askstring(
                "Multiple Items Found",
                f"Multiple items named '{name}' found.\nPlease enter the index number of the item you want to update:\n\n{options_text}"
            )
            
            try:
                idx = int(index_to_update)
                if idx not in name_matches.index:
                    messagebox.showwarning("Invalid Selection", "Please enter a valid index number.")
                    return
                # Update only the selected item
                old_quantity = self.df.at[idx, 'Quantity']
                self.df.at[idx, 'Quantity'] = new_quantity
            except (ValueError, TypeError):
                messagebox.showwarning("Invalid Input", "Please enter a valid index number.")
                return
        else:
            # Only one match, update it directly
            idx = name_matches.index[0]
            old_quantity = self.df.at[idx, 'Quantity']
            self.df.at[idx, 'Quantity'] = new_quantity
        
        # Remove items with quantity 0
        if new_quantity == 0:
            self.df = self.df[self.df['Quantity'] > 0]
        
        self.save_data()
        
        # Display result message
        self.textbox.delete("1.0", "end")
        if new_quantity > 0:
            self.textbox.insert("end", f"✅ Successfully updated '{name}' quantity from {old_quantity} to {new_quantity}.\n\n")
        else:
            self.textbox.insert("end", f"✅ Item '{name}' was removed from inventory (quantity set to 0).\n\n")
        
        # Display the updated inventory
        self.textbox.insert("end", "Updated inventory:\n")
        if self.df.empty:
            self.textbox.insert("end", "No items found.\n")
        else:
            # Header
            header = f"{'Name':<20}{'Quantity':<12}{'Category':<15}{'Compartment':<20}{'Expiry Date'}\n"
            self.textbox.insert("end", header)
            self.textbox.insert("end", "-" * 75 + "\n")

            # Rows
            for _, row in self.df.iterrows():
                # Format expiry date nicely if it's a datetime, otherwise use as is
                expiry_date = row['Expiry_Date']
                if isinstance(expiry_date, pd.Timestamp):
                    expiry_formatted = expiry_date.strftime('%Y-%m-%d')
                else:
                    expiry_formatted = str(expiry_date)
                
                line = f"{str(row['Name']):<20}{str(row['Quantity']):<12}{str(row['Category']):<15}{str(row['Compartment']):<20}{expiry_formatted}\n"
                self.textbox.insert("end", line)
        
        # Clear UI elements after update is complete
        self.clear_update_ui()
    def clear_update_ui(self):
        """Clears the update shopping list UI elements if they exist."""
        if self.update_frame:
            self.update_frame.destroy()  
            self.update_frame = None
            self.entry_name = None
            self.entry_quantity = None
            self.confirm_button = None
            self.minus_btn = None
            self.plus_btn = None
            self.quantity_var = None
    
    def increment_quantity(self):
        """Increment the quantity value by 1."""
        try:
            current_val = int(self.quantity_var.get())
            self.quantity_var.set(str(current_val + 1))
        except ValueError:
            self.quantity_var.set("1")

    def decrement_quantity(self):
        """Decrement the quantity value by 1, but not below 0."""
        try:
            current_val = int(self.quantity_var.get())
            if current_val > 0:
                self.quantity_var.set(str(current_val - 1))
        except ValueError:
            self.quantity_var.set("0")
    
    
    def show_update_shopping_list_ui(self):
        """Shows UI elements for updating shopping list."""
        # Display current inventory first
        self.display_items()
        
        # Create a frame for the update controls (bottom row)
        self.update_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.update_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        self.update_frame.grid_columnconfigure(0, weight=1)  # Name entry
        self.update_frame.grid_columnconfigure(1, weight=0)  # Minus button
        self.update_frame.grid_columnconfigure(2, weight=0)  # Quantity entry
        self.update_frame.grid_columnconfigure(3, weight=0)  # Plus button
        self.update_frame.grid_columnconfigure(4, weight=1)  # Confirm button
        
        # Create entry fields for item name
        self.entry_name = ctk.CTkEntry(self.update_frame, placeholder_text="Item Name")
        self.entry_name.grid(row=0, column=0, padx=5, sticky="ew")
        # Add validation to automatically update quantity when a valid item name is entered
        self.entry_name.bind("<KeyRelease>", self.auto_update_quantity)
        
        # Create quantity controls with +/- buttons
        self.quantity_var = ctk.StringVar(value="1")
        
        # Minus button
        self.minus_btn = ctk.CTkButton(self.update_frame, text="-", width=30, command=self.decrement_quantity)
        self.minus_btn.grid(row=0, column=1, padx=(5, 2))
        
        # Quantity entry
        self.entry_quantity = ctk.CTkEntry(self.update_frame, textvariable=self.quantity_var, width=60, justify='center')
        self.entry_quantity.grid(row=0, column=2, padx=0)
        
        # Plus button
        self.plus_btn = ctk.CTkButton(self.update_frame, text="+", width=30, command=self.increment_quantity)
        self.plus_btn.grid(row=0, column=3, padx=(2, 5))
        
        # Confirm button
        self.confirm_button = ctk.CTkButton(self.update_frame, text="Confirm", command=self.update_shopping_list)
        self.confirm_button.grid(row=0, column=4, padx=5, sticky="ew")

    def auto_update_quantity(self, event=None):
        """Automatically update the quantity field when a valid item name is entered."""
        name = self.entry_name.get().strip()
        if not name:
            return
            
        # Filter items matching the name (case-insensitive)
        name_matches = self.df[self.df['Name'].str.lower() == name.lower()]
        if not name_matches.empty:
            # Get the quantity of the first matching item
            current_quantity = name_matches.iloc[0]['Quantity']
            self.quantity_var.set(str(int(current_quantity)))
            
            # If multiple matches, provide a hint
            if len(name_matches) > 1:
                self.textbox.insert("end", f"\nMultiple items named '{name}' found. The quantity shown is for the first match.\n")

# if __name__ == "__main__":
#     root = ctk.CTk()
#     app = SmartGroceryTrackerUI(root)
#     root.mainloop()