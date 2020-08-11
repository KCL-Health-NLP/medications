
"""
Created on Tue Jul 24 15:46:43 2018
@author: ABittar
"""

import os
import sys

#from ehost_functions import load_mentions_with_attributes, convert_file_annotations
from collections import Counter
from sklearn.metrics import cohen_kappa_score, precision_recall_fscore_support
import ntpath

import xml.etree.ElementTree as ET
import re

# specifies the attributes to evaluate
ATTRS = set([])
IGNORE_ATTRS = ['start', 'end', 'class', 'annotator', 'comment', 'text']


def create_expression(terms):
    expr = '|'.join(t for t in terms)
    return '('+expr+')'

## Time information in sentence ##
months = ['january','february','march','april','may','june','july','august','september','october','november','december']
months_short = ['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec']

def normalise_time(text):
    text = text.strip()
    text = text.lower()
    text = text.replace('sept','sep')
    text = text.replace('sepember','sep')
    timex_type = 'not_converted'
    timex = text
    p = re.compile('\d\d/\d\d/(\d\d)?\d\d')
    if(re.search(p,text)):
        #print(text, timex)
        return text
    p = re.compile('\d\d/\d/(\d\d)?\d\d')
    if(re.search(p,text)):
        timex_type = 'full_date'
        els = text.split('/')
        timex = els[0]+'/0'+els[1]+'/'+els[2]
        if(len(els[2])==2):
            timex = els[0]+'/0'+els[1]+'/20'+els[2]  
        #print(text, timex)
        return text
    p = re.compile('\d/\d\d/(\d\d)?\d\d')
    if(re.search(p,text)):
        timex_type = 'full_date'
        els = text.split('/')
        timex = '0'+els[0]+'/'+els[1]+'/'+els[2]
        if(len(els[2])==2):
            timex = els[0]+'/0'+els[1]+'/20'+els[2]  
        #print(text, timex)
        return text
    p = re.compile('\d/\d/(\d\d)?\d\d')
    if(re.search(p,text)):
        timex_type = 'full_date'
        els = text.split('/')
        timex = '0'+els[0]+'/0'+els[1]+'/'+els[2]
        if(len(els[2])==2):
            timex = els[0]+'/0'+els[1]+'/20'+els[2]  
        #print(text, timex)
        return text
    p = re.compile(create_expression(months_short)+ " (\d\d\d\d)")
    matches = re.findall(p,text)
    for m in matches:
        timex_type = 'month_short'
        m_short = m[0]
        text = text.replace(m_short, months[months_short.index(m_short)])
    #print(text, timex, timex_type)
    return text


def normalise_drug(name):#added JC
    name = name.strip()
    name = name.lower()
    #name = name.split(' ',1)[0]
    return name

def normalise_cessation(field):#added JC
    field = field.strip()
    field = field.replace('---','None')
    
def normalise_route(form):#added JC
    form = form.strip()
    form = form.lower()
    form = form.replace('oral tablets','oral')
    form = form.replace('oral (liquid)','oral liquid')
    form = form.replace('Oral (liquid)','oral liquid')
    form = form.replace('oral suspension','oral')
    form = form.replace('depot injection','depot')
    form = form.replace('nasal spray','inhaled')
    form = form.replace('inhaler','inhaled')
    form = form.replace('topical application','topical')
    form = form.replace('depot','injection')
    form = form.replace('IM injection','IM')

def normalise_when(when):#added JC
    when = when.strip()
    when = when.lower()
    when = when.replace('eveing','evening')
    when = when.replace('at night','night')
    when = when.replace('PRN','prn')
    
def normalise_dose_unit(unit):#added JC
    unit = unit.strip()
    unit = unit.lower()
    unit = unit.replace('microgram','mcg')
    unit = unit.replace('grams','gram')
    unit = unit.replace('gms','gm')
    unit = unit.replace('mgs','mg')
    unit = unit.replace('mcg','micrograms')

def normalise_dose_value(value):
    value = value.strip()
    value = value.lower()
    #value = value.split('.')[0]
    #formatNumber = lambda value: int(value) if not value%1 else value
    #value = formatNumber(int(float(value)))
    '''try:
        return int(value)
    except ValueError:
        try:
            return int(float(value))
        except:
            raise'''
    
def normalise_frequency(freq):#added JC
    freq = freq.strip()
    freq = freq.lower()
    #freq = freq.split('.')[0]
    
def normalise_interval(inter):#added JC
    inter = inter.strip()
    inter = inter.lower()
    #inter = inter.split('.')[0]
    
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
                if('_time' in attr and val!='unknown'):
                    val = normalise_time(val)
                if('drug' in attr):#added JC
                   val = normalise_drug(val)
                if('2_CESSATION' in attr and val == '---'):#added JC
                    val = normalise_cessation(val)
                if('route' in attr and val == 'depot' or val == 'IM' or val == 'oral tablets' or val == 'oral suspension' or val == 'oral (liquid)' or val == 'Oral (liquid)' or val == 'depot injection' or val == 'nasal spray' or val == 'inhaler' or val == 'topical application'):
                    val = normalise_route(val)#added JC
                if('when' in attr and val == 'eveing' or val == 'at night' or val == 'PRN'):#added JC
                    val = normalise_when(val)
                if('dose_unit' in attr and val == 'microgram' or val == 'grams' or val == 'gms' or val == 'mcg' or val == 'mgs'):#added JC
                    val = normalise_dose_unit(val)
                if('dose_value' in attr):#added JC
                    val = normalise_dose_value(val)
                if('frequency' in attr):#added JC
                    val = normalise_frequency(val)
                if('interval' in attr):#added JC
                    val = normalise_interval(val)
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

def read_corpus(pin):
    d_list = [os.path.join(pin, os.path.join(d, 'corpus')) for d in os.listdir(pin) if not '.' in d and 'pat' in d]
    all_files = []
    for d in d_list:
        f_list = [os.path.join(d,f) for f in os.listdir(d) if f.endswith('.txt')]
        for f in f_list:
            all_files.append(f)
    print('corpus files', len(all_files))
    return all_files

def get_saved_files(pin):
    d_list = [os.path.join(pin, os.path.join(d, 'saved')) for d in os.listdir(pin) if not '.' in d and 'pat' in d]
    all_files = []
    #print(d_list)
    for d in d_list:
        f_list = [os.path.join(d,f) for f in os.listdir(d) if f.endswith('knowtator.xml')]
        for f in f_list:
            all_files.append(f)
    print('saved files', len(all_files))
    return all_files  

def get_all_annotated_attributes(files1, files2):
    """
    Update the set of attributes to evaluate.
    """
    global ATTRS
    global IGNORE_ATTRS
    
    for f in files1:
        d = convert_file_annotations(load_mentions_with_attributes(f))
        flat_list = [item for sublist in d for item in sublist if item not in IGNORE_ATTRS]
        ATTRS = ATTRS.union(set(flat_list))
    
    for f in files2:
        d = convert_file_annotations(load_mentions_with_attributes(f))
        flat_list = [item for sublist in d for item in sublist if item not in IGNORE_ATTRS]
        ATTRS = ATTRS.union(set(flat_list))


def match_span(a1, a2, matching):
    s1 = int(a1['start'])
    s2 = int(a2['start'])
    e1 = int(a1['end'])
    e2 = int(a2['end'])
    t1 = a1['text']
    t2 = a2['text']

#    match_str = '{} {} {}\n        {} {} {}'.format(s1, e1, t1, s2, e2, t2)
    match_str = '{} {} {}\n{} {} {}'.format(s1, e1, t1, s2, e2, t2)
    
    # Exact match (strict matching)
    if s1 == s2 and e1 == e2:
#        match_str = 'match 1 ' + match_str
        return True, match_str
       
    if matching == 'relaxed':
        # s1_[ s2_< > ] (s1 INCLUDES s2)
        if s1 <= s2 and e1 >= e2:
            #match_str = 'match 2 ' + match_str
            return True, match_str

        # s2_< s1_[] > (s2 INCLUDES s1)
        if s1 >= s2 and e1 <= e2:
            #match_str = 'match 3 ' + match_str
            return True, match_str
    
        # s1_[ s2_<] > (s1 OVERLAP_BEFORE s2)
        if s1 <= s2 and e1 >= s2:
            #match_str = 'match 4 ' + match_str
            return True, match_str
        
        # s2_< s1_[> ] (s1 OVERLAP_AFTER s2)
        if s1 >= s2 and s1 <= e2:
            #match_str = 'match 5 ' + match_str
            return True, match_str
    
    #print('no', match_str)
    return False, ''


def match_attributes(tag1, tag2):
    attr_agr = {}
    
    attrs_to_check = [a for a in tag1.keys() if a not in ['start', 'end', 'text', 'comment', 'annotator']]
    
    #for a in attrs_to_check:
    #    attr_agr[a] = {'tp': 0, 'tn': 0, 'fp': 0, 'fn': 0}
    
    match_str = ''
    
    for attr in attrs_to_check:
        val1 = tag1.get(attr, None)
        val2 = tag2.get(attr, None)
        if val1 is not None and val2 is not None:
            if val1 == val2:
                scores = attr_agr.get(attr, {})
                tp = scores.get('tp', 0) + 1
                scores['tp'] = tp
                attr_agr[attr] = scores
            else:
                # this is fp and fn - weird
                scores = attr_agr.get(attr, {})
                fp = scores.get('fp', 0) + 1
                scores['fp'] = fp
                attr_agr[attr] = scores
                fn = scores.get('fn', 0) + 1
                scores['fn'] = fn
                attr_agr[attr] = scores
                match_str += '-- attribute disagreement on ' + attr + ': ' + str(val1) + ' vs. ' + str(val2) + '\n'
        elif val1 is None and val2 is None:#added JC
            if val1 == val2:
                scores = attr_agr.get(attr, {})
                tp = scores.get('tp', 0) + 1
                scores['tp'] = tp
                attr_agr[attr] = scores
            else:
                # this is fp and fn - weird
                scores = attr_agr.get(attr, {})
                fp = scores.get('fp', 0) + 1
                scores['fp'] = fp
                attr_agr[attr] = scores
                fn = scores.get('fn', 0) + 1
                scores['fn'] = fn
                attr_agr[attr] = scores
                match_str += '-- attribute disagreement on ' + attr + ': ' + str(val1) + ' vs. ' + str(val2) + '\n'
        elif val1 is None and val2 is not None:
            scores = attr_agr.get(attr, {})
            fp = scores.get('fp', 0) + 1
            scores['fp'] = fp
            attr_agr[attr] = scores
            match_str += '-- attribute disagreement on ' + attr + ': ' + str(val1) + ' vs. ' + str(val2) + '\n'
        elif val1 is not None and val2 is None:
            scores = attr_agr.get(attr, {})
            fn = scores.get('fn', 0) + 1
            scores['fn'] = fn
            attr_agr[attr] = scores
            match_str += '-- attribute disagreement on ' + attr + ': ' + str(val1) + ' vs. ' + str(val2) + '\n'
        else:
            scores = attr_agr.get(attr, {})
            tn = scores.get('tn', 0) + 1
            scores['tn'] = tn
            attr_agr[attr] = scores
            match_str += '-- attribute disagreement on ' + attr + ': ' + str(val1) + ' vs. ' + str(val2) + '\n'

    return attr_agr, match_str


def get_tag_attrs(tag):
    global ATTRS
    values = {}
    
    for attr in ATTRS:
        val = tag.get(attr, None)
        values[attr] = val
    
    return values


def count_agreements(pin1, pin2, report_string, matching):
    ann1 = load_mentions_with_attributes(pin1)
    ann2 = load_mentions_with_attributes(pin2)
    
    tags1 = convert_file_annotations(ann1)
    tags2 = convert_file_annotations(ann2)
    
    matched = []
    non_matched = []
    
    tp = fp = fn = 0
    
    attr_agr = {}
    attr_vals1 = []
    attr_vals2 = []
    
    report_string += '\n--------------------\n'
    report_string += 'MATCH\t'
    
    for tag1 in tags1:
        for tag2 in tags2:
            m, r = match_span(tag1, tag2, matching)
            if m:
                report_string += ntpath.basename(pin1) + '\t' + r + '\n'
                # span
                matched.append(tag1)
                matched.append(tag2)
                tp += 1
                # attributes
                a, r = match_attributes(tag1, tag2)
                report_string += r
                for attr in a:
                    curr_agr = attr_agr.get(attr, {})
                    new_agr = a[attr]
                    c = dict(Counter(curr_agr) + Counter(new_agr))
                    attr_agr[attr] = c
                # testing
                vals1 = get_tag_attrs(tag1)
                vals2 = get_tag_attrs(tag2)
                attr_vals1.append(vals1)
                attr_vals2.append(vals2)
                break

    for tag2 in tags2:
        if tag2 not in matched:
            for tag1 in tags1:
                if tag1 not in matched:
                    m, r = match_span(tag2, tag1, matching)
                    if m:
                        report_string += ntpath.basename(pin1) + '\t' + r + '\n'
                        # span
                        matched.append(tag1)
                        matched.append(tag2)
                        tp += 1
                        # attributes
                        a, r = match_attributes(tag1, tag2)
                        report_string += r
                        for attr in a:
                            curr_agr = attr_agr.get(attr, {})
                            new_agr = a[attr]
                            c = dict(Counter(curr_agr) + Counter(new_agr))
                            attr_agr[attr] = c
                        # testing
                        vals1 = get_tag_attrs(tag1)
                        vals2 = get_tag_attrs(tag2)
                        attr_vals1.append(vals1)
                        attr_vals2.append(vals2)
                        break

    report_string += '\n-------------------\n'
    report_string += 'FN\t'
    for tag1 in tags1:
        if tag1 not in matched:
            report_string += ntpath.basename(pin1) + '\t' +str(tag1['start']) + ' ' + str(tag1['end']) + ' ' + str(tag1['text']) + '\n'
            # span
            non_matched.append(tag1)
            fn += 1

    report_string += '\n--------------------\n'
    report_string += 'FP\t'
    for tag2 in tags2:
        if tag2 not in matched:
            report_string += ntpath.basename(pin1) + '\t' +str(tag2['start']) + ' ' + str(tag2['end']) + ' ' + str(tag2['text']) + '\n'
            non_matched.append(tag2)
            fp += 1
    
    report_string += '\n==========\n'

    return tp, fp, fn, attr_agr, attr_vals1, attr_vals2, report_string, matched, non_matched

def count_agreements_relaxed(pin1, pin2, report_string, matching):
    ann1 = load_mentions_with_attributes(pin1)
    ann2 = load_mentions_with_attributes(pin2)
    
    #TO ADD FILTERS TO THE ANNOTATIONS - NOT USED FOR PRESCRIPTIONS
    #ann1 = filter_annotations(ann1)
    #ann2 = filter_annotations(ann2)
    
    tags1 = convert_file_annotations(ann1)
    tags2 = convert_file_annotations(ann2)
    
    matched = []
    non_matched = []
    
    tp = fp = fn = 0
    
    attr_agr = {}
    attr_vals1 = []
    attr_vals2 = []
    
    report_string += '\n--------------------\n'
    report_string += 'MATCH\t'
    
    for tag1 in tags1:
        for tag2 in tags2:
            m, r = match_span(tag1, tag2, matching)
            if m:
                report_string += ntpath.basename(pin1) + '\t' + r + '\n'
                # span
                matched.append(tag1)
                matched.append(tag2)
                tp += 1
                # attributes
                a, r = match_attributes(tag1, tag2)
                report_string += r
                for attr in a:
                    curr_agr = attr_agr.get(attr, {})
                    new_agr = a[attr]
                    c = dict(Counter(curr_agr) + Counter(new_agr))
                    attr_agr[attr] = c
                # testing
                vals1 = get_tag_attrs(tag1)
                vals2 = get_tag_attrs(tag2)
                attr_vals1.append(vals1)
                attr_vals2.append(vals2)
                break

    for tag2 in tags2:
        if tag2 not in matched:
            for tag1 in tags1:
                if tag1 not in matched:
                    m, r = match_span(tag2, tag1, matching)
                    if m:
                        report_string += ntpath.basename(pin1) + '\t' + r + '\n'
                        # span
                        matched.append(tag1)
                        matched.append(tag2)
                        tp += 1
                        # attributes
                        a, r = match_attributes(tag1, tag2)
                        report_string += r
                        for attr in a:
                            curr_agr = attr_agr.get(attr, {})
                            new_agr = a[attr]
                            c = dict(Counter(curr_agr) + Counter(new_agr))
                            attr_agr[attr] = c
                        # testing
                        vals1 = get_tag_attrs(tag1)
                        vals2 = get_tag_attrs(tag2)
                        attr_vals1.append(vals1)
                        attr_vals2.append(vals2)
                        break

    report_string += '\n-------------------\n'
    report_string += 'FN\t'
    for tag1 in tags1:
        if tag1 not in matched:
            report_string += ntpath.basename(pin1) + '\t' +str(tag1['start']) + ' ' + str(tag1['end']) + ' ' + str(tag1['text']) + '\n'
            # span
            non_matched.append(tag1)
            fn += 1

    report_string += '\n--------------------\n'
    report_string += 'FP\t'
    for tag2 in tags2:
        if tag2 not in matched:
            report_string += ntpath.basename(pin1) + '\t' +str(tag2['start']) + ' ' + str(tag2['end']) + ' ' + str(tag2['text']) + '\n'
            non_matched.append(tag2)
            fp += 1
    
    report_string += '\n==========\n'

    return tp, fp, fn, attr_agr, attr_vals1, attr_vals2, report_string, matched, non_matched


def attr_prf(attr_agr_g, report_string):
    """
    Hand-coded calculations
    """
    # Using my metric - gives the same results as scikit-learn
    for attr in attr_agr_g:
        report_string += '-- ' + attr + '\n'
        tp = attr_agr_g[attr].get('tp', 0.0)
        fp = attr_agr_g[attr].get('fp', 0.0)
        #tn = attr_agr_g[attr].get('tn', 0.0)
        fn = attr_agr_g[attr].get('fn', 0.0)
        p, r, f = prf(tp, fp, fn)
        report_string += '\tprecision: ' + str(p) + '\n'
        report_string += '\trecall   : ' + str(r) + '\n'
        report_string += '\tf-score  : ' + str(f) + '\n'

    return report_string


def prf(tp, fp, fn):
    print('-- Calculating precision, recall and f-score')
    print('   tp:', tp)
    print('   fp:', fp)
    print('   fn:', fn)

    if tp + fp == 0.0 or tp + fn == 0.0:
        print('-- Warning: cannot calculate metrics with zero denominator')
        return 0.0, 0.0, 0.0

    if(tp>0):
        p = tp / (tp + fp)
        r = tp / (tp + fn)
        f = 2 * p * r / (p + r)
    else:
        p = 0
        r = 0
        f = 0
    
    return p, r, f


def batch_agreement(batch, ann1, ann2, files1, files2, report_dir=None, matching='relaxed', compare_attributes=True, ignore_attributes=[]):
    """
    ann_dir_1 and ann_dir_2 are tuples of the form:
        ('Annotator1_Name','Dir_1')
        ('Annotator2_Name','Dir_2')
    report_dir: specifies the output directory for the report file (overwrite existing report for the specified annotator pair)
    matching: specifies whether spans must be strict matches (strict) or partial matches (relaxed)
    compare_attributes: calculate agreement for span attributes (True/False)
    ignore_attributes: list of attributes to ignore
    """
    global ATTRS
    
    if matching not in ['strict', 'relaxed']:
        raise ValueError('-- Invalid matching type "' + str(matching) + '". Use "strict" or "relaxed".')
    
    if report_dir is not None and not os.path.isdir(report_dir):
        raise ValueError('-- Invalid report directory "' + str(matching) + '".')
    
    # Get all annotated attributes - need to do this here
    get_all_annotated_attributes(files1, files2)
    
    print(files1)
    #print('---')
    print(files2)
    
    if report_dir is not None:
        pout = os.path.join(report_dir, 'agreement_report_' + ann1 + '_' + ann2 + '_attr_'+str(batch)+'.txt')
        fout = open(pout, 'w', encoding='utf-8')
    
    report_string =  '================================\n'
    report_string += 'INTER-ANNOTATOR AGREEMENT REPORT\n'
    report_string += '================================\n'

    report_string += 'Batch: ' + batch + '\tAnnotators:' + ann1 + ',' + ann2 + '\n'
    report_string += 'Matching: ' + matching + '\n'
    report_string += '-------------------------\n'

    tp_g = fp_g = fn_g = 0.0
    
    attr_agr_g = {}
    attr_vals1_g = []
    attr_vals2_g = []
    
    matched_all = []
    non_matched_all = []
    
    filenames1 = [ntpath.basename(f1) for f1 in files1]
    filenames2 = [ntpath.basename(f2) for f2 in files2]
    
    print(set(filenames2)-set(filenames1))
    print(set(filenames1)-set(filenames2))
    
    for f1 in files1:
        for f2 in files2:
            # Only compare files that are in both sets
            f1b = os.path.basename(f1)
            f2b = os.path.basename(f2)
            if f1b == f2b:
                report_string += 'File1: ' + f1 + '\n'
                report_string += 'File2: ' + f2 + '\n'
                #tp, fp, fn, attr_agr, attr_vals1, attr_vals2, report_string, matched, non_matched = count_agreements(f1, f2, report_string, matching)
                tp, fp, fn, attr_agr, attr_vals1, attr_vals2, report_string, matched, non_matched = count_agreements_relaxed(f1, f2, report_string, matching)
                
                tp_g += tp
                fp_g += fp
                fn_g += fn
                for attr in attr_agr:
                    curr_agr = attr_agr_g.get(attr, {})
                    new_agr = attr_agr[attr]
                    c = dict(Counter(curr_agr) + Counter(new_agr))
                    attr_agr_g[attr] = c
                
                # Used for scikit-learn calculations
                attr_vals1_g.extend(attr_vals1)
                attr_vals2_g.extend(attr_vals2)
                
                matched_all.append([f1, matched])
                non_matched_all.append([f1, non_matched])

    assert len(attr_vals1_g) == len(attr_vals2_g)
    
    report_string += '\n'
    report_string += 'SPANS\n'
    report_string += '-----\n'

    p, r, f = prf(tp_g, fp_g, fn_g)
    
    report_string += 'tp: ' + str(tp_g) + '\n'
    report_string += 'fp: ' + str(fp_g) + '\n'
    report_string += 'fn: ' + str(fn_g) + '\n'
    report_string += 'precision: ' + str(p) + '\n'
    report_string += 'recall   : ' + str(r) + '\n'
    report_string += 'f-score  : ' + str(f) + '\n'

    # Using scikit-learn (per-class results)
    if compare_attributes:
        report_string += '\n'
        report_string += 'ATTRIBUTES\n'
        report_string += '----------\n'
        
        if len(ATTRS) == 0:
            report_string += '-- No attributes to compare\n'
        
        for attr in sorted(ATTRS):
            report_string += '-- ' + attr + '\n'
            sample1 = [k.get(attr, None) for k in attr_vals1_g]
            sample2 = [k.get(attr, None) for k in attr_vals2_g]
        
            scores = {}
            scores['macro'] = precision_recall_fscore_support(sample1, sample2, average='macro')
            scores['micro'] = precision_recall_fscore_support(sample1, sample2, average='micro')

            for score in scores:
                report_string += 'precision (' + score + '): ' + str(scores[score][0]) + '\n'
                report_string += 'recall    (' + score + '): ' + str(scores[score][1]) + '\n'
                report_string += 'f-score   (' + score + '): ' + str(scores[score][2]) + '\n'

            k = cohen_kappa_score(sample1, sample2)
            report_string += '\tkappa            : ' + str(k) + '\n'

    report_string = attr_prf(attr_agr_g, report_string)

    print(report_string)
    print('f-score  : ' + str(f) + '\n')

    if report_dir is not None:
        print('-- Printed report to file:', pout, file=sys.stderr)
        fout.write(report_string)
        fout.close()
        
    return matched_all, non_matched_all
'''
##not used for prescriptions##
def filter_annotations(all_annotations):
    for doc, anns in all_annotations.items():
        ann_copy = anns.copy()
        for ann_id, ann_values in ann_copy.items():
            #to remove annotations where the 'type' attribute is null
            if('type' not in ann_values):
                del anns[ann_id]
            else:
                #to remove some types of annotations
                if (ann_values['class'] == 'NO_ONSET_MENTIONED' or ann_values['type'] =='antypsychotic_drugs'):
                #if (ann_values['class'] == 'NO_ONSET_MENTIONED'):
                    del anns[ann_id]
    return all_annotations
'''
    
batch = 'batch_1'

annotator1 = 'Chloe'
#dir_1 = "T:/Natalia Viani/annotation_onset_mention/"+annotator1+"/first_ref_extended/"+batch
dir_1 = "T:/Natalia Viani/annotation_prescription/"+annotator1+"/Schizophrenia/Attachments_done/"+batch

annotator2 = 'GATE'
#dir_2 = "T:/Natalia Viani/annotation_onset_mention/"+annotator2+"/first_ref_extended/"+batch
dir_2 = "T:/Natalia Viani/annotation_prescription/"+annotator2+"/drug_annotation/Schizophrenia/"+batch

txt_files1 = read_corpus(dir_1)
txt_files2 = read_corpus(dir_2)

assert (len(txt_files1) == len(txt_files2))

saved_files1 = [f for f in get_saved_files(dir_1) if f.endswith('xml')]
saved_files2 = [f for f in get_saved_files(dir_2) if f.endswith('xml')]
filenames1 = [ntpath.basename(f).split('.')[0] for f in saved_files1]
filenames2 = [ntpath.basename(f).split('.')[0] for f in saved_files2]

for f1, f2 in zip(txt_files1, txt_files2):
    f = ntpath.basename(f1).split('.')[0]
    if f not in filenames1:
        print('Appending empty:' + f1.replace('corpus','saved')+'.knowtator.xml')
        saved_files1.append(f1.replace('corpus','saved')+'.knowtator.xml')
    if f not in filenames2:
        print('Appending empty:' + f2.replace('corpus','saved')+'.knowtator.xml')
        saved_files2.append(f2.replace('corpus','saved')+'.knowtator.xml')

#compute IAA and write file
matched_all, non_matched_all = batch_agreement(batch, annotator1, annotator2, saved_files1, saved_files2, report_dir='IAA', matching='relaxed', compare_attributes=False, ignore_attributes=IGNORE_ATTRS)

overlap_anns = [ann for ann in [match[1] for match in matched_all] if len(ann)>0]
flat_overlap_anns  = [item for sublist in overlap_anns for item in sublist]
merge_anns = [ann for ann in [match[1] for match in non_matched_all] if len(ann)>0]
flat_merge_anns  = [item for sublist in merge_anns for item in sublist]