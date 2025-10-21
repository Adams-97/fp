from reference import CsvTable


data = CsvTable(['age', 'region', 'sex', 'smoker'], 'expanded_life_table.csv')
values = {
    'region': 'North',
    'sex': ['M', 'F'],
    'age': 28,
    'smoker': True
}

val = data.lookup(values, 'q_x')
print(val)

# 28,0.0027597067582892,M,True,North