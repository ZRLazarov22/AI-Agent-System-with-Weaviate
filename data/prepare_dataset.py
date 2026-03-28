import pandas as pd

# Recipes
csv_path = 'recipes.csv'

columns_to_remove = ['Unnamed: 0', 'yield', 'cuisine_path', 'timing', 'img_src']

df = pd.read_csv(csv_path)

cleaned_df = df.drop(columns=[col for col in columns_to_remove if col in df.columns]).drop_duplicates().dropna()

cleaned_df.to_csv(csv_path, index=False)

print('Removed columns:', columns_to_remove)