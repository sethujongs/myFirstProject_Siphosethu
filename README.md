# 📊 Excel Analytics Dashboard

A powerful web-based dashboard for analyzing and visualizing Excel and CSV data. Upload your spreadsheets and instantly generate comprehensive analytics and beautiful visualizations.

## 🚀 Features

- **📁 File Upload**: Support for Excel (.xlsx, .xls) and CSV files
- **📊 Smart Analytics**: Automatic statistics, data types, and quality analysis
- **📈 Visualizations**: Interactive bar charts, line charts, and pie charts
- **💎 Modern UI**: Professional design with gradient styling and responsive layout
- **🔍 Data Preview**: Instant preview of uploaded data with detailed column information
- **⚡ Real-time**: Fast processing and immediate results

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/sethujongs/myFirstProject_Siphosethu.git
   cd myFirstProject_Siphosethu
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   # For full Excel support (recommended)
   python excel_app.py
   
   # Or for CSV-only version
   python simple_app.py
   ```

4. **Open in browser**:
   - Excel version: http://localhost:5001
   - CSV version: http://localhost:5000

## 📈 Usage

1. **Upload Data**: Click "Choose File" and select your Excel or CSV file
2. **View Analytics**: Automatically generated statistics appear instantly
3. **Create Charts**: Select chart type and columns to visualize your data
4. **Explore**: Use the data preview and column information for insights

## 🎨 Screenshots

### Welcome Screen
![Dashboard Welcome](https://github.com/user-attachments/assets/409a8ad8-43fa-4d0d-8edb-70879493cd84)

### Data Analysis
![Data Analysis View](https://github.com/user-attachments/assets/10c44944-b9ee-4573-abc8-579bbedd2cc9)

## 📋 Requirements

- Python 3.7+
- Flask 2.3.3
- openpyxl 3.1.2 (for Excel support)
- Bootstrap 5.1.3 (loaded via CDN)

## 🗂️ Project Structure

```
myFirstProject_Siphosethu/
├── excel_app.py           # Main Flask app with Excel support
├── simple_app.py          # Lightweight CSV-only version
├── requirements.txt       # Python dependencies
├── templates/
│   ├── excel_dashboard.html    # Enhanced dashboard template
│   └── simple_dashboard.html   # Basic CSV dashboard
└── static/
    ├── css/style.css      # Custom styling
    └── js/dashboard.js    # Interactive functionality
```

## 🚀 Getting Started

1. Start with sample data by creating a CSV file with columns like:
   ```csv
   Product,Sales,Price,Category,Quarter
   Laptop,150,999.99,Electronics,Q1
   Phone,200,699.99,Electronics,Q2
   ```

2. Upload the file and explore the generated analytics

3. Create visualizations by selecting different chart types and columns

## 🤝 Contributing

This is a learning project. Feel free to fork, experiment, and improve!

## 📄 License

Open source - feel free to use and modify as needed.

---

Built with ❤️ using Flask, Bootstrap, and modern web technologies.
