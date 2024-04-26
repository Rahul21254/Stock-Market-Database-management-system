import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import sqlite3
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class StockDBMS:
    def __init__(self, master):
        self.master = master
        self.master.title("Stock Market DBMS")
        
        # Set up custom style for buttons with rounded edges
        self.style = ttk.Style()
        self.style.theme_use("vista")  # Choose a theme (e.g., "clam", "alt", etc.)
        self.style.configure("TButton", foreground="black", font=("Arial", 10), anchor="center", relief=tk.FLAT, background="#FFA500", borderwidth=0, borderradius=8)  # Orange buttons with round edges
        self.style.map("TButton", background=[("active", "#FFD700")])  # Lighter shade on hover
        
        # Initialize current database
        self.current_db = "default.db"
        
        # Check if current database exists, if not create it
        if not os.path.exists(self.current_db):
            self.create_database(self.current_db)
        
        # Connect to SQLite database
        self.conn = sqlite3.connect(self.current_db)
        self.c = self.conn.cursor()
        
        # Left pane for management options
        self.left_pane = tk.PanedWindow(master, orient=tk.VERTICAL, bg="#87CEEB", bd=5, relief=tk.RIDGE)  # Light blue background
        self.left_pane.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(10, 5), pady=10)
        
        # Buttons for managing databases
        tk.Button(self.left_pane, text="Create Database", command=self.create_new_database, bg="#32CD32", fg="white").grid(row=0, column=0, columnspan=2, sticky="we", pady=(0, 5))  # Green button
        tk.Button(self.left_pane, text="Switch Database", command=self.switch_database, bg="#FF6347", fg="white").grid(row=1, column=0, columnspan=2, sticky="we", pady=(0, 5))  # Red button
        tk.Button(self.left_pane, text="Delete Database", command=self.delete_database, bg="#8A2BE2", fg="white").grid(row=2, column=0, columnspan=2, sticky="we", pady=(0, 5))  # Purple button
        
        # Labels and Entry fields for managing stocks
        tk.Label(self.left_pane, text="Symbol:", bg="#87CEEB").grid(row=3, column=0, sticky="w", pady=(10, 0))
        tk.Label(self.left_pane, text="Company Name:", bg="#87CEEB").grid(row=4, column=0, sticky="w")
        tk.Label(self.left_pane, text="Price:", bg="#87CEEB").grid(row=5, column=0, sticky="w")
        tk.Label(self.left_pane, text="Volume:", bg="#87CEEB").grid(row=6, column=0, sticky="w")
        
        self.symbol_entry = tk.Entry(self.left_pane)
        self.symbol_entry.grid(row=3, column=1, pady=(10, 0))
        
        self.company_entry = tk.Entry(self.left_pane)
        self.company_entry.grid(row=4, column=1)
        
        self.price_entry = tk.Entry(self.left_pane)
        self.price_entry.grid(row=5, column=1)
        
        self.volume_entry = tk.Entry(self.left_pane)
        self.volume_entry.grid(row=6, column=1)
        
        # Buttons for managing stocks
        ttk.Button(self.left_pane, text="Add Stock", command=self.add_stock).grid(row=7, column=0, columnspan=2, sticky="we", pady=(10, 0))
        ttk.Button(self.left_pane, text="Show Stocks", command=self.show_stocks).grid(row=8, column=0, columnspan=2, sticky="we")
        ttk.Button(self.left_pane, text="Export to Excel", command=self.export_to_excel).grid(row=9, column=0, columnspan=2, sticky="we")
        
        # Right pane divided into two halves
        self.right_pane = tk.PanedWindow(master, orient=tk.VERTICAL, bg="#F0E68C", bd=5, relief=tk.RIDGE)  # Light yellow background
        self.right_pane.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        
        # Upper half for tabular output
        self.upper_frame = tk.Frame(self.right_pane, bg="#FFE4B5", bd=3, relief=tk.RIDGE)  # Moccasin background
        self.right_pane.add(self.upper_frame)
        
        self.output_table = ttk.Treeview(self.upper_frame, columns=('Symbol', 'Company Name', 'Price', 'Volume'), show='headings')
        self.output_table.heading('Symbol', text='Symbol')
        self.output_table.heading('Company Name', text='Company Name')
        self.output_table.heading('Price', text='Price')
        self.output_table.heading('Volume', text='Volume')
        self.output_table.pack(fill=tk.BOTH, expand=1)
        
        # Lower half for graphical output
        self.lower_frame = tk.Frame(self.right_pane, bg="#FFDAB9", bd=3, relief=tk.RIDGE)  # Peachpuff background
        self.right_pane.add(self.lower_frame)
        
        self.graph_canvas = tk.Canvas(self.lower_frame, bg="#FFDAB9")  # Peachpuff background
        self.graph_canvas.pack(fill=tk.BOTH, expand=1)
        
        # Animation for buttons
        self.animate_buttons()
        
    def animate_buttons(self):
        # Button animation
        for button in self.left_pane.winfo_children():
            button.bind("<Enter>", lambda event, button=button: self.animate_enter(button))
            button.bind("<Leave>", lambda event, button=button: self.animate_leave(button))
            
    def animate_enter(self, button):
        self.style.configure(button.winfo_class(), background="#FFD700")  # Change background color on mouse hover
            
    def animate_leave(self, button):
        self.style.configure(button.winfo_class(), background="#FFA500")  # Restore original background color
        
    def add_stock(self):
        # Add stock to the database
        symbol = self.symbol_entry.get()
        company_name = self.company_entry.get()
        price = float(self.price_entry.get())
        volume = int(self.volume_entry.get())
        
        # Insert data into the table
        self.c.execute("INSERT INTO stocks VALUES (?, ?, ?, ?)", (symbol, company_name, price, volume))
        self.conn.commit()
        
        # Show stocks in the table
        self.show_stocks()
        
        # Update the graph
        self.plot_graph()

    def show_stocks(self):
        # Clear previous data
        for row in self.output_table.get_children():
            self.output_table.delete(row)
        
        # Fetch stocks from the database
        self.c.execute("SELECT rowid, * FROM stocks")
        stocks = self.c.fetchall()
        
        # Display stocks in the table
        if not stocks:
            messagebox.showinfo("Empty", "No stocks found!")
        else:
            for stock in stocks:
                self.output_table.insert('', 'end', text=stock[0], values=(stock[1], stock[2], stock[3], stock[4]))
        
        # Update the graph
        self.plot_graph()
        
    def plot_graph(self):
        self.c.execute("SELECT symbol, volume FROM stocks")
        stocks = self.c.fetchall()
        
        symbols = [stock[0] for stock in stocks]
        volumes = [stock[1] for stock in stocks]
        
        plt.bar(symbols, volumes)
        plt.xlabel('Symbol')
        plt.ylabel('Volume')
        plt.title('Stock Volume')
        
        # Display plot in canvas
        self.graph_canvas.delete("all")  # Clear previous plot
        self.canvas = FigureCanvasTkAgg(plt.gcf(), master=self.graph_canvas)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def export_to_excel(self):
        self.c.execute("SELECT * FROM stocks")
        data = self.c.fetchall()
        
        df = pd.DataFrame(data, columns=['Symbol', 'Company Name', 'Price', 'Volume'])
        df.to_excel("stock_data.xlsx", index=False)
        messagebox.showinfo("Exported", "Stock data exported to Excel successfully!")
    
    def create_new_database(self):
        db_name = simpledialog.askstring("Create New Database", "Enter database name:")
        if db_name:
            db_path = db_name + ".db"
            self.create_database(db_path)
            messagebox.showinfo("Success", f"Database '{db_name}' created successfully!")
        
    def switch_database(self):
        db_name = simpledialog.askstring("Switch Database", "Enter database name:")
        if db_name:
            db_path = db_name + ".db"
            if os.path.exists(db_path):
                self.current_db = db_path
                self.conn = sqlite3.connect(self.current_db)
                self.c = self.conn.cursor()
                messagebox.showinfo("Success", f"Switched to database '{db_name}'")
            else:
                messagebox.showerror("Error", f"Database '{db_name}' does not exist!")
        
    def delete_database(self):
        db_name = simpledialog.askstring("Delete Database", "Enter database name:")
        if db_name:
            db_path = db_name + ".db"
            if os.path.exists(db_path):
                os.remove(db_path)
                messagebox.showinfo("Success", f"Database '{db_name}' deleted successfully!")
            else:
                messagebox.showerror("Error", f"Database '{db_name}' does not exist!")
        
    def create_database(self, db_path):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS stocks
             (symbol TEXT, company_name TEXT, price REAL, volume INTEGER)''')
        conn.commit()
        conn.close()

root = tk.Tk()
root.geometry("1075x540") 
app = StockDBMS(root)
root.mainloop()
