import pandas as pd

#  from intents_to_departments
df = pd.read_csv("intents_to_departments.csv")
print(df.iloc[:,1:4])

print("\n")

df2 = pd.read_csv("categories_to_departments.csv")
print(df2.iloc[:,1:4])
