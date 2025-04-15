import pandas as pd

#  from intents_to_departments
df = pd.read_csv("intents_to_departments.csv")
print(df.iloc[:,0:2])

print("\n")

df2 = pd.read_csv("categories_to_departments.csv")
print(df2.iloc[:,0:2])
