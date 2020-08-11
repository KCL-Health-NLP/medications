# -*- coding: utf-8 -*-
"""
Created on Thu Nov  7 14:58:03 2019

@author: jchaturvedi
"""
from ehost_functions import load_mentions_with_attributes
import os
import sys
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError

def load_GATE_output(pin):
    """
    Create a mapping of all mentions to all their associated attributes.
    This is necessary due to the structure of eHOST XML documents in which
    these entities are stored in separate XML tags.
    """

    if (os.path.isfile(pin) == False):
        print(pin+' not found')
        return { key: {} }
    else:
        key = pin
    
    xml = ET.parse(pin)
    root = xml.getroot()
    ann_sets = root.findall('AnnotationSet')
    annotation_nodes = []
    for ann in ann_sets:
        if ('Name' in ann.attrib and ann.attrib['Name']=='Medication-work'):
            annotation_nodes = ann.findall('Annotation')

    # Collect annotations and related data to insert into mentions
    annotations = {}
    mentions = {}
    for annotation_node in annotation_nodes:
        annotation_id = annotation_node.attrib['Id']
        annotation_type = annotation_node.attrib['Type']
        start = annotation_node.attrib['StartNode']
        end = annotation_node.attrib['EndNode']
        if(annotation_type == 'Prescription'):
            annotations[annotation_id] = (annotation_type, start, end)
            mentions[annotation_id] = { 'class': annotation_type,
                                     'start': start,
                                     'end': end,
                                     }

    return { key: mentions }


path = 'T:/Jaya Chaturvedi/6. Medications app/annotations_backup/Idil/Schiziphrenia/batch_4/pat_10090783/'

doc = path+'corpus/1-572697314153178-2019-03-15.txt'
saved = path+'saved/1-572697314153178-2019-03-15.txt.knowtator.xml'
gatexml = 'C:/Users/jchaturvedi/Desktop/idil_gatexml2'

f = open(doc, "r")
text = f.read()

fh = open(doc,  "r")
text2 = ''
for line in fh:
    text2 = text2 + line.strip()+'\n'
fh.close()

annotations = load_mentions_with_attributes(saved, full_key=False)

for key in annotations:
    annotated_doc = annotations[key]
    for annotation in annotated_doc:
        start = int(annotated_doc[annotation]['start'])
        end = int(annotated_doc[annotation]['end'])   
        #print(text[start:end])

annotations_gate = load_GATE_output(gatexml)

for key in annotations_gate:
    annotated_doc = annotations_gate[key]
    for annotation in annotated_doc:
        start = int(annotated_doc[annotation]['start'])
        end = int(annotated_doc[annotation]['end'])   
        print(text2[start:end])