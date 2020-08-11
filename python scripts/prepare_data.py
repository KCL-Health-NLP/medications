# -*- coding: utf-8 -*-
"""
Created on Fri Feb 21 14:06:08 2020

@author: jchaturvedi

This is to get new start and stop spans for just drug name from ehost annotations in order to compare with output from medcat
"""
import pandas as pd
import re

NLP_drive = 'S:/AchlysShared/BRC_NLP/All apps/Development/Jaya/'
filename = NLP_drive+'annotation_projects_setup/output_annotations/prescriptions/Depression/adjudication/output_Chloe_batch1to5_new.txt'
ehost_anns = pd.read_csv(filename, header = None, sep = '\t', encoding = 'cp1252', names = ['batch','pat','doc','start','end','subject','drug','initiation','initiation_time','cessation','cessation_time','modality','dose_unit','dose_value','frequency','interval','route','when','undef1','undef2','span','undef3','annotator','comment']) 

ehost_anns = ehost_anns.drop(labels=['undef1','undef2','undef3'], axis = 1)
ehost_anns = ehost_anns.drop(labels=['initiation','initiation_time','cessation','cessation_time','modality','dose_unit','dose_value','frequency','interval','route','when'], axis = 1)


converted = []
new_starts = []
new_ends = []

for index, row in ehost_anns.iterrows():
    drug_name = row['drug']
    span = str(row['span'])
    start = row['start']
    end = row['end']
    new_start = start
    new_end = end
    found = 0
    if(str(drug_name)!='nan' and len(span)>0):
        m = re.search(drug_name, span, re.IGNORECASE)
        if(m):
            found=1
            new_start = start+m.start()
            new_end = new_start + len(m.group())                
    else:
        print(drug_name, span)
    new_starts.append(new_start)
    new_ends.append(new_end)  
    converted.append(found)
            
print(sum(converted))
print(len(ehost_anns))  
ehost_anns['converted']=converted
ehost_anns['new_start']=new_starts
ehost_anns['new_end']=new_ends

output_file = NLP_drive+'medcat_experiments/converted/medcat_input_depression.csv'
ehost_anns.to_csv(output_file)