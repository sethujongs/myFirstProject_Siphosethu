import pandas as pd
import numpy as np

# Create sample data for testing
np.random.seed(42)

# Create a sample dataset
data = {
    'Product': ['Laptop', 'Phone', 'Tablet', 'Monitor', 'Keyboard'] * 10,
    'Sales': np.random.randint(100, 1000, 50),
    'Price': np.random.uniform(50, 2000, 50),
    'Category': ['Electronics', 'Electronics', 'Electronics', 'Electronics', 'Accessories'] * 10,
    'Quarter': np.random.choice(['Q1', 'Q2', 'Q3', 'Q4'], 50),
    'Rating': np.random.uniform(3.0, 5.0, 50)
}

df = pd.DataFrame(data)
df['Revenue'] = df['Sales'] * df['Price']

# Round numeric columns for better readability
df['Price'] = df['Price'].round(2)
df['Rating'] = df['Rating'].round(1)
df['Revenue'] = df['Revenue'].round(2)

# Save to Excel
df.to_excel('/tmp/sample_data.xlsx', index=False)
print("Sample Excel file created at /tmp/sample_data.xlsx")
print(f"Data shape: {df.shape}")
print("\nFirst few rows:")
print(df.head())