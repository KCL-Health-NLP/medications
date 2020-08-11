# -*- coding: utf-8 -*-
"""
Created on Tue Aug  7 16:20:44 2018
@author: ABittar
"""

import os
from ehost_functions import load_mentions_with_attributes

def batch_process_directory(pin, full_key=True):
    """
    Get all annotations from the corpus and store a mapping of file names to 
    annotations.
    """
    global_annotations = {}
    
    d_list = [os.path.join(pin, os.path.join(d, 'saved')) for d in os.listdir(pin) if 'config' not in d and 'annotationadmin' not in d and '.' not in d]

    for d in d_list:
        f_list = [os.path.join(d,f) for f in os.listdir(d) if f.endswith('knowtator.xml')]
    
        for f in f_list:
            curr_annotations = load_mentions_with_attributes(f, full_key=full_key)
            global_annotations.update(curr_annotations)
   
    return global_annotations

def get_value(dic, key):
    if (key in dic):
        return dic[key]
    else:
        return "null"

def get_value2(dic, key):
    if (key in dic):
        return dic[key]
    else:
        return "null"


#### MANUAL ANNOTATIONS #####
#annotator = 'Jack'
#dir_1 = "T:/Natalia Viani/annotation_onset_mention/"+annotator+"/first_ref_extended/"
#batches = list(range(1,21))
#batches = [str(b) for b in batches]

#annotator = 'RS'
#dir_1 = "T:/Natalia Viani/annotation_onset_mention/"+annotator+"/first_referrals/"
#batches=['1']

annotator = 'GATE'
dir_1 = "T:/Natalia Viani/annotation_prescription/"+annotator+"/drug_annotation/Schizophrenia\\"
batches = list(range(1,6))
batches = [str(b) for b in batches]

write_file = True
if(write_file):
    #text_file = open("./first_referrals_extended_onset/output_"+annotator+".txt", "w")
    #text_file = open("./first_referrals_0diff/output_"+annotator+".txt", "w")  
    text_file = open("./prescriptions/Schizophrenia/output_"+annotator+"_drug_anno_batch1to5"+".txt", "w")
    
for batch in batches:
    if(os.path.isdir(dir_1+'batch_'+batch)):
        
        #read corpus file
        pin = dir_1+'batch_'+batch
        d_list = [os.path.join(pin, os.path.join(d, 'corpus')) for d in os.listdir(pin) if 'config' not in d and 'annotationadmin' not in d and '.' not in d]
        all_files = []
        for d in d_list:
            f_list = [os.path.join(d,f) for f in os.listdir(d) if f.endswith('.txt')]
            for f in f_list:
                all_files.append(f.split("\\")[-3]+"\\"+f.split("\\")[-1].split(".")[0])
            
        annotations = batch_process_directory(pin, full_key=True)
        #annotations = batch_process_directory(dir_1+'set_0_diff_batch'+batch, full_key=True)
        saved_files = []
        for path, annotationList in annotations.items():
            docPath = path.split('/')[5]
            batch = docPath.split('\\')[1]
            pat = docPath.split('\\')[2]
            docName = docPath.split('\\')[4].split('.')[0]
            if(write_file):
                for key, value in annotationList.items():
                    line = batch+"\t"+pat+"\t"+docName+"\t"+value['start']+"\t"+value['end']+"\t"+get_value2(value, 'Subject')+"\t"+get_value2(value, 'drug')+"\t"+get_value2(value, '1_INITIATION')+"\t"+get_value2(value, '1_INITIATION_time')+"\t"+get_value2(value, '2_CESSATION')+"\t"+get_value2(value, '2_CESSATION_time')+"\t"+get_value(value, 'Modality')+"\t"+get_value(value, 'dose_unit')+"\t"+get_value(value, 'dose_value')+"\t"+get_value(value, 'frequency')+"\t"+get_value(value,'interval')+"\t"+get_value(value,'route')+"\t"+get_value(value,'when')+"\t"+get_value(value,'type')+"\t"+value['text']+"\t"+get_value(value,'value')
                    if(value['comment'] is not None):
                        line = line+"\t"+value['comment']
                    text_file.write(line+"\n")
                    saved_files.append(pat+"\\"+docName)
        
        saved_files = list(dict.fromkeys(saved_files))
        missing = [s for s in all_files if s not in saved_files]
        print(batch, missing)
  
if(write_file):           
    text_file.close()
 
    
'''
###SUTIME OUTPUT###
annotator = 'SUTime'
dir_1 = "S:/All apps/Development/Natalia/annotation_projects/first_referrals_2018/extraction_1_no_overlap_extended/"
batches = list(range(1,21))
batches = [str(b) for b in batches]

#annotator = 'SUTime'
#dir_1 = "S:/All apps/Development/Natalia/annotation_projects/early_services/set_0_diff/"
#batches=['RP','RS']

write_file_SUTime = True
if(write_file_SUTime):
    text_file = open("./first_referrals_extended_onset/output_"+annotator+".txt", "w")
    #text_file = open("./early_services_0diff/output_"+annotator+".txt", "w")

    for batch in batches:
        annotations = batch_process_directory(dir_1+'batch_'+batch+"_preannotated", full_key=True)
        for path, annotationList in annotations.items():
            docPath = path.split('/')[6]
            batch = path.split('/')[7]
            pat = batch.split('\\')[1]
            docName = batch.split('\\')[3].split('.')[0]
            for key, value in annotationList.items():
                ann_class = value['class']
                if(ann_class=="UNDEF"):
                    line = ''
                    text = value['text']
                    text = text.replace("\n"," ")
                    line = batch.split('\\')[0]+"\t"+pat+"\t"+docName+"\t"+value['start']+"\t"+value['end']+"\t"+text+"\t"+get_value(value, 'value')
                    if(value['comment'] is not None):
                        line = line+"\t"+value['comment']
                    text_file.write(line+"\n")
                    
    text_file.close()
'''