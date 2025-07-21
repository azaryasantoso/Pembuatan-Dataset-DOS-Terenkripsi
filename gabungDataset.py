import os
import pandas as pd

folder = 'datasetResult'
merged_df = pd.DataFrame()

for file in os.listdir(folder):
    if file.startswith('Dataset_') and file.endswith('.csv'):
        file_path = os.path.join(folder, file)
        print(f"Membaca: {file}")

        try:
            df = pd.read_csv(file_path, on_bad_lines='warn')
        except Exception as e:
            print(f"Gagal membaca {file}: {e}")
            continue

        if df.columns.tolist() == df.iloc[0].tolist():
            df = df[1:]

        merged_df = pd.concat([merged_df, df], ignore_index=True)

output_path = os.path.join(folder, 'final_dataset.csv')
merged_df.to_csv(output_path, index=False)
print(f"Semua dataset berhasil digabung ke: {output_path}")
print(f"Jumlah total baris data: {len(merged_df)}")
