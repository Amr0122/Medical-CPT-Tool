import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from PIL import Image, ImageTk
import pandas as pd
import json
import shutil
from datetime import datetime
import sys, os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS  # مكان الملفات لما يكون exe
    except Exception:
        base_path = os.path.abspath(".")  # مكان الملفات في وضع dev
    return os.path.join(base_path, relative_path)


# Load doctor settings
settings_file = "doctor_settings.json"
if os.path.exists(settings_file):
    with open(settings_file, "r", encoding="utf-8") as f:
        doctor_settings = json.load(f)
else:
    doctor_settings = {}

# Load available remark codes
with open(resource_path("available_remark_codes.txt"), "r", encoding="utf-8") as f:
    available_codes = [line.strip() for line in f.readlines()]

class CPTApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CPT Denial Analyzer")
        self.root.geometry("1000x600")
        self.root.configure(bg="#1e1e2f")

        self.file_path = ""
        self.selected_doctor = tk.StringVar()
        self.search_var = tk.StringVar()
        self.check_vars = {}

        # Sidebar
        sidebar = tk.Frame(root, bg="#252537", width=200)
        sidebar.pack(side="left", fill="y")

        tk.Label(sidebar, text="Doctor:", bg="#252537", fg="white", font=("Segoe UI", 10)).pack(pady=5)
        self.doctor_menu = ttk.Combobox(sidebar, textvariable=self.selected_doctor, values=list(doctor_settings.keys()))
        self.doctor_menu.pack(pady=5)

        tk.Button(sidebar, text="Add Doctor", command=self.add_doctor, bg="#007acc", fg="white").pack(fill="x", padx=10, pady=5)
        tk.Button(sidebar, text="Edit Doctor Settings", command=self.edit_doctor_settings, bg="#007acc", fg="white").pack(fill="x", padx=10, pady=5)
        tk.Button(sidebar, text="Delete Doctor", command=self.delete_doctor, bg="#e53935", fg="white").pack(fill="x", padx=10, pady=5)
        tk.Button(sidebar, text="Upload File", command=self.select_file, bg="#007acc", fg="white").pack(fill="x", padx=10, pady=5)
        tk.Button(sidebar, text="Run Analysis", command=self.run_analysis, bg="#00bfa5", fg="white").pack(fill="x", padx=10, pady=5)
        tk.Button(sidebar, text="Settings", command=self.show_settings, bg="#444", fg="white").pack(fill="x", padx=10, pady=5)

        # Main Panel
        main_panel = tk.Frame(root, bg="#1e1e2f")
        main_panel.pack(side="right", fill="both", expand=True)

        # Logo
        logo_path = "Image_3.png"
        if os.path.exists(logo_path):
            logo_img = Image.open(logo_path).resize((150, 150))
            self.logo = ImageTk.PhotoImage(logo_img)
            tk.Label(main_panel, image=self.logo, bg="#1e1e2f").pack(pady=10)

        # Title
        tk.Label(main_panel, text="CPT Denial Summary", font=("Segoe UI", 14, "bold"), fg="white", bg="#1e1e2f").pack(pady=5)

        # Search
        tk.Entry(main_panel, textvariable=self.search_var, font=("Segoe UI", 10), bg="#2e2e3f", fg="white", insertbackground="white").pack(pady=5)
        tk.Button(main_panel, text="Search", command=self.filter_table, bg="#007acc", fg="white").pack(pady=5)

        # Table Frame
        self.table_frame = tk.Frame(main_panel, bg="#1e1e2f")
        self.table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree = None
        self.load_summary_table()

    def add_doctor(self):
        name = simpledialog.askstring("Add Doctor", "Enter doctor's name:")
        if name:
            doctor_settings[name] = {
                "remark_codes": [],
                "default_file": "",
                "output_dir": f"output_{name.replace(' ', '_')}",
                "icd_codes": []
            }
            with open(settings_file, "w", encoding="utf-8") as f:
                json.dump(doctor_settings, f, indent=4)
            self.doctor_menu["values"] = list(doctor_settings.keys())
            self.selected_doctor.set(name)

    def delete_doctor(self):
        doctor = self.selected_doctor.get()
        if not doctor:
            messagebox.showerror("Error", "Please select a doctor to delete.")
            return
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete doctor '{doctor}'?")
        if confirm:
            if doctor in doctor_settings:
                # امسح الفولدر بتاع الدكتور لو موجود
                output_dir = doctor_settings[doctor].get("output_dir", "")
                if output_dir and os.path.exists(output_dir):
                    try:
                        shutil.rmtree(output_dir)
                    except Exception as e:
                        messagebox.showwarning("Warning", f"Could not delete folder:\n{e}")

                # امسح الدكتور من الإعدادات
                del doctor_settings[doctor]
                with open(settings_file, "w", encoding="utf-8") as f:
                    json.dump(doctor_settings, f, indent=4)
                self.doctor_menu["values"] = list(doctor_settings.keys())
                self.selected_doctor.set("")
                messagebox.showinfo("Deleted", f"Doctor '{doctor}' has been deleted (and folder removed).")

    def select_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")])
        messagebox.showinfo("File Selected", f"Selected file:\n{self.file_path}")

    def run_analysis(self):
        doctor = self.selected_doctor.get() or "default"
        selected_codes = doctor_settings.get(doctor, {}).get("remark_codes", [])
        if not selected_codes or not self.file_path:
            messagebox.showerror("Error", "Please select a doctor, file, and remark codes.")
            return
        try:
            if self.file_path.endswith(".csv"):
                df_raw = pd.read_csv(self.file_path, encoding='utf-16', header=None)
            else:
                df_raw = pd.read_excel(self.file_path, engine="openpyxl", header=None)
            df = df_raw.iloc[:, 0].str.split('\\t', expand=True)
            columns = ["Facility", "Denial Code", "CPT Code", "Patient Acct No", "Denial Amount", "Denial Count", "Total1", "Total2", "Total3", "Total4"]
            df.columns = columns + ["Extra"] if len(df.columns) > len(columns) else columns
            filtered_df = df[df["Denial Code"].isin(selected_codes)]
            cpt_summary = filtered_df["CPT Code"].value_counts().reset_index()
            cpt_summary.columns = ["CPT Code", "Denial Count"]

            # اسم الشهر الحالي
            month_name = datetime.now().strftime("%b%Y")  # Aug2025
            output_dir = f"output_{doctor.replace(' ', '_')}_{month_name}"
            os.makedirs(output_dir, exist_ok=True)

            # نسمي الملفات بالـ month suffix
            filtered_file = os.path.join(output_dir, f"filtered_denials_{month_name}.csv")
            summary_file = os.path.join(output_dir, f"cpt_summary_{month_name}.csv")

            filtered_df.to_csv(filtered_file, index=False)
            cpt_summary.to_csv(summary_file, index=False)

            doctor_settings[doctor]["default_file"] = self.file_path
            doctor_settings[doctor]["output_dir"] = output_dir
            with open(settings_file, "w", encoding="utf-8") as f:
                json.dump(doctor_settings, f, indent=4)
            messagebox.showinfo("Success", f"Analysis complete. Files saved in {output_dir}")
            self.load_summary_table(output_dir)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_summary_table(self, output_dir=None):
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        if output_dir:
            # دور على ملف الـ summary في الفولدر
            summary_file = [f for f in os.listdir(output_dir) if f.startswith("cpt_summary")][0]
            summary_file = os.path.join(output_dir, summary_file)
        else:
            summary_file = "cpt_summary.csv"
        if os.path.exists(summary_file):
            df_summary = pd.read_csv(summary_file)
        else:
            df_summary = pd.DataFrame(columns=["CPT Code", "Denial Count"])
        self.tree = ttk.Treeview(self.table_frame, columns=list(df_summary.columns), show="headings")
        for col in df_summary.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")
        for _, row in df_summary.iterrows():
            self.tree.insert("", "end", values=list(row))
        scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

    def filter_table(self):
        query = self.search_var.get().lower()
        for item in self.tree.get_children():
            values = self.tree.item(item)["values"]
            if any(query in str(v).lower() for v in values):
                self.tree.item(item, tags=("match",))
            else:
                self.tree.item(item, tags=("no_match",))
        self.tree.tag_configure("match", background="#2e2e3f", foreground="white")
        self.tree.tag_configure("no_match", background="#1e1e2f", foreground="#666")

    def edit_doctor_settings(self):
        doctor = self.selected_doctor.get()
        if not doctor:
            messagebox.showerror("Error", "Please select a doctor first.")
            return
        win = tk.Toplevel(self.root)
        win.title(f"Edit Settings for {doctor}")
        win.geometry("400x500")
        win.configure(bg="#1e1e2f")

        tk.Label(win, text="ICD Codes (comma separated):", bg="#1e1e2f", fg="white").pack(pady=5)
        icd_var = tk.StringVar(value=",".join(doctor_settings[doctor].get("icd_codes", [])))
        tk.Entry(win, textvariable=icd_var, bg="#2e2e3f", fg="white").pack(fill="x", padx=10)

        tk.Label(win, text="Select Remark Codes:", bg="#1e1e2f", fg="white").pack(pady=5)
        search_remark = tk.StringVar()
        tk.Entry(win, textvariable=search_remark, bg="#2e2e3f", fg="white").pack(fill="x", padx=10)

        codes_frame = tk.Frame(win, bg="#1e1e2f")
        codes_frame.pack(fill="both", expand=True, padx=10, pady=10)

        remark_vars = {}
        def update_codes():
            previous_selection = {
                code: var.get()
                for code, var in remark_vars.items()
            }
            for widget in codes_frame.winfo_children():
                widget.destroy()
            query = search_remark.get().lower()
            for code in available_codes:
                if query in code.lower():
                    var = tk.BooleanVar(value=previous_selection.get(code, code in doctor_settings[doctor].get("remark_codes", [])))
                    chk = tk.Checkbutton(codes_frame, text=code, variable=var, bg="#1e1e2f", fg="white", selectcolor="#333")
                    chk.pack(anchor="w")
                    remark_vars[code] = var

        search_remark.trace_add("write", lambda *args: update_codes())
        update_codes()

        def save_settings():
            doctor_settings[doctor]["icd_codes"] = [x.strip() for x in icd_var.get().split(",") if x.strip()]
            doctor_settings[doctor]["remark_codes"] = [code for code, var in remark_vars.items() if var.get()]
            with open(settings_file, "w", encoding="utf-8") as f:
                json.dump(doctor_settings, f, indent=4)
            messagebox.showinfo("Saved", "Doctor settings updated.")
            win.destroy()

        tk.Button(win, text="Save", command=save_settings, bg="#00bfa5", fg="white").pack(pady=10)

    def show_settings(self):
        win = tk.Toplevel(self.root)
        win.title("Application Settings")
        win.geometry("400x300")
        win.configure(bg="#1e1e2f")
        tk.Label(win, text="Settings Panel", font=("Segoe UI", 12, "bold"), fg="white", bg="#1e1e2f").pack(pady=10)
        tk.Label(win, text="(Future settings will appear here)", fg="gray", bg="#1e1e2f").pack(pady=5)

# Run the app
root = tk.Tk()
app = CPTApp(root)
root.iconbitmap(resource_path("medical_icon.ico"))
root.mainloop()
