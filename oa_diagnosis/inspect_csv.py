
import pandas as pd
try:
    df = pd.read_csv(r'c:\Users\pahad\Desktop\AutoGen\data\Clinical_FNIH_merged_all_tables.csv')
    with open('columns.txt', 'w') as f:
        f.write("Columns:\n")
        for col in df.columns:
            f.write(f"{col}\n")
        f.write("\nFirst row:\n")
        for k, v in df.iloc[0].to_dict().items():
            f.write(f"{k}: {v}\n")
except Exception as e:
    with open('columns.txt', 'w') as f:
        f.write(str(e))
