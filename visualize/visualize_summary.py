import pandas as pd
import matplotlib.pyplot as plt

# Load data
df = pd.read_csv('../exported_data/monthly_summary.csv')

# Group by merchant and sum total amounts
merchant_summary = df.groupby('merchant')['total_amount_inr'].sum().sort_values(ascending=False)

# Plot bar chart
plt.figure(figsize=(10, 6))
merchant_summary.plot(kind='bar', color='skyblue')
plt.title('Total Transaction Amount by Merchant')
plt.xlabel('Merchant')
plt.ylabel('Total Amount (INR)')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()
