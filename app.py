import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename

# -----------------------------
# Flask Application Setup
# -----------------------------
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'supersecretkey'  # Required for session support
ALLOWED_EXTENSIONS = {'xlsx'}

# -----------------------------
# Helper Functions
# -----------------------------
def allowed_file(filename):
    """
    Check if the uploaded file has a valid extension (.xlsx).
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_plot(df, graph_type):
    """
    Generates Income vs Expense plot and saves as static/plot.png.
    Supports 'line', 'bar', and 'pie' chart types.
    """
    plt.figure(figsize=(10, 5))

    if graph_type == 'line':
        plt.plot(df['Month'], df['Income'], label='Income', marker='o', color='#b4005a')
        plt.plot(df['Month'], df['Expense'], label='Expense', marker='o', color='#fbb1d3')
    elif graph_type == 'bar':
        width = 0.35
        x = range(len(df['Month']))
        plt.bar([i - width/2 for i in x], df['Income'], width=width, label='Income', color='#b4005a', alpha=0.85)
        plt.bar([i + width/2 for i in x], df['Expense'], width=width, label='Expense', color='#fbb1d3', alpha=0.85)
        plt.xticks(x, df['Month'], rotation=45)
    elif graph_type == 'pie':
        total_income = df['Income'].sum()
        total_expense = df['Expense'].sum()
        plt.pie([total_income, total_expense],
                labels=['Total Income', 'Total Expense'],
                autopct='%1.1f%%',
                startangle=90,
                colors=['#b4005a','#fbb1d3'])
        plt.title('Income vs Expense (Pie Chart)')

    if graph_type != 'pie':
        plt.xlabel('Month')
        plt.ylabel('Amount')
        plt.title('Income vs Expense (Last 12 Months)')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()

    plot_path = os.path.join('static', 'plot.png')
    plt.savefig(plot_path)
    plt.close()

def compute_stats(df):
    """
    Compute summary statistics from DataFrame.
    """
    return {
        'highest_income_month': df.loc[df['Income'].idxmax(), 'Month'] if 'Income' in df.columns else '',
        'lowest_income_month': df.loc[df['Income'].idxmin(), 'Month'] if 'Income' in df.columns else '',
        'highest_expense_month': df.loc[df['Expense'].idxmax(), 'Month'] if 'Expense' in df.columns else '',
        'lowest_expense_month': df.loc[df['Expense'].idxmin(), 'Month'] if 'Expense' in df.columns else '',
        'avg_income': df['Income'].mean() if 'Income' in df.columns else 0,
        'avg_expense': df['Expense'].mean() if 'Expense' in df.columns else 0
    }

def get_latest_file():
    """
    Returns the path to the most recently uploaded Excel file.
    """
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    if not files:
        return None
    return max([os.path.join(app.config['UPLOAD_FOLDER'], f) for f in files],
               key=os.path.getctime)

# -----------------------------
# Routes
# -----------------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return redirect(request.url)

    # Save the uploaded file
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Load Excel data
    df = pd.read_excel(filepath)
    if not {'Month', 'Income', 'Expense'}.issubset(df.columns):
        return "Excel file must contain 'Month', 'Income', and 'Expense' columns."

    # Default graph type
    graph_type = 'line'
    session['graph_type'] = graph_type
    generate_plot(df, graph_type)
    stats = compute_stats(df)

    return render_template(
        'results.html',
        stats=stats,
        plot_url=url_for('static', filename='plot.png'),
        data=df.to_dict(orient='records'),
        graph_type=graph_type
    )

@app.route('/results')
def results():
    latest_file = get_latest_file()
    if not latest_file:
        return redirect(url_for('index'))

    df = pd.read_excel(latest_file)
    graph_type = session.get('graph_type', 'line')
    generate_plot(df, graph_type)
    stats = compute_stats(df)

    return render_template(
        'results.html',
        stats=stats,
        plot_url=url_for('static', filename='plot.png'),
        data=df.to_dict(orient='records'),
        graph_type=graph_type
    )

@app.route('/change_graph', methods=['POST'])
def change_graph():
    latest_file = get_latest_file()
    if not latest_file:
        return redirect(url_for('index'))

    df = pd.read_excel(latest_file)
    graph_type = request.form.get('graph_type', 'line')
    session['graph_type'] = graph_type
    generate_plot(df, graph_type)
    stats = compute_stats(df)

    return render_template(
        'results.html',
        stats=stats,
        plot_url=url_for('static', filename='plot.png'),
        data=df.to_dict(orient='records'),
        graph_type=graph_type
    )

@app.route('/month/<month>')
def month_details(month):
    latest_file = get_latest_file()
    if not latest_file:
        return redirect(url_for('index'))

    df = pd.read_excel(latest_file)
    month_data = df[df['Month'] == month].to_dict(orient='records')
    if not month_data:
        return f"No data available for {month}."

    avg_income = df['Income'].mean() if 'Income' in df.columns else 0
    avg_expense = df['Expense'].mean() if 'Expense' in df.columns else 0
    this_income = month_data[0]['Income']
    this_expense = month_data[0]['Expense']

    income_bar_width = int((this_income / avg_income) * 120) if avg_income else 0
    expense_bar_width = int((this_expense / avg_expense) * 120) if avg_expense else 0

    return render_template(
        'month_details.html',
        month=month,
        details=month_data[0],
        avg_income=avg_income,
        avg_expense=avg_expense,
        income_bar_width=income_bar_width,
        expense_bar_width=expense_bar_width
    )

# -----------------------------
# Run Application
# -----------------------------
if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs('static', exist_ok=True)
    print("Starting Flask app...")
    app.run(debug=True)

