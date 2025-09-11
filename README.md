# Siphosethu Analytics Dashboard

A professional, ultra-feminine analytics dashboard built with Flask, Pandas, and Matplotlib. This app allows users to upload an Excel file with monthly financial data, visualize income and expenses, and explore summary statistics and details for each month.

## Features
- **File Upload:** Upload an Excel file (`.xlsx`) with columns: `Month`, `Income`, `Expense`.
- **Dashboard:** View summary cards, dynamic graphs (line, bar, pie, area, scatter, step), and a monthly data table.
- **Month Details:** Click any month for a detailed view, including comparison bars and motivational design.
- **Ultra-Feminine Design:** Pastel color palette, soft shapes, and a motivational quote.
- **Upload Another File:** Easily upload new data from the dashboard.

## How to Use
1. **Install dependencies:**
   ```bash
   pip install flask pandas matplotlib openpyxl
   ```
2. **Run the app:**
   ```bash
   python app.py
   ```
3. **Open your browser:**
   Visit [http://127.0.0.1:5000](http://127.0.0.1:5000)
4. **Upload your Excel file:**
   - The file must have columns: `Month`, `Income`, `Expense`.
5. **Explore your dashboard:**
   - View summary statistics, switch graph types, and click months for details.

## File Structure
- `app.py` — Main Flask application
- `templates/` — HTML templates (`index.html`, `results.html`, `month_details.html`)
- `static/` — Static files (generated plot images)
- `uploads/` — Uploaded Excel files

## Example Excel Format
| Month   | Income | Expense |
|---------|--------|---------|
| January | 1200   | 800     |
| ...     | ...    | ...     |

## Customization
- Change colors, fonts, or layout in the HTML templates for a personalized look.
- Add more analytics or visualizations by editing `app.py` and templates.

## License
MIT License

---
Created with love for analytics and design. 💖
