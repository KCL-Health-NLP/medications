# -*- coding: utf-8 -*-
"""
Created on Thu Jul 11 11:11:38 2019

@author: NViani
"""
import os
import sys
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError

def load_mentions_with_attributes(pin, full_key=True):
    """
    Create a mapping of all mentions to all their associated attributes.
    This is necessary due to the structure of eHOST XML documents in which
    these entities are stored in separate XML tags.
    """
    if full_key:
        key = pin
    else:
        key = os.path.basename(pin)
        
    if (os.path.isfile(pin) == False):
        #print(pin+' not found')
        return { key: {} }
    
    xml = ET.parse(pin)
    annotation_nodes = xml.findall('annotation')
    attribute_nodes = xml.findall('.//stringSlotMention')
    mention_nodes = xml.findall('.//classMention')

    # Collect annotations and related data to insert into mentions
    annotations = {}
    for annotation_node in annotation_nodes:
        annotation_id = annotation_node.find('mention').attrib['id']
        annotator = annotation_node.find('annotator').text
        start = annotation_node.find('span').attrib['start']
        end = annotation_node.find('span').attrib['end']
        
        comment_node = annotation_node.find('annotationComment')
        comment = None
        if comment_node is not None:
            comment = comment_node.text
        
        annotations[annotation_id] = (annotator, start, end, comment)
    
    # Collect attributes and values to insert into mentions
    attributes = {}
    for attribute_node in attribute_nodes:
        attribute_id = attribute_node.attrib['id']
        attribute_name = attribute_node[0].attrib['id']
        attribute_value = attribute_node[1].attrib['value']
        attributes[attribute_id] = (attribute_name, attribute_value)
    
    # Collect mention classes so we can link them to the appropriate comment
    mentions = {}
    for mention_node in mention_nodes:
        mention_id = mention_node.attrib['id']
        mention_class_node = mention_node.findall('.//mentionClass')
        if len(mention_class_node) > 0:
            mention_class = mention_class_node[0].attrib['id']
            mention_text = mention_class_node[0].text
            annotator, start, end, comment = annotations.get(mention_id, None)
            mentions[mention_id] = { 'class': mention_class,
                                     'text' : mention_text,
                                     'annotator': annotator,
                                     'start': start,
                                     'end': end,
                                     'comment': comment
                                     }

        # Retrieve ids of attribute nodes
        slot_nodes = mention_node.findall('.//hasSlotMention')
        for slot_node in slot_nodes:
            temp = mentions.get(mention_id, None)
            if temp is not None:
                slot_id = slot_node.attrib['id']
                attr, val = attributes.get(slot_id)
                temp[attr] = val
                mentions[mention_id] = temp
    
    return { key: mentions }


def convert_file_annotations(file_annotations):
    """
    Convert the multi-level dictionary format returned
    by load_mentions_with_attributes() into a flatter structure.
    """
    all_annotations = []
    for file_key in file_annotations:
        annotations = file_annotations[file_key]
        for annotation_id in annotations:
            annotation = annotations[annotation_id]
            all_annotations.append(annotation)
    return all_annotations

def count_mentions(pin):
    """
    Count all mention-level annotations in a document.
    """
    mention_counts = {}
    xml = None
    
    try:
        xml = ET.parse(pin)
    except ParseError as e:
        print('-- Error: unable to parse document ' + pin, file=sys.stderr)
        print(e, file=sys.stderr)
        return mention_counts
        
    mention_nodes = xml.findall('.//classMention')
    
    for mention_node in mention_nodes:
        mention_class = mention_node[0].attrib['id']
        n = mention_counts.get(mention_class, 0) + 1
        mention_counts[mention_class] = n
    
    return mention_counts
