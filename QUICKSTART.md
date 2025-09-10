# 🚀 Quick Start Guide

Get your Excel Analytics Dashboard running in 3 minutes!

## Step 1: Install & Run

```bash
# Clone and enter directory
git clone https://github.com/sethujongs/myFirstProject_Siphosethu.git
cd myFirstProject_Siphosethu

# Install dependencies
pip install Flask openpyxl

# Start the dashboard
python excel_app.py
```

## Step 2: Open in Browser

Navigate to: **http://localhost:5001**

## Step 3: Upload Data

1. Click "Choose File"
2. Select any Excel (.xlsx) or CSV file
3. Click "Upload & Analyze"

## Step 4: Create Visualizations

1. Select chart type (Bar, Line, or Pie)
2. Choose X-axis and Y-axis columns
3. Click "✨ Generate Chart"

## 🎯 Tips

- **Excel files**: Supported formats are .xlsx and .xls
- **CSV files**: Make sure the first row contains column headers
- **Best columns for X-axis**: Categories, dates, text values
- **Best columns for Y-axis**: Numbers, quantities, measurements

## 📊 Sample Data

Create a test file `sample.csv`:
```csv
Product,Sales,Price,Category
Laptop,150,999.99,Electronics
Phone,200,699.99,Electronics
Tablet,80,399.99,Electronics
Keyboard,300,49.99,Accessories
Mouse,250,29.99,Accessories
```

## 🆘 Troubleshooting

**"Excel support not available"**: Install openpyxl with `pip install openpyxl`

**Port already in use**: Change port in `excel_app.py` (line 289): `app.run(port=5002)`

**File upload fails**: Check file size (max 16MB) and format

---

That's it! You now have a fully functional analytics dashboard. 🎉