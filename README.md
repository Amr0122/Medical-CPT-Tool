# Medical-CPT-Tool
A desktop app for handling CPT codes and denials, built with Python and Tkinter.
# CPT GUI App

A simple GUI application for processing CPT codes and medical insurance files.  
Built with **Python + Tkinter**.

---

## 📌 Features
- Analyze insurance summary files to detect the most rejected CPT codes due to ICD mismatch.
- Clean and preprocess claim denial data automatically.
- Generate interactive dashboards to show the top rejected codes (e.g., 99214).
- Help medical billers match ICD ↔ CPT correctly before submitting claims.
- Export cleaned datasets for further analysis (Excel / Power BI).


---

## 🚀 Run Locally (for developers)

1. Clone the repo:
   ```bash
   git clone https://github.com/ِAmr0122/REPO-NAME.git
   cd REPO-NAME

⚙️ Build Your Own EXE   
pyinstaller --onefile --noconsole --icon=medical_icon.ico cpt_gui_app.py

📂 Files

cpt_gui_app.py → main script

available_remark_codes.txt → remark codes

doctor_setting.json → doctor settings

medical_icon.ico → app icon

---
## 📌 requirements
- pandas
- openpyxl
- tk
- pyinstaller
- matplotlib
- seaborn
- plotly
----
  
⚡ Now you’re ready To Used 
