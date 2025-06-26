import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime, date
import re

class TruckDeliverySystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Truck Deliveries Management System")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize database
        self.init_database()
        
        # Create main interface
        self.create_main_interface()
        
        # Load initial data
        self.refresh_all_data()
    
    def init_database(self):
        """Initialize SQLite database with required tables"""
        self.conn = sqlite3.connect('truck_deliveries.db')
        self.cursor = self.conn.cursor()
        
        # Create trucks table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS trucks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                truck_number TEXT UNIQUE NOT NULL,
                model TEXT NOT NULL,
                capacity REAL NOT NULL,
                status TEXT DEFAULT 'Available',
                registration_date DATE,
                last_maintenance DATE
            )
        ''')
        
        
    
    def create_main_interface(self):
        """Create the main user interface"""
        # Main title
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        title_frame.pack(fill='x', pady=(0, 10))
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text="🚛 Truck Deliveries Management System", 
                              font=('Arial', 18, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack(expand=True)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Create tabs
        self.create_truck_management_tab()
        self.create_driver_management_tab()
        self.create_delivery_scheduling_tab()
        self.create_delivery_tracking_tab()
        self.create_reports_tab()
    
    def create_truck_management_tab(self):
        """Create truck management interface"""
        truck_frame = ttk.Frame(self.notebook)
        self.notebook.add(truck_frame, text="🚚 Truck Management")
        
        # Control panel
        control_frame = ttk.LabelFrame(truck_frame, text="Truck Controls", padding=10)
        control_frame.pack(fill='x', padx=10, pady=5)
        
        # Input fields
        fields_frame = ttk.Frame(control_frame)
        fields_frame.pack(fill='x')
        
        # Truck number
        ttk.Label(fields_frame, text="Truck Number:").grid(row=0, column=0, sticky='w', padx=5)
        self.truck_number_entry = ttk.Entry(fields_frame, width=15)
        self.truck_number_entry.grid(row=0, column=1, padx=5)
        
        # Model
        ttk.Label(fields_frame, text="Model:").grid(row=0, column=2, sticky='w', padx=5)
        self.truck_model_entry = ttk.Entry(fields_frame, width=15)
        self.truck_model_entry.grid(row=0, column=3, padx=5)
        
        # Capacity
        ttk.Label(fields_frame, text="Capacity (tons):").grid(row=0, column=4, sticky='w', padx=5)
        self.truck_capacity_entry = ttk.Entry(fields_frame, width=15)
        self.truck_capacity_entry.grid(row=0, column=5, padx=5)
        
        # Status
        ttk.Label(fields_frame, text="Status:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.truck_status_combo = ttk.Combobox(fields_frame, values=['Available', 'In Transit', 'Maintenance', 'Out of Service'], width=12)
        self.truck_status_combo.grid(row=1, column=1, padx=5, pady=5)
        self.truck_status_combo.set('Available')
        
        # Buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill='x', pady=10)
        
        ttk.Button(button_frame, text="Add Truck", command=self.add_truck).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Update Truck", command=self.update_truck).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Delete Truck", command=self.delete_truck).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Clear Fields", command=self.clear_truck_fields).pack(side='left', padx=5)
        
        # Truck list
        list_frame = ttk.LabelFrame(truck_frame, text="Truck List", padding=10)
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Treeview for trucks
        columns = ('ID', 'Truck Number', 'Model', 'Capacity', 'Status', 'Registration Date')
        self.truck_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.truck_tree.heading(col, text=col)
            self.truck_tree.column(col, width=120)
        
        # Scrollbar
        truck_scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.truck_tree.yview)
        self.truck_tree.configure(yscrollcommand=truck_scrollbar.set)
        
        self.truck_tree.pack(side='left', fill='both', expand=True)
        truck_scrollbar.pack(side='right', fill='y')
        
        # Bind selection event
        self.truck_tree.bind('<<TreeviewSelect>>', self.on_truck_select)
    
    
    # Truck Management Methods
    def add_truck(self):
        """Add a new truck to the database"""
        try:
            truck_number = self.truck_number_entry.get().strip()
            model = self.truck_model_entry.get().strip()
            capacity = float(self.truck_capacity_entry.get().strip())
            status = self.truck_status_combo.get()
            
            if not truck_number or not model:
                messagebox.showerror("Error", "Truck number and model are required!")
                return
            
            self.cursor.execute('''
                INSERT INTO trucks (truck_number, model, capacity, status, registration_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (truck_number, model, capacity, status, date.today()))
            
            self.conn.commit()
            messagebox.showinfo("Success", "Truck added successfully!")
            self.clear_truck_fields()
            self.refresh_truck_data()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid capacity!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Truck number already exists!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add truck: {str(e)}")
    
    def update_truck(self):
        """Update selected truck"""
        selected = self.truck_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a truck to update!")
            return
        
        try:
            truck_id = self.truck_tree.item(selected[0])['values'][0]
            truck_number = self.truck_number_entry.get().strip()
            model = self.truck_model_entry.get().strip()
            capacity = float(self.truck_capacity_entry.get().strip())
            status = self.truck_status_combo.get()
            
            if not truck_number or not model:
                messagebox.showerror("Error", "Truck number and model are required!")
                return
            
            self.cursor.execute('''
                UPDATE trucks SET truck_number=?, model=?, capacity=?, status=?
                WHERE id=?
            ''', (truck_number, model, capacity, status, truck_id))
            
            self.conn.commit()
            messagebox.showinfo("Success", "Truck updated successfully!")
            self.clear_truck_fields()
            self.refresh_truck_data()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid capacity!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update truck: {str(e)}")
    
    def delete_truck(self):
        """Delete selected truck"""
        selected = self.truck_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a truck to delete!")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this truck?"):
            try:
                truck_id = self.truck_tree.item(selected[0])['values'][0]
                self.cursor.execute('DELETE FROM trucks WHERE id=?', (truck_id,))
                self.conn.commit()
                messagebox.showinfo("Success", "Truck deleted successfully!")
                self.refresh_truck_data()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete truck: {str(e)}")
    
    def clear_truck_fields(self):
        """Clear truck input fields"""
        self.truck_number_entry.delete(0, tk.END)
        self.truck_model_entry.delete(0, tk.END)
        self.truck_capacity_entry.delete(0, tk.END)
        self.truck_status_combo.set('Available')
    
    def on_truck_select(self, event):
        """Handle truck selection"""
        selected = self.truck_tree.selection()
        if selected:
            values = self.truck_tree.item(selected[0])['values']
            self.truck_number_entry.delete(0, tk.END)
            self.truck_number_entry.insert(0, values[1])
            self.truck_model_entry.delete(0, tk.END)
            self.truck_model_entry.insert(0, values[2])
            self.truck_capacity_entry.delete(0, tk.END)
            self.truck_capacity_entry.insert(0, values[3])
            self.truck_status_combo.set(values[4])
    
        # Driver Management Methods
    def add_driver(self):
        """Add a new driver to the database"""
        try:
            name = self.driver_name_entry.get().strip()
            license_number = self.driver_license_entry.get().strip()
            phone = self.driver_phone_entry.get().strip()
            email = self.driver_email_entry.get().strip()
            status = self.driver_status_combo.get()
            
            if not name or not license_number:
                messagebox.showerror("Error", "Name and license number are required!")
                return
            
            # Validate email if provided
            if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                messagebox.showerror("Error", "Please enter a valid email address!")
                return
            
            self.cursor.execute('''
                INSERT INTO drivers (name, license_number, phone, email, status, hire_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, license_number, phone, email, status, date.today()))
            
            self.conn.commit()
            messagebox.showinfo("Success", "Driver added successfully!")
            self.clear_driver_fields()
            self.refresh_driver_data()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "License number already exists!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add driver: {str(e)}")
    
    def update_driver(self):
        """Update selected driver"""
        selected = self.driver_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a driver to update!")
            return
        
        try:
            driver_id = self.driver_tree.item(selected[0])['values'][0]
            name = self.driver_name_entry.get().strip()
            license_number = self.driver_license_entry.get().strip()
            phone = self.driver_phone_entry.get().strip()
            email = self.driver_email_entry.get().strip()
            status = self.driver_status_combo.get()
            
            if not name or not license_number:
                messagebox.showerror("Error", "Name and license number are required!")
                return
            
            # Validate email if provided
            if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                messagebox.showerror("Error", "Please enter a valid email address!")
                return
            
            self.cursor.execute('''
                UPDATE drivers SET name=?, license_number=?, phone=?, email=?, status=?
                WHERE id=?
            ''', (name, license_number, phone, email, status, driver_id))
            
            self.conn.commit()
            messagebox.showinfo("Success", "Driver updated successfully!")
            self.clear_driver_fields()
            self.refresh_driver_data()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update driver: {str(e)}")
    
    def delete_driver(self):
        """Delete selected driver"""
        selected = self.driver_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a driver to delete!")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this driver?"):
            try:
                driver_id = self.driver_tree.item(selected[0])['values'][0]
                self.cursor.execute('DELETE FROM drivers WHERE id=?', (driver_id,))
                self.conn.commit()
                messagebox.showinfo("Success", "Driver deleted successfully!")
                self.refresh_driver_data()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete driver: {str(e)}")
    
    def clear_driver_fields(self):
        """Clear driver input fields"""
        self.driver_name_entry.delete(0, tk.END)
        self.driver_license_entry.delete(0, tk.END)
        self.driver_phone_entry.delete(0, tk.END)
        self.driver_email_entry.delete(0, tk.END)
        self.driver_status_combo.set('Available')
    
    def on_driver_select(self, event):
        """Handle driver selection"""
        selected = self.driver_tree.selection()
        if selected:
            values = self.driver_tree.item(selected[0])['values']
            self.driver_name_entry.delete(0, tk.END)
            self.driver_name_entry.insert(0, values[1])
            self.driver_license_entry.delete(0, tk.END)
            self.driver_license_entry.insert(0, values[2])
            self.driver_phone_entry.delete(0, tk.END)
            self.driver_phone_entry.insert(0, values[3] if values[3] else "")
            self.driver_email_entry.delete(0, tk.END)
            self.driver_email_entry.insert(0, values[4] if values[4] else "")
            self.driver_status_combo.set(values[5])
    

def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = TruckDeliverySystem(root)
    root.mainloop()

if __name__ == "__main__":
    main()