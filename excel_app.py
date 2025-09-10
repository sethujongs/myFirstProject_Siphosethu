from flask import Flask, render_template, request, jsonify
import csv
import json
import os
from werkzeug.utils import secure_filename

# Try to import openpyxl for Excel support
try:
    import openpyxl
    EXCEL_SUPPORT = True
except ImportError:
    EXCEL_SUPPORT = False
    print("Excel support disabled - openpyxl not available")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Global variable to store current data
current_data = None

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('excel_dashboard.html', excel_support=EXCEL_SUPPORT)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle CSV and Excel file upload"""
    global current_data
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Determine file type and read accordingly
            if filename.endswith('.csv'):
                current_data = read_csv_file(filepath)
            elif filename.endswith('.xlsx') or filename.endswith('.xls'):
                if EXCEL_SUPPORT:
                    current_data = read_excel_file(filepath)
                else:
                    return jsonify({'error': 'Excel support not available. Please use CSV files.'}), 400
            else:
                return jsonify({'error': 'Unsupported file format'}), 400
            
            # Generate basic statistics
            stats = generate_basic_stats(current_data)
            
            # Clean up the uploaded file
            os.remove(filepath)
            
            return jsonify({
                'success': True, 
                'stats': stats,
                'columns': list(current_data[0].keys()) if current_data else [],
                'preview': generate_preview_table(current_data[:5])
            })
            
        except Exception as e:
            return jsonify({'error': f'Error processing file: {str(e)}'}), 500
    
    return jsonify({'error': 'Invalid file format. Please upload a CSV or Excel file.'}), 400

@app.route('/generate_chart', methods=['POST'])
def generate_chart():
    """Generate chart data for visualization"""
    global current_data
    
    if current_data is None:
        return jsonify({'error': 'No data loaded. Please upload a file first.'}), 400
    
    try:
        data = request.json
        chart_type = data.get('chart_type')
        x_column = data.get('x_column')
        y_column = data.get('y_column')
        
        chart_data = prepare_chart_data(current_data, chart_type, x_column, y_column)
        
        return jsonify({'chart_data': chart_data})
            
    except Exception as e:
        return jsonify({'error': f'Error generating chart: {str(e)}'}), 500

def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'} if EXCEL_SUPPORT else {'csv'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def read_csv_file(filepath):
    """Read CSV file and return data as list of dictionaries"""
    data = []
    with open(filepath, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)
    return data

def read_excel_file(filepath):
    """Read Excel file and return data as list of dictionaries"""
    if not EXCEL_SUPPORT:
        raise Exception("Excel support not available")
    
    # Load workbook
    wb = openpyxl.load_workbook(filepath, data_only=True)
    ws = wb.active
    
    # Get all data
    data = []
    rows = list(ws.rows)
    
    if not rows:
        return []
    
    # First row as headers
    headers = [cell.value for cell in rows[0]]
    
    # Remaining rows as data
    for row in rows[1:]:
        row_data = {}
        for i, cell in enumerate(row):
            if i < len(headers):
                # Convert cell values to strings, handling None values
                value = cell.value
                if value is None:
                    value = ""
                else:
                    value = str(value)
                row_data[headers[i]] = value
        data.append(row_data)
    
    return data

def generate_basic_stats(data):
    """Generate basic statistics for the data"""
    if not data:
        return {}
    
    columns = list(data[0].keys())
    numeric_columns = []
    
    # Check which columns are numeric
    for col in columns:
        try:
            # Try to convert first non-empty value to float
            for row in data:
                if row[col] and row[col].strip():
                    float(row[col])
                    numeric_columns.append(col)
                    break
        except (ValueError, TypeError, AttributeError):
            pass
    
    stats = {
        'total_rows': len(data),
        'total_columns': len(columns),
        'numeric_columns': len(numeric_columns),
        'text_columns': len(columns) - len(numeric_columns),
        'column_info': []
    }
    
    for column in columns:
        values = [row[column] for row in data if row[column] and str(row[column]).strip()]
        unique_values = len(set(values))
        missing = len(data) - len(values)
        
        col_info = {
            'name': column,
            'type': 'numeric' if column in numeric_columns else 'text',
            'missing': missing,
            'unique_values': unique_values
        }
        
        if column in numeric_columns:
            numeric_values = []
            for v in values:
                try:
                    numeric_values.append(float(v))
                except (ValueError, TypeError):
                    pass
            
            if numeric_values:
                col_info.update({
                    'mean': round(sum(numeric_values) / len(numeric_values), 2),
                    'min': min(numeric_values),
                    'max': max(numeric_values)
                })
        
        stats['column_info'].append(col_info)
    
    return stats

def generate_preview_table(data):
    """Generate HTML table for data preview"""
    if not data:
        return "<p>No data to preview</p>"
    
    html = '<table class="table table-striped"><thead><tr>'
    for column in data[0].keys():
        html += f'<th>{column}</th>'
    html += '</tr></thead><tbody>'
    
    for row in data:
        html += '<tr>'
        for value in row.values():
            # Truncate long values for display
            display_value = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
            html += f'<td>{display_value}</td>'
        html += '</tr>'
    
    html += '</tbody></table>'
    return html

def prepare_chart_data(data, chart_type, x_column, y_column):
    """Prepare data for chart visualization"""
    if chart_type == 'bar':
        # Group by x_column and sum y_column
        groups = {}
        for row in data:
            x_val = row[x_column]
            try:
                y_val = float(row[y_column]) if row[y_column] else 0
            except (ValueError, TypeError):
                y_val = 0
            groups[x_val] = groups.get(x_val, 0) + y_val
        
        return {
            'type': 'bar',
            'x': list(groups.keys()),
            'y': list(groups.values()),
            'title': f'Bar Chart: {y_column} by {x_column}'
        }
    
    elif chart_type == 'line':
        x_vals = [row[x_column] for row in data]
        y_vals = []
        for row in data:
            try:
                y_vals.append(float(row[y_column]) if row[y_column] else 0)
            except (ValueError, TypeError):
                y_vals.append(0)
        
        return {
            'type': 'line',
            'x': x_vals,
            'y': y_vals,
            'title': f'Line Chart: {y_column} vs {x_column}'
        }
    
    elif chart_type == 'pie':
        # Count occurrences of each value in x_column
        counts = {}
        for row in data:
            val = row[x_column]
            counts[val] = counts.get(val, 0) + 1
        
        return {
            'type': 'pie',
            'labels': list(counts.keys()),
            'values': list(counts.values()),
            'title': f'Pie Chart of {x_column}'
        }
    
    return {}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)