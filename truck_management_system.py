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
    
# Delivery Scheduling Methods
    def schedule_delivery(self):
        """Schedule a new delivery"""
        try:
            delivery_id = self.delivery_id_entry.get().strip()
            truck = self.delivery_truck_combo.get()
            driver = self.delivery_driver_combo.get()
            pickup_location = self.pickup_location_entry.get().strip()
            delivery_location = self.delivery_location_entry.get().strip()
            cargo_description = self.cargo_description_entry.get().strip()
            weight = float(self.cargo_weight_entry.get().strip()) if self.cargo_weight_entry.get().strip() else 0
            scheduled_date = self.scheduled_date_entry.get().strip()
            scheduled_time = self.scheduled_time_entry.get().strip()
            status = self.delivery_status_combo.get()
            
            if not all([delivery_id, truck, driver, pickup_location, delivery_location]):
                messagebox.showerror("Error", "Please fill in all required fields!")
                return
            
            # Validate date format
            try:
                datetime.strptime(scheduled_date, '%Y-%m-%d')
            except ValueError:
                messagebox.showerror("Error", "Please enter date in YYYY-MM-DD format!")
                return
            
            # Validate time format
            try:
                datetime.strptime(scheduled_time, '%H:%M')
            except ValueError:
                messagebox.showerror("Error", "Please enter time in HH:MM format!")
                return
            
            # Get truck and driver IDs
            truck_id = truck.split(' - ')[0]
            driver_id = driver.split(' - ')[0]
            
            self.cursor.execute('''
                INSERT INTO deliveries (delivery_id, truck_id, driver_id, pickup_location, 
                delivery_location, cargo_description, weight, scheduled_date, scheduled_time, 
                status, created_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (delivery_id, truck_id, driver_id, pickup_location, delivery_location, 
                  cargo_description, weight, scheduled_date, scheduled_time, status, date.today()))
            
            self.conn.commit()
            messagebox.showinfo("Success", "Delivery scheduled successfully!")
            self.clear_delivery_fields()
            self.refresh_delivery_data()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid weight!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Delivery ID already exists!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to schedule delivery: {str(e)}")
    
    def update_delivery(self):
        """Update selected delivery"""
        selected = self.delivery_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a delivery to update!")
            return
        
        try:
            delivery_db_id = self.delivery_tree.item(selected[0])['values'][0]
            delivery_id = self.delivery_id_entry.get().strip()
            truck = self.delivery_truck_combo.get()
            driver = self.delivery_driver_combo.get()
            pickup_location = self.pickup_location_entry.get().strip()
            delivery_location = self.delivery_location_entry.get().strip()
            cargo_description = self.cargo_description_entry.get().strip()
            weight = float(self.cargo_weight_entry.get().strip()) if self.cargo_weight_entry.get().strip() else 0
            scheduled_date = self.scheduled_date_entry.get().strip()
            scheduled_time = self.scheduled_time_entry.get().strip()
            status = self.delivery_status_combo.get()
            
            if not all([delivery_id, truck, driver, pickup_location, delivery_location]):
                messagebox.showerror("Error", "Please fill in all required fields!")
                return
            
            # Get truck and driver IDs
            truck_id = truck.split(' - ')[0]
            driver_id = driver.split(' - ')[0]
            
            self.cursor.execute('''
                UPDATE deliveries SET delivery_id=?, truck_id=?, driver_id=?, pickup_location=?, 
                delivery_location=?, cargo_description=?, weight=?, scheduled_date=?, 
                scheduled_time=?, status=? WHERE id=?
            ''', (delivery_id, truck_id, driver_id, pickup_location, delivery_location, 
                  cargo_description, weight, scheduled_date, scheduled_time, status, delivery_db_id))
            
            self.conn.commit()
            messagebox.showinfo("Success", "Delivery updated successfully!")
            self.clear_delivery_fields()
            self.refresh_delivery_data()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid weight!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update delivery: {str(e)}")
    
    def cancel_delivery(self):
        """Cancel selected delivery"""
        selected = self.delivery_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a delivery to cancel!")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to cancel this delivery?"):
            try:
                delivery_id = self.delivery_tree.item(selected[0])['values'][0]
                self.cursor.execute('UPDATE deliveries SET status="Cancelled" WHERE id=?', (delivery_id,))
                self.conn.commit()
                messagebox.showinfo("Success", "Delivery cancelled successfully!")
                self.refresh_delivery_data()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to cancel delivery: {str(e)}")
    
    def clear_delivery_fields(self):
        """Clear delivery input fields"""
        self.delivery_id_entry.delete(0, tk.END)
        self.pickup_location_entry.delete(0, tk.END)
        self.delivery_location_entry.delete(0, tk.END)
        self.cargo_description_entry.delete(0, tk.END)
        self.cargo_weight_entry.delete(0, tk.END)
        self.scheduled_date_entry.delete(0, tk.END)
        self.scheduled_date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.scheduled_time_entry.delete(0, tk.END)
        self.scheduled_time_entry.insert(0, '09:00')
        self.delivery_status_combo.set('Scheduled')
    
    def generate_delivery_id(self):
        """Generate a unique delivery ID"""
        delivery_id = f"DEL{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.delivery_id_entry.delete(0, tk.END)
        self.delivery_id_entry.insert(0, delivery_id)
    
    def on_delivery_select(self, event):
        """Handle delivery selection"""
        selected = self.delivery_tree.selection()
        if selected:
            values = self.delivery_tree.item(selected[0])['values']
            
            # Get the actual delivery data from database to get truck_id and driver_id
            try:
                delivery_db_id = values[0]
                self.cursor.execute('''
                    SELECT d.*, t.truck_number, dr.name as driver_name
                    FROM deliveries d
                    LEFT JOIN trucks t ON d.truck_id = t.id
                    LEFT JOIN drivers dr ON d.driver_id = dr.id
                    WHERE d.id = ?
                ''', (delivery_db_id,))
                
                delivery_data = self.cursor.fetchone()
                
                if delivery_data:
                    # Fill delivery fields
                    self.delivery_id_entry.delete(0, tk.END)
                    self.delivery_id_entry.insert(0, delivery_data[1])  # delivery_id
                    
                    # Set truck combo - find the option that starts with the truck_id
                    truck_id = delivery_data[2]  # truck_id
                    for i, truck_option in enumerate(self.delivery_truck_combo['values']):
                        if truck_option.startswith(f"{truck_id} - "):
                            self.delivery_truck_combo.current(i)
                            break
                    
                    # Set driver combo - find the option that starts with the driver_id
                    driver_id = delivery_data[3]  # driver_id
                    for i, driver_option in enumerate(self.delivery_driver_combo['values']):
                        if driver_option.startswith(f"{driver_id} - "):
                            self.delivery_driver_combo.current(i)
                            break
                    
                    # Fill other fields
                    self.pickup_location_entry.delete(0, tk.END)
                    self.pickup_location_entry.insert(0, delivery_data[4])  # pickup_location
                    self.delivery_location_entry.delete(0, tk.END)
                    self.delivery_location_entry.insert(0, delivery_data[5])  # delivery_location
                    self.cargo_description_entry.delete(0, tk.END)
                    self.cargo_description_entry.insert(0, delivery_data[6] if delivery_data[6] else "")  # cargo_description
                    self.cargo_weight_entry.delete(0, tk.END)
                    self.cargo_weight_entry.insert(0, str(delivery_data[7]) if delivery_data[7] else "")  # weight
                    self.scheduled_date_entry.delete(0, tk.END)
                    self.scheduled_date_entry.insert(0, delivery_data[8])  # scheduled_date
                    self.scheduled_time_entry.delete(0, tk.END)
                    self.scheduled_time_entry.insert(0, delivery_data[9])  # scheduled_time
                    self.delivery_status_combo.set(delivery_data[10])  # status
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load delivery details: {str(e)}")
    
    # Delivery Tracking Methods
    def search_delivery(self):
        """Search for a specific delivery"""
        search_term = self.search_delivery_entry.get().strip()
        if not search_term:
            messagebox.showwarning("Warning", "Please enter a delivery ID to search!")
            return
        
        try:
            self.cursor.execute('''
                SELECT d.*, t.truck_number, dr.name as driver_name
                FROM deliveries d
                LEFT JOIN trucks t ON d.truck_id = t.id
                LEFT JOIN drivers dr ON d.driver_id = dr.id
                WHERE d.delivery_id LIKE ?
            ''', (f'%{search_term}%',))
            
            result = self.cursor.fetchone()
            if result:
                self.display_delivery_details(result)
            else:
                messagebox.showinfo("Not Found", "No delivery found with that ID!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {str(e)}")
    
    def show_all_deliveries(self):
        """Show all deliveries in tracking"""
        self.refresh_delivery_tracking()
    
    def filter_deliveries(self):
        """Filter deliveries by status"""
        status_filter = self.status_filter_combo.get()
        
        try:
            if status_filter == 'All':
                query = '''
                    SELECT d.*, t.truck_number, dr.name as driver_name
                    FROM deliveries d
                    LEFT JOIN trucks t ON d.truck_id = t.id
                    LEFT JOIN drivers dr ON d.driver_id = dr.id
                    ORDER BY d.scheduled_date DESC, d.scheduled_time DESC
                '''
                self.cursor.execute(query)
            else:
                query = '''
                    SELECT d.*, t.truck_number, dr.name as driver_name
                    FROM deliveries d
                    LEFT JOIN trucks t ON d.truck_id = t.id
                    LEFT JOIN drivers dr ON d.driver_id = dr.id
                    WHERE d.status = ?
                    ORDER BY d.scheduled_date DESC, d.scheduled_time DESC
                '''
                self.cursor.execute(query, (status_filter,))
            
            results = self.cursor.fetchall()
            
            if results:
                details_text = f"Found {len(results)} deliveries with status '{status_filter}':\n\n"
                for result in results:
                    details_text += self.format_delivery_details(result) + "\n" + "="*50 + "\n\n"
                self.delivery_details_text.delete(1.0, tk.END)
                self.delivery_details_text.insert(1.0, details_text)
            else:
                self.delivery_details_text.delete(1.0, tk.END)
                self.delivery_details_text.insert(1.0, f"No deliveries found with status '{status_filter}'")
                
        except Exception as e:
            messagebox.showerror("Error", f"Filter failed: {str(e)}")
    
    def display_delivery_details(self, delivery_data):
        """Display detailed information about a delivery"""
        details = self.format_delivery_details(delivery_data)
        self.delivery_details_text.delete(1.0, tk.END)
        self.delivery_details_text.insert(1.0, details)
    
    def format_delivery_details(self, delivery_data):
        """Format delivery data for display"""
        return f"""
Delivery ID: {delivery_data[1]}
Truck: {delivery_data[12]} (ID: {delivery_data[2]})
Driver: {delivery_data[13]} (ID: {delivery_data[3]})
Pickup Location: {delivery_data[4]}
Delivery Location: {delivery_data[5]}
Cargo Description: {delivery_data[6] or 'N/A'}
Weight: {delivery_data[7]} tons
Scheduled Date: {delivery_data[8]}
Scheduled Time: {delivery_data[9]}
Status: {delivery_data[10]}
Created Date: {delivery_data[11]}
Completed Date: {delivery_data[14] or 'Not completed'}
        """
    
    def update_delivery_status(self):
        """Update delivery status from tracking tab"""
        search_term = self.search_delivery_entry.get().strip()
        new_status = self.update_status_combo.get()
        
        if not search_term or not new_status:
            messagebox.showwarning("Warning", "Please enter delivery ID and select status!")
            return
        
        try:
            completed_date = date.today() if new_status == 'Completed' else None
            
            self.cursor.execute('''
                UPDATE deliveries SET status=?, completed_date=?
                WHERE delivery_id=?
            ''', (new_status, completed_date, search_term))
            
            if self.cursor.rowcount > 0:
                self.conn.commit()
                messagebox.showinfo("Success", "Delivery status updated successfully!")
                self.search_delivery()  # Refresh the display
            else:
                messagebox.showwarning("Warning", "No delivery found with that ID!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update status: {str(e)}")
    
    def mark_completed(self):
        """Mark delivery as completed"""
        self.update_status_combo.set('Completed')
        self.update_delivery_status()
    
    # Reports Methods
    def truck_utilization_report(self):
        """Generate truck utilization report"""
        try:
            self.cursor.execute('''
                SELECT 
                    t.truck_number,
                    t.model,
                    t.status,
                    COUNT(d.id) as total_deliveries,
                    COUNT(CASE WHEN d.status = 'Completed' THEN 1 END) as completed_deliveries,
                    COUNT(CASE WHEN d.status = 'In Progress' THEN 1 END) as active_deliveries
                FROM trucks t
                LEFT JOIN deliveries d ON t.id = d.truck_id
                GROUP BY t.id, t.truck_number, t.model, t.status
                ORDER BY total_deliveries DESC
            ''')
            
            results = self.cursor.fetchall()
            
            report = "TRUCK UTILIZATION REPORT\n"
            report += "=" * 60 + "\n\n"
            report += f"{'Truck Number':<15} {'Model':<15} {'Status':<12} {'Total':<8} {'Completed':<10} {'Active':<8}\n"
            report += "-" * 68 + "\n"
            
            for row in results:
                report += f"{row[0]:<15} {row[1]:<15} {row[2]:<12} {row[3]:<8} {row[4]:<10} {row[5]:<8}\n"
            
            self.reports_text.delete(1.0, tk.END)
            self.reports_text.insert(1.0, report)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
    
    def driver_performance_report(self):
        """Generate driver performance report"""
        try:
            self.cursor.execute('''
                SELECT 
                    dr.name,
                    dr.license_number,
                    dr.status,
                    COUNT(d.id) as total_deliveries,
                    COUNT(CASE WHEN d.status = 'Completed' THEN 1 END) as completed_deliveries,
                    COUNT(CASE WHEN d.status = 'In Progress' THEN 1 END) as active_deliveries
                FROM drivers dr
                LEFT JOIN deliveries d ON dr.id = d.driver_id
                GROUP BY dr.id, dr.name, dr.license_number, dr.status
                ORDER BY completed_deliveries DESC
            ''')
            
            results = self.cursor.fetchall()
            
            report = "DRIVER PERFORMANCE REPORT\n"
            report += "=" * 70 + "\n\n"
            report += f"{'Driver Name':<20} {'License':<15} {'Status':<12} {'Total':<8} {'Completed':<10} {'Active':<8}\n"
            report += "-" * 73 + "\n"
            
            for row in results:
                report += f"{row[0]:<20} {row[1]:<15} {row[2]:<12} {row[3]:<8} {row[4]:<10} {row[5]:<8}\n"
            
            self.reports_text.delete(1.0, tk.END)
            self.reports_text.insert(1.0, report)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
    
    def delivery_summary_report(self):
        """Generate delivery summary report"""
        try:
            self.cursor.execute('''
                SELECT 
                    status,
                    COUNT(*) as count,
                    AVG(weight) as avg_weight
                FROM deliveries
                GROUP BY status
                ORDER BY count DESC
            ''')
            
            status_results = self.cursor.fetchall()
            
            self.cursor.execute('''
                SELECT 
                    COUNT(*) as total_deliveries,
                    SUM(weight) as total_weight,
                    AVG(weight) as avg_weight
                FROM deliveries
            ''')
            
            summary = self.cursor.fetchone()
            
            report = "DELIVERY SUMMARY REPORT\n"
            report += "=" * 50 + "\n\n"
            
            report += "OVERALL STATISTICS:\n"
            report += f"Total Deliveries: {summary[0]}\n"
            report += f"Total Weight: {summary[1]:.2f} tons\n"
            report += f"Average Weight: {summary[2]:.2f} tons\n\n"
            
            report += "STATUS BREAKDOWN:\n"
            report += f"{'Status':<15} {'Count':<8} {'Avg Weight':<12}\n"
            report += "-" * 35 + "\n"
            
            for row in status_results:
                avg_weight = row[2] if row[2] else 0
                report += f"{row[0]:<15} {row[1]:<8} {avg_weight:<12.2f}\n"
            
            self.reports_text.delete(1.0, tk.END)
            self.reports_text.insert(1.0, report)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
    
    def monthly_report(self):
        """Generate monthly report"""
        try:
            current_month = datetime.now().strftime('%Y-%m')
            
            self.cursor.execute('''
                SELECT 
                    strftime('%Y-%m', scheduled_date) as month,
                    COUNT(*) as total_deliveries,
                    COUNT(CASE WHEN status = 'Completed' THEN 1 END) as completed,
                    COUNT(CASE WHEN status = 'Cancelled' THEN 1 END) as cancelled,
                    SUM(weight) as total_weight
                FROM deliveries
                WHERE strftime('%Y-%m', scheduled_date) = ?
                GROUP BY month
            ''', (current_month,))
            
            monthly_data = self.cursor.fetchone()
            
            if monthly_data:
                report = f"MONTHLY REPORT - {current_month}\n"
                report += "=" * 40 + "\n\n"
                report += f"Total Deliveries: {monthly_data[1]}\n"
                report += f"Completed: {monthly_data[2]}\n"
                report += f"Cancelled: {monthly_data[3]}\n"
                report += f"In Progress: {monthly_data[1] - monthly_data[2] - monthly_data[3]}\n"
                report += f"Total Weight: {monthly_data[4]:.2f} tons\n"
                report += f"Completion Rate: {(monthly_data[2]/monthly_data[1]*100):.1f}%\n"
            else:
                report = f"MONTHLY REPORT - {current_month}\n"
                report += "=" * 40 + "\n\n"
                report += "No deliveries found for this month.\n"
            
            self.reports_text.delete(1.0, tk.END)
            self.reports_text.insert(1.0, report)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
    
    # Data Refresh Methods
    def refresh_all_data(self):
        """Refresh all data displays"""
        self.refresh_truck_data()
        self.refresh_driver_data()
        self.refresh_delivery_data()
        self.refresh_delivery_tracking()
        self.update_combos()
    
    def refresh_truck_data(self):
        """Refresh truck treeview"""
        for item in self.truck_tree.get_children():
            self.truck_tree.delete(item)
        
        try:
            self.cursor.execute('SELECT * FROM trucks ORDER BY truck_number')
            trucks = self.cursor.fetchall()
            
            for truck in trucks:
                self.truck_tree.insert('', 'end', values=truck)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh truck data: {str(e)}")
    
    def refresh_driver_data(self):
        """Refresh driver treeview"""
        for item in self.driver_tree.get_children():
            self.driver_tree.delete(item)
        
        try:
            self.cursor.execute('SELECT * FROM drivers ORDER BY name')
            drivers = self.cursor.fetchall()
            
            for driver in drivers:
                self.driver_tree.insert('', 'end', values=driver)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh driver data: {str(e)}")
    
    def refresh_delivery_data(self):
        """Refresh delivery treeview"""
        for item in self.delivery_tree.get_children():
            self.delivery_tree.delete(item)
        
        try:
            self.cursor.execute('''
                SELECT d.id, d.delivery_id, t.truck_number, dr.name, 
                       d.pickup_location, d.delivery_location, 
                       d.scheduled_date, d.scheduled_time, d.status
                FROM deliveries d
                LEFT JOIN trucks t ON d.truck_id = t.id
                LEFT JOIN drivers dr ON d.driver_id = dr.id
                ORDER BY d.scheduled_date DESC, d.scheduled_time DESC
            ''')
            deliveries = self.cursor.fetchall()
            
            for delivery in deliveries:
                self.delivery_tree.insert('', 'end', values=delivery)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh delivery data: {str(e)}")
    
    def refresh_delivery_tracking(self):
        """Refresh delivery tracking display"""
        try:
            self.cursor.execute('''
                SELECT d.*, t.truck_number, dr.name as driver_name
                FROM deliveries d
                LEFT JOIN trucks t ON d.truck_id = t.id
                LEFT JOIN drivers dr ON d.driver_id = dr.id
                ORDER BY d.scheduled_date DESC, d.scheduled_time DESC
                LIMIT 10
            ''')
            
            recent_deliveries = self.cursor.fetchall()
            
            if recent_deliveries:
                details_text = "RECENT DELIVERIES:\n\n"
                for delivery in recent_deliveries:
                    details_text += self.format_delivery_details(delivery) + "\n" + "="*50 + "\n\n"
                self.delivery_details_text.delete(1.0, tk.END)
                self.delivery_details_text.insert(1.0, details_text)
            else:
                self.delivery_details_text.delete(1.0, tk.END)
                self.delivery_details_text.insert(1.0, "No deliveries found.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh tracking data: {str(e)}")
    
    def update_combos(self):
        """Update combo box values"""
        try:
            # Update truck combo - include all trucks so existing deliveries can show their assigned truck
            self.cursor.execute('SELECT id, truck_number FROM trucks ORDER BY truck_number')
            trucks = self.cursor.fetchall()
            truck_values = [f"{truck[0]} - {truck[1]}" for truck in trucks]
            self.delivery_truck_combo['values'] = truck_values
            
            # Update driver combo - include all drivers so existing deliveries can show their assigned driver
            self.cursor.execute('SELECT id, name FROM drivers ORDER BY name')
            drivers = self.cursor.fetchall()
            driver_values = [f"{driver[0]} - {driver[1]}" for driver in drivers]
            self.delivery_driver_combo['values'] = driver_values
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update combos: {str(e)}")
    
    def __del__(self):
        """Close database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()

            
def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = TruckDeliverySystem(root)
    root.mainloop()

if __name__ == "__main__":
    main()