import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import os
from mainScript import main

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()
        self.set_default_output_directory()

    def create_widgets(self):
        self.file_label = tk.Label(self, text="Excel File:")
        self.file_label.grid(row=0, column=0, padx=5, pady=5)
        self.file_entry = tk.Entry(self, width=50)
        self.file_entry.grid(row=0, column=1, padx=5, pady=5)
        self.file_button = tk.Button(self, text="Browse", command=self.browse_file)
        self.file_button.grid(row=0, column=2, padx=5, pady=5)

        self.output_label = tk.Label(self, text="Output Directory:")
        self.output_label.grid(row=1, column=0, padx=5, pady=5)
        self.output_entry = tk.Entry(self, width=50)
        self.output_entry.grid(row=1, column=1, padx=5, pady=5)
        self.output_button = tk.Button(self, text="Browse", command=self.browse_output)
        self.output_button.grid(row=1, column=2, padx=5, pady=5)

        self.log_text = tk.Text(self, height=10, width=70)
        self.log_text.grid(row=2, column=0, columnspan=3, padx=5, pady=5)
        
        self.start_button = tk.Button(self, text="Start", command=self.start_processing)
        self.start_button.grid(row=3, column=1, pady=5)

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if file_path:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)

    def browse_output(self):
        output_dir = filedialog.askdirectory()
        if output_dir:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, output_dir)

    def log(self, message):
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)
        print(message)  # Also print to the console for additional visibility

    def start_processing(self):
        file_path = self.file_entry.get()
        output_dir = self.output_entry.get()
        
        if not file_path or not output_dir:
            messagebox.showerror("Error", "Please select both file and output directory.")
            return
        
        thread = threading.Thread(target=self.execute_script, args=(file_path, output_dir))
        thread.start()

    def execute_script(self, file_path, output_dir):
        try:
            channel_sheet = 'Channel_4_1'
            global_info_sheet = 'Global_Info'
            self.log("Starting process...")
            main(file_path, channel_sheet, global_info_sheet, output_dir, self.log)
        except Exception as e:
            self.log(f"Error: {str(e)}")
            messagebox.showerror("Error", str(e))

    def set_default_output_directory(self):
        default_output_dir = "/Users/hunmac/Python-CV-Visualizer/processedData"
        if not os.path.exists(default_output_dir):
            os.makedirs(default_output_dir)
        self.output_entry.insert(0, default_output_dir)

root = tk.Tk()
root.title("CV Visualizer")
app = Application(master=root)
app.mainloop()
