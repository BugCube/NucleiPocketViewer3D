# NucleiPocketViewer3D

### NucleiPocketViewer3D by Dr. Frederic Strobl  
### Associated with the Krämer *et al.* 2026A Data Descriptor Study  
### Version 1.0 — Tested with Python 3.12 (64-bit)

---

## 1) Purpose

The NucleiPocketViewer3D provides fast, intuitive, and interactive 3D visualization of cell nuclei (or other objects) directly in a web browser. The application is built using the Dash framework and enables rapid inspection of spatial datasets without requiring specialized visualization software.

---

## 2) Running the Program

Download the Python script and the accompanying `data` folder from the repository.

### Requirements
The program requires the following Python packages:
- Dash  
- Plotly  
- pandas  
- NumPy  
- openpyxl  

Install all dependencies via:
```bash
pip install dash plotly pandas numpy openpyxl
```

### Execution
Run the script, for example in Visual Studio Code or via terminal:
```bash
python NucleiPocketViewer3D-V1.0.py
```

After launching, a local server will start. Open the displayed link (typically `http://127.0.0.1:8050`) in your web browser.

### Interaction
- **Dataset selection:** Choose `.xlsx` files from the `data` folder using the dropdown menu  
- **3D navigation:** Rotate via drag & drop  
- **View alignment:** Use the view buttons to switch to predefined perspectives  
- **Spatial filtering:** Use the filter buttons to mask regions along X, Y, and Z axes  

---

## 3) Adding your own Data

Place additional `.xlsx` files into the `data` folder. The program automatically detects all compatible files.

### Expected data structure
- At least four columns in the following order:
  1. Object name  
  2. X coordinate  
  3. Y coordinate  
  4. Z coordinate  

- A header row is **recommended**  
  (If omitted, the first row will be interpreted as column names and will not be plotted.)

- Column names are not required, but the **column order must be correct**

- By default, the program expect coordinates to be in a range of 0 to 600 for x, 0 to 1100 for y, and 0 to 600 for z. Adjust according to your data in the **“Preferences”** section of the Python script.

---

## 4) Preferences

Visualization parameters (e.g. color scheme, marker size, opacity, and rendering ranges) can be adjusted in the **“Preferences”** section of the Python script.

---

## 5) Folder Structure

```text
project/
│
├── NucleiPocketViewer3D-V1.0.py
└── data/
    ├── Kraemer2026A-DS0001TP0028-NucleiCoordinates.xlsx
    ├── ...
    ├── your_dataset.xlsx
```

---

## 6) Notes

- The application is designed for rapid exploratory visualization rather than quantitative analysis  
- Incorrect column ordering may lead to misleading visualizations without raising an explicit error  
- If no Excel files are found in the `data` folder, the program will terminate with an error message  
