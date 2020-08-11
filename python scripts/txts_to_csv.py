# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import csv
import os
import pandas as pd
from pathlib import Path
from collections import defaultdict

cohort = 'stress_anxiety'
my_dir_path = 'S:/AchlysShared/BRC_CRIS/Jaya Chaturvedi/6. Medications app/medcat/to_run_on_medcat/'+cohort+'/'
output = 'S:/AchlysShared/BRC_CRIS/Jaya Chaturvedi/6. Medications app/medcat/to_run_on_medcat/output_file_stress_anxiety.csv'
output_excel = 'S:/AchlysShared/BRC_CRIS/Jaya Chaturvedi/6. Medications app/medcat/to_run_on_medcat/output_file_stress_anxiety.xlsx'

'''
results = defaultdict(list)

for file in Path(my_dir_path).iterdir():
    with open(file,"r") as file_open:
        for name in file.name:
            results["name"] = file.name
            results["text"].append(file_open.read())


df = pd.DataFrame(results)

df.head()

df.to_csv('S:/AchlysShared/BRC_CRIS/Jaya Chaturvedi/6. Medications app/medcat/to_run_on_medcat/stress_anxiety.csv')

df.to_excel('S:/AchlysShared/BRC_CRIS/Jaya Chaturvedi/6. Medications app/medcat/to_run_on_medcat/stress_anxiety.xlsx')

'''



with open(output, 'w') as outfile:
    csvout = csv.writer(outfile)
    csvout.writerow(['name', 'text'])

    files = os.listdir(my_dir_path)

    for filename in files:
        with open(my_dir_path + '/' + filename) as afile:
            csvout.writerow([filename, afile.read()])
            afile.close()

    outfile.close()

df = pd.read_csv(output, encoding='cp1252')

df.head()

df.to_excel(output_excel, encoding='utf-8', index=False)

df2 = pd.read_excel(output_excel)

df2.head()

#to check encoding of csv file
with open(output_excel) as f:
   print(f)