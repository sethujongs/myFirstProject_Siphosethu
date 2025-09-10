from flask import Flask, render_template, request, jsonify
import csv
import json
import os
from werkzeug.utils import secure_filename

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
    return render_template('simple_dashboard.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle CSV file upload (simplified version without Excel)"""
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
            
            # Read the CSV file
            current_data = []
            with open(filepath, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    current_data.append(row)
            
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
    
    return jsonify({'error': 'Invalid file format. Please upload a CSV file.'}), 400

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
    ALLOWED_EXTENSIONS = {'csv'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_basic_stats(data):
    """Generate basic statistics for the data"""
    if not data:
        return {}
    
    columns = list(data[0].keys())
    numeric_columns = []
    
    # Check which columns are numeric
    for col in columns:
        try:
            float(data[0][col])
            numeric_columns.append(col)
        except (ValueError, TypeError):
            pass
    
    stats = {
        'total_rows': len(data),
        'total_columns': len(columns),
        'numeric_columns': len(numeric_columns),
        'text_columns': len(columns) - len(numeric_columns),
        'column_info': []
    }
    
    for column in columns:
        values = [row[column] for row in data if row[column]]
        unique_values = len(set(values))
        missing = len(data) - len(values)
        
        col_info = {
            'name': column,
            'type': 'numeric' if column in numeric_columns else 'text',
            'missing': missing,
            'unique_values': unique_values
        }
        
        if column in numeric_columns:
            numeric_values = [float(v) for v in values if v]
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
            html += f'<td>{value}</td>'
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
            y_val = float(row[y_column]) if row[y_column] else 0
            groups[x_val] = groups.get(x_val, 0) + y_val
        
        return {
            'type': 'bar',
            'x': list(groups.keys()),
            'y': list(groups.values()),
            'title': f'{chart_type.title()} Chart: {y_column} by {x_column}'
        }
    
    elif chart_type == 'line':
        x_vals = [row[x_column] for row in data]
        y_vals = [float(row[y_column]) if row[y_column] else 0 for row in data]
        
        return {
            'type': 'line',
            'x': x_vals,
            'y': y_vals,
            'title': f'{chart_type.title()} Chart: {y_column} vs {x_column}'
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
    app.run(debug=True, host='0.0.0.0', port=5000)