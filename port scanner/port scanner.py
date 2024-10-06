import tkinter as tk
from tkinter import scrolledtext, messagebox
from tkinter.ttk import Label, Entry, Button, Combobox
import webbrowser
import asyncio
import threading
import socket
import time
import datetime
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class PortScannerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Port Scanner")
        self.configure(bg="#f0f0f0")  # Set background color

        self.create_widgets()

    def create_widgets(self):
        # Project Info button
        project_info_button = tk.Button(self, text="Project Info", command=self.open_project_info, bg="lightblue", fg="black", font=("Arial", 12, "bold"))
        project_info_button.grid(row=0, column=1, padx=10, pady=10)

        Label(self, text="Enter Web Address:", font=("Arial", 12), style="Label.TLabel").grid(row=1, column=0, padx=5,
                                                                                              pady=5, sticky="e")
        self.web_address_entry = Entry(self, font=("Arial", 12))
        self.web_address_entry.grid(row=1, column=1, padx=5, pady=5)
        get_ip_button = tk.Button(self, text="Get IP Address", command=self.get_ip_address, bg="lightblue", fg="black", font=("Arial", 12, "bold"))
        get_ip_button.grid(row=1, column=2, padx=(0, 10), pady=5, sticky="w")  # Adjusted padx and added sticky option

        Label(self, text="IP Address:", font=("Arial", 12), style="Label.TLabel").grid(row=2, column=0, padx=5,
                                                                                       pady=5, sticky="e")
        self.ip_address_label = Label(self, text="", font=("Arial", 12), style="Label.TLabel")
        self.ip_address_label.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        Label(self, text="Enter Start Port:", font=("Arial", 12), style="Label.TLabel").grid(row=3, column=0, padx=5,
                                                                                             pady=5, sticky="e")
        self.start_port_entry = Entry(self, font=("Arial", 12))
        self.start_port_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        Label(self, text="Enter End Port:", font=("Arial", 12), style="Label.TLabel").grid(row=4, column=0, padx=5,
                                                                                           pady=5, sticky="e")
        self.end_port_entry = Entry(self, font=("Arial", 12))
        self.end_port_entry.grid(row=4, column=1, padx=5, pady=5, sticky="w")

        Label(self, text="Display Type:", font=("Arial", 12), style="Label.TLabel").grid(row=5, column=0, padx=5,
                                                                                         pady=5, sticky="e")
        self.display_type_combobox = Combobox(self, values=['All Ports', 'Important Ports'], font=("Arial", 12),
                                              state='readonly')
        self.display_type_combobox.grid(row=5, column=1, padx=5, pady=5, sticky="w")
        self.display_type_combobox.current(1)  # Set default option
        self.display_type_combobox.config(style="Bold.TCombobox")  # Make text bold

        scan_button = tk.Button(self, text="Scan Ports", command=self.scan_ports, bg="lightblue", fg="black", font=("Arial", 12, "bold"))
        scan_button.grid(row=6, column=0, columnspan=3, padx=5, pady=5)

        self.status_label = Label(self, text="", font=("Arial", 12), style="Label.TLabel")
        self.status_label.grid(row=7, column=0, columnspan=3, padx=5, pady=5)

        self.output_text = scrolledtext.ScrolledText(self, width=60, height=20, wrap=tk.WORD, font=("Arial", 12),
                                                     state='disabled', foreground="#000000", background="#F8F177")
        self.output_text.grid(row=8, column=0, columnspan=3, padx=5, pady=5)

        save_report_button = tk.Button(self, text="Save Report", command=self.save_report, bg="lightblue", fg="black", font=("Arial", 12, "bold"))
        save_report_button.grid(row=9, column=0, columnspan=3, padx=5, pady=5)

        self.style = tk.ttk.Style()
        #self.style.configure("Custom.TButton", font=("Arial", 12, "bold"), bg="lightblue", fg="black")  # Added borderwidth and highlightthickness
      # self.style.map("Custom.TButton",
                      # foreground=[('active', '#FF0000'),
                                #   ('disabled', '#A9A9A9')])  # Change text color on active and disabled states
        self.style.configure("Label.TLabel", foreground='#000000', background="#7CEA9C")
        self.style.configure("Bold.TCombobox", font=("Arial", 12, "bold"))  # Combobox text style

        self.configure(bg="#000000")  # Set background color for the window

        # Center elements when window is maximized
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)


    def get_ip_address(self):
        web_address = self.web_address_entry.get()
        try:
            ip_address = socket.gethostbyname(web_address)
            self.ip_address_label.config(text=f"IP Address: {ip_address}")
        except Exception as e:
            messagebox.showerror("Error", f"Error getting IP address: {e}")

    async def scan_port(self, ip, port, progress_signal, open_ports_signal):
        try:
            reader, writer = await asyncio.open_connection(ip, port)
            writer.close()
            open_ports_signal.emit(f"Port {port} is open on {ip}\n")
        except Exception as e:
            print(f"Error scanning port {port}: {e}")
            #open_ports_signal.emit(f"Error scanning port {port}: {e}\n")
        progress_signal.emit(f"Scanning port {port}...")

    async def port_scan(self, ip_address, start_port, end_port, display_type, progress_signal, open_ports_signal):
        start_time = time.time()
        try:
            for port in range(start_port, end_port + 1):
                if display_type == 'All Ports' or (display_type == 'Important Ports' and port in important_ports):
                    await self.scan_port(ip_address, port, progress_signal, open_ports_signal)
        except Exception as e:
            print(f"Error during port scan: {e}")
        end_time = time.time()
        elapsed_time = end_time - start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        progress_signal.emit(f"Scan completed in {minutes} minutes {seconds} seconds.")

    def scan_ports(self):
        ip_address = self.ip_address_label.cget("text").split(":")[1].strip()  # Get IP address from label
        start_port = int(self.start_port_entry.get())
        end_port = int(self.end_port_entry.get())
        display_type = self.display_type_combobox.get()

        print("Starting port scan...")
        self.status_label.config(text="Starting port scan...")

        self.output_text.configure(state='normal')
        self.output_text.delete('1.0', tk.END)
        self.output_text.configure(state='disabled')

        progress_signal = ProgressSignal(self.status_label)
        open_ports_signal = OpenPortsSignal(self.output_text)

        def run_port_scan():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.port_scan(ip_address, start_port, end_port, display_type, progress_signal, open_ports_signal))
                loop.close()
            except Exception as e:
                print(f"Error during port scan: {e}")
                self.status_label.config(text=f"Error: {e}")

        threading.Thread(target=run_port_scan).start()

    def save_report(self):
        ip_address = self.ip_address_label.cget("text").split(":")[1].strip()  # Get IP address from label
        start_port = int(self.start_port_entry.get())
        end_port = int(self.end_port_entry.get())
        display_type = self.display_type_combobox.get()
        open_ports = self.output_text.get('1.0', tk.END).strip().split('\n')

        filename = f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pdf"
        filepath = os.path.join("D:/ports data", filename)

        try:
            c = canvas.Canvas(filepath, pagesize=letter)
            c.drawString(100, 750, f"Web Address: {ip_address}")
            c.drawString(100, 730, f"Port Range: {start_port}-{end_port}")
            c.drawString(100, 710, "Open Ports:")

            y_coordinate = 690
            for port in open_ports:
                c.drawString(100, y_coordinate, port)
                y_coordinate -= 20

            c.save()

            messagebox.showinfo("Save Report", f"Report saved successfully as {filename} in D:/ports data")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving report: {e}")

    def open_project_info(self):
        html_content = """
           <!DOCTYPE html>
           <html lang="en">
           <head>
               <meta charset="UTF-8">
               <meta http-equiv="X-UA-Compatible" content="IE=edge">
               <meta name="viewport" content="width=device-width, initial-scale=1.0">
               <title>Project Information</title>
               <style>
                   body {
                       font-family: Arial, sans-serif;
                       background-color: #f5f5f5;
                       margin: 0;
                       padding: 20px;
                   }
                   .container {
                       max-width: 800px;
                       margin: 0 auto;
                       background-color: #fff;
                       padding: 20px;
                       box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                   }
                   h1, h2 {
                       color: #333;
                   }
                   table {
                       width: 100%;
                       border-collapse: collapse;
                       margin-bottom: 20px;
                       background-color: #fff;
                       font-size: 14px;
                   }
                   th, td {
                       padding: 10px;
                       text-align: left;
                       border: 1px solid #ccc;
                   }
                   th {
                       background-color: #ddd;
                   }
               </style>
           </head>
           <body>
               <div class="container">
                   <h1>Project Information</h1>
                   <p>This project was developed by us as part of a Cyber Security Internship. This project is designed to check all the open ports in a website:</p>
                   <table>
                       <tr>
                           <th>Project Details</th>
                           <th>Value</th>
                       </tr>
                       <tr>
                           <td>Project Name</td>
                           <td>Port Scanner</td>
                       </tr>
                       <tr>
                           <td>Project Description</td>
                           <td>To Scan all the open ports in a website and save them as a report in pdf format.</td>
                       </tr>
                       <tr>
                           <td>Project Start Date</td>
                           <td>17-02-2024</td>
                       </tr>
                       <tr>
                           <td>Project End Date</td>
                           <td>29-03-2024</td>
                       </tr>
                       <tr>
                           <td>Project Status</td>
                           <td>Completed</td>
                       </tr>
                   </table>
                   <h3>Developer Details</h3>
                   <table>
                       <tr>
                           <th>Name</th>
                           <th>Email</th>
                       </tr>
                       <tr>
                           <td>Palagati Sai Gowtham Reddy</td>
                           <td>saigowthamreddy@gmail.com</td>
                       </tr>
                       <tr>
                           <td>Bsuneel</td>
                           <td>suneel@gmail.com</td>
                       </tr>
                       <tr>
                           <td>Data 5</td>
                           <td>Data 6</td>
                       </tr>
                       <tr>
                           <td>Data 7</td>
                           <td>Data 8</td>
                       </tr>
                       <tr>
                           <td>Data 9</td>
                           <td>Data 10</td>
                       </tr>
                   </table>
               </div>
           </body>
           </html>
           """
        with open("project_info.html", "w") as f:
            f.write(html_content)
        webbrowser.open_new("project_info.html")


class ProgressSignal:
    def __init__(self, label):
        self.label = label

    def emit(self, message):
        print(message)
        self.label.config(text=message)

class OpenPortsSignal:
    def __init__(self, output_text):
        self.output_text = output_text

    def emit(self, message):
        self.output_text.configure(state='normal')
        self.output_text.insert(tk.END, message)
        self.output_text.configure(state='disabled')

# Define array of important ports up to 65535
important_ports = [
    21, 22, 23, 25, 53, 80, 110, 119, 123, 135, 137, 138, 139, 143, 161, 194, 389,
    443, 445, 465, 514, 563, 587, 636, 993, 995, 1080, 1433, 1702, 1720, 1723, 2082,
    2083, 3128, 3306, 3389, 5432, 5800, 5900, 8080, 10000, 20000,
]

if __name__ == "__main__":
    app = PortScannerApp()
    app.mainloop()
