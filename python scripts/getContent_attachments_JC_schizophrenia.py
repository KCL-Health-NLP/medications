# -*- coding: utf-8 -*-
"""
Created on Wed Jun 27 13:49:08 2018

@author: NViani

JC: extraction of patient documents for schizophrenia (F20x)
"""

import pandas as pd
import pyodbc
import pickle
import nltk
import random
import numpy as np

nltk.data.path.append(r'U:/software')



NLP_dev = 'S:/AchlysShared/BRC_NLP/All apps/Development/Jaya/'
project_schema_path = 'S:/AchlysShared/BRC_NLP/All apps/Development/Natalia/'+'annotation_projects/config_tasks/prescription_correction/'

def produceDocuments(df):
    import os
    import shutil
    outputDir=NLP_dev+"annotation_projects_setup/output_example_schizophrenia/"
 
    i = 0 #num_patients per batch
    j = 6 #num_batches (change to 6 if re-running for more batches)
    k = 1 #num_doc
    prev_brcid = "first"
    
    df=df.sort_values(by=['BrcId','ViewDate'])
    
    for t in df[['BrcId', 'CN_Doc_ID', 'Attachment_Text','ViewDate','Attachment_Text_html']].itertuples():
          
        brcidcol = str(t[1])
        docidcol = str(t[2])
        textcol = str(t[3])
        date = str(t[4])
        
        if(brcidcol!=prev_brcid):
            i +=1
            k = 1
        
        if i/11==1:
            j += 1
            i = 1
            
        batch = 'batch_'+str(j)
        patient = 'pat_'+brcidcol
        
        batch_directory = os.path.join(outputDir, batch)
        if not os.path.isdir(batch_directory):
            os.mkdir(batch_directory)
            
        pat_directory = os.path.join(batch_directory, patient)
        if not os.path.isdir(pat_directory):
            os.mkdir(pat_directory)
            
        corpusdirectory = os.path.join(pat_directory,  "corpus")
        if not os.path.isdir(corpusdirectory):
            os.mkdir(corpusdirectory)
            
        saveddirectory = os.path.join(pat_directory, "saved")
        if not os.path.isdir(saveddirectory):
            os.mkdir(saveddirectory)
            
        configdirectory = os.path.join(pat_directory, "config")
        if not os.path.isdir(configdirectory):
            os.mkdir(configdirectory)
        
        shutil.copy(project_schema_path+"projectschema.xml", configdirectory)        
        
        date_list = date.split(" ")
        fname = str(k)+"-"+docidcol+"-"+date_list[0]+".txt"
        print(j, i, fname)
        f = open(os.path.join(corpusdirectory, fname), "w")
        f.write(textcol)
        f.close() 
        prev_brcid = brcidcol
        k +=1
    return None



### read XLSX data ###
all_data = []


### First data extraction ###
conn = pyodbc.connect("Driver={SQL Server};"
                      "Server=brhnsql094;"
                      "Database=SQLCRIS;"
                      "Trusted_Connection=yes;")

sql = ("SELECT distinct top 1000 a.BrcId, a.CN_Doc_ID, a.Attachment_Text,a.ViewDate,a.Attachment_Text_html, b.Primary_Diag "+
"from sqlcris.dbo.Attachment a "+
"INNER JOIN SQLCRIS.dbo.Diagnosis b "+
"ON a.BrcId = b.BrcId "+
"WHERE b.Primary_Diag LIKE '%F20%' AND a.Attachment_Text <> '' " )

df = pd.read_sql(sql, conn, index_col=None, coerce_float=True, params=None, parse_dates=None, columns=None, chunksize=None)
df = df.loc[:,~df.columns.duplicated()]

conn.close()

### Computed text length ###
def get_char_length(text):
    if text is None:
        return 0
    return len(text)

def get_tokens_num(text):
    if text is None:
        return 0
    tokens = nltk.word_tokenize(text)
    return len(tokens)

df['attach_tokens_num'] = df['Attachment_Text'].apply(get_tokens_num)

df.to_pickle("./attachments_top_1000_schizophrenia.pkl")


#1) read first referrals pickle with docs, length, average line length, num_symptoms   
pickle_in = open("attachments_top_1000_schizophrenia.pkl","rb")
df_all = pickle.load(pickle_in)
df_all = df_all.drop_duplicates(subset='CN_Doc_ID', keep='first', inplace=False)

# example of filtering
df_red = df_all[df_all['attach_tokens_num']>=5]
print("All Attachments:", len(df_all))
print("Attachments with at least 5 tokens:", len(df_red))
df_red = df_all[df_all['attach_tokens_num']>=1000]
print("Attachments with at least 1000 tokens (50%):", len(df_red))


#2) #randomly select patients
random.seed(15)
available_patients = np.array(list(set(df_red["BrcId"].values)))
count = 50
selected_indexes = random.sample(range(0,len(available_patients)-1), count)
selected_patients = available_patients[selected_indexes]
df_selected = df_red[df_red["BrcId"].isin(selected_patients)]
print('patients',len(selected_patients), 'documents', len(df_selected))

#if you need mpre batches and don't want to include the ones already extracted:
#df_selected = df_red[~df_red["BrcId"].isin(selected_patients)]

#produceDocuments(df_selected)

pd.set_option('mode.chained_assignment', None)
df_red['Attachment_length'] = df_red['Attachment_Text'].apply(len)
print('average length of Attachment_Text:',df_red['Attachment_length'].mean())

#average length of text
df_len = (df_red.groupby('BrcId')['Attachment_Text'].apply(lambda x: np.mean(x.str.len())).reset_index(name='mean_len_text'))
print(df_len)
print("average lenght=", df_len['mean_len_text'].mean())

print("average tokens=", df_red["attach_tokens_num"].mean())