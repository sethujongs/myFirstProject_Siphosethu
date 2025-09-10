from flask import Flask, render_template, request, jsonify, redirect, url_for
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.utils
import json
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Global variable to store current dataframe
current_df = None

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle Excel file upload"""
    global current_df
    
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
            
            # Read the Excel file
            if filename.endswith('.xlsx') or filename.endswith('.xls'):
                current_df = pd.read_excel(filepath)
            else:
                return jsonify({'error': 'Invalid file format. Please upload an Excel file.'}), 400
            
            # Generate basic statistics
            stats = generate_basic_stats(current_df)
            
            # Clean up the uploaded file
            os.remove(filepath)
            
            return jsonify({
                'success': True, 
                'stats': stats,
                'columns': current_df.columns.tolist(),
                'preview': current_df.head().to_html(classes='table table-striped')
            })
            
        except Exception as e:
            return jsonify({'error': f'Error processing file: {str(e)}'}), 500
    
    return jsonify({'error': 'Invalid file format'}), 400

@app.route('/generate_chart', methods=['POST'])
def generate_chart():
    """Generate a chart based on user selection"""
    global current_df
    
    if current_df is None:
        return jsonify({'error': 'No data loaded. Please upload a file first.'}), 400
    
    try:
        data = request.json
        chart_type = data.get('chart_type')
        x_column = data.get('x_column')
        y_column = data.get('y_column')
        
        fig = None
        
        if chart_type == 'bar':
            fig = px.bar(current_df, x=x_column, y=y_column, title=f'{chart_type.title()} Chart: {y_column} vs {x_column}')
        elif chart_type == 'line':
            fig = px.line(current_df, x=x_column, y=y_column, title=f'{chart_type.title()} Chart: {y_column} vs {x_column}')
        elif chart_type == 'scatter':
            fig = px.scatter(current_df, x=x_column, y=y_column, title=f'{chart_type.title()} Plot: {y_column} vs {x_column}')
        elif chart_type == 'histogram':
            fig = px.histogram(current_df, x=x_column, title=f'Histogram of {x_column}')
        elif chart_type == 'box':
            fig = px.box(current_df, y=y_column, title=f'Box Plot of {y_column}')
        elif chart_type == 'pie':
            # For pie charts, use value counts of the selected column
            value_counts = current_df[x_column].value_counts()
            fig = px.pie(values=value_counts.values, names=value_counts.index, title=f'Pie Chart of {x_column}')
        
        if fig:
            graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            return jsonify({'chart': graphJSON})
        else:
            return jsonify({'error': 'Invalid chart type'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Error generating chart: {str(e)}'}), 500

def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_basic_stats(df):
    """Generate basic statistics for the dataframe"""
    stats = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'numeric_columns': len(df.select_dtypes(include=['number']).columns),
        'text_columns': len(df.select_dtypes(include=['object']).columns),
        'missing_values': df.isnull().sum().sum(),
        'column_info': []
    }
    
    for column in df.columns:
        col_info = {
            'name': column,
            'type': str(df[column].dtype),
            'missing': df[column].isnull().sum(),
            'unique_values': df[column].nunique()
        }
        
        if df[column].dtype in ['int64', 'float64']:
            col_info.update({
                'mean': round(df[column].mean(), 2) if pd.notna(df[column].mean()) else 'N/A',
                'min': df[column].min() if pd.notna(df[column].min()) else 'N/A',
                'max': df[column].max() if pd.notna(df[column].max()) else 'N/A'
            })
        
        stats['column_info'].append(col_info)
    
    return stats

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)