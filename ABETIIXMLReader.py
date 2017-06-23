import tkinter
from tkinter import *
import tkinter.filedialog
from tkinter import filedialog
import os
import pandas as pd
import numpy as np
import xml.parsers.expat as etp
import xml.etree.ElementTree as et
import xml.etree.cElementTree as etd

curr_working_dir = os.getcwd()
qc_dir = curr_working_dir + "\\" + "Quality_Control_Rule"

def xml_cleanup_func(xml_string):
    node_start = "<"
    node_end = ">"
    xml_new_string = xml_string
    xml_new_string_length = len(xml_new_string)
    for a in range(0,xml_new_string_length):
        xml_string_temp = xml_new_string[a]
        xml_node_start = xml_string_temp.find(node_start)
        xml_node_end = xml_string_temp.find(node_end)
        if xml_node_start == -1:
            xml_new_string[a] = xml_string_temp
        if xml_node_start >= 0:
            xml_string_temp = xml_string_temp[:xml_node_start] + xml_string_temp[(xml_node_end + 1):]
            xml_node_start = xml_string_temp.find(node_start)
            xml_node_end = xml_string_temp.find(node_end)
            if xml_node_start == -1:
                xml_new_string[a] = xml_string_temp
            if xml_node_start >= 0:
                xml_string_temp = xml_string_temp[:xml_node_start] + xml_string_temp[(xml_node_end + 1):]
                xml_new_string[a] = xml_string_temp
    return xml_new_string

def removeNull(data):
    return ['NA' if a=='' else a for a in data]

#active_xml_path = filedialog.askopenfile()

active_xml_load =et.parse('TCNLAB1_Sys5PALAPP4M_Mouse dPAL 1 v3_214.xml')
active_xml_load_root = active_xml_load.getroot()
active_xml_load_session = active_xml_load_root[1]
active_xml_load_data = active_xml_load_root[2]

# Load Session Data#
active_xml_session_string = et.tostring(active_xml_load_session)
active_xml_session_string = bytes.decode(active_xml_session_string)
active_xml_session_string_listed = active_xml_session_string.splitlines()
active_xml_session_string_listed = [a.replace(" ", "") for a in active_xml_session_string_listed]
active_xml_session_string_listed = [a.replace("</Information>","") for a in active_xml_session_string_listed]
active_xml_session_string_listed = [a.replace("<Information>","") for a in active_xml_session_string_listed]
active_xml_session_string_listed = [a.replace("<SessionInformation>", "") for a in active_xml_session_string_listed]
active_xml_session_string_listed = [a.replace("</SessionInformation>", "") for a in active_xml_session_string_listed]
active_xml_session_string_listed = list(filter(None, active_xml_session_string_listed))
active_xml_session_string_cleaned = xml_cleanup_func(xml_string=active_xml_session_string_listed)
active_xml_session_column_titles = active_xml_session_string_cleaned[0::2]
active_xml_session_column_data = active_xml_session_string_cleaned[1::2]





# Load Data - General#
active_xml_data_string = et.tostring(active_xml_load_data)
active_xml_data_string = bytes.decode(active_xml_data_string)
active_xml_data_string_listed = active_xml_data_string.splitlines()
active_xml_data_string_listed = [a.replace('<MarkerData>', "") for a in active_xml_data_string_listed]
active_xml_data_string_listed = [a.replace('</MarkerData>', "") for a in active_xml_data_string_listed]
active_xml_data_string_listed = [a.replace('<Marker>', "") for a in active_xml_data_string_listed]
active_xml_data_string_listed = [a.replace('</Marker>', "") for a in active_xml_data_string_listed]
active_xml_data_string_listed = [a.replace(" ","") for a in active_xml_data_string_listed]
active_xml_data_string_listed = list(filter(None, active_xml_data_string_listed))
active_data_types = [a for a in active_xml_data_string_listed if "<SourceType>" in a]
active_data_types = [a.replace("<SourceType>", "") for a in active_data_types]
active_data_types = [a.replace("</SourceType>", "") for a in active_data_types]
active_data_types = [a.replace(" ", "") for a in active_data_types]
active_data_types = list(set(active_data_types))
active_data_evaluation_index = list()
active_data_measure_index = list()
active_data_count_index = list()


# Process Evaluation Data if Found #
if any("Evaluation" in a for a in active_data_types):
    for a in range(0,len(active_xml_data_string_listed)):
        if "Evaluation" in active_xml_data_string_listed[a]:
            active_data_evaluation_index.append(a)
        else:
            active_data_evaluation_index = active_data_evaluation_index
    final_evaluation_column = max(active_data_evaluation_index) + 1
    first_evaluation_column = min(active_data_evaluation_index) - 1
    active_xml_data_evaluation = active_xml_data_string_listed[first_evaluation_column:(final_evaluation_column + 1)]
    active_xml_data_evaluation = [a.replace("<SourceType>Evaluation</SourceType>", "") for a in active_xml_data_evaluation]
    active_xml_data_evaluation = list(filter(None, active_xml_data_evaluation))
    active_xml_data_name_index = list()
    for a in range(0,len(active_xml_data_evaluation)):
        if "<Name>" in active_xml_data_evaluation[a]:
            active_xml_data_name_index.append(a)
        else:
            active_xml_data_name_index = active_xml_data_name_index
    for a in range(0,len(active_xml_data_name_index)):
        current_index = active_xml_data_name_index[a]
        if current_index != max(active_xml_data_name_index):
            following_index = active_xml_data_name_index[(a + 1)]
            if following_index - current_index == 1:
                active_xml_data_evaluation.insert(following_index, "NA")
                active_xml_data_name_index[(a+1):] = [b+1 for b in active_xml_data_name_index[(a+1):]]
            else:
                active_xml_data_name_index = active_xml_data_name_index
        else:
            active_xml_data_name_index = active_xml_data_name_index


    active_xml_data_evaluation = [a.replace("<Name>", "") for a in
                                  active_xml_data_evaluation]
    active_xml_data_evaluation = [a.replace("</Name>", "") for a in
                                  active_xml_data_evaluation]
    active_xml_data_evaluation = [a.replace("<Results>", "") for a in
                                  active_xml_data_evaluation]
    active_xml_data_evaluation = [a.replace("</Results>", "") for a in
                                  active_xml_data_evaluation]
    active_xml_data_evaluation_column_titles = active_xml_data_evaluation[0::2]
    active_xml_data_evaluation_column_data = active_xml_data_evaluation[1::2]
    for a in range(0,len(active_xml_data_evaluation_column_data)):
        if active_xml_data_evaluation_column_data[a] != 'NA':
            active_xml_data_evaluation_column_data[a] = float(active_xml_data_evaluation_column_data[a])

# Process Measure Data if Found #
if any("Measure" in a for a in active_data_types):
    for a in range(0,len(active_xml_data_string_listed)):
        if "Measure" in active_xml_data_string_listed[a]:
            active_data_measure_index.append(a)
        else:
            active_data_measure_index = active_data_measure_index
    first_measure_column = min(active_data_measure_index) - 1
    final_measure_column = max(active_data_measure_index) + 2
    active_xml_data_measure = active_xml_data_string_listed[first_measure_column:(final_measure_column + 1)]
    active_xml_data_measure = [a.replace("<SourceType>Measure</SourceType>","") for a in active_xml_data_measure]
    active_xml_data_measure = list(filter(None, active_xml_data_measure))
    active_xml_data_measure_duration = list()
    active_xml_data_measure_start = list()
    active_xml_data_measure_dur_index = list()
    active_xml_data_measure_start_index = list()
    for a in range(0,len(active_xml_data_measure)):
        if ("<Name>" in active_xml_data_measure[a]) or ("<Time>" in active_xml_data_measure[a]):
            active_xml_data_measure_start.append(active_xml_data_measure[a])
        if ("<Name>" in active_xml_data_measure[a]) or ("<Duration>" in active_xml_data_measure[a]):
            active_xml_data_measure_duration.append(active_xml_data_measure[a])

    active_xml_data_measure_duration = [a.replace("<Name>","") for a in active_xml_data_measure_duration]
    active_xml_data_measure_duration = [a.replace("</Name>", "") for a in active_xml_data_measure_duration]
    active_xml_data_measure_duration = [a.replace("<Duration>","") for a in active_xml_data_measure_duration]
    active_xml_data_measure_duration = [a.replace("</Duration>", "") for a in active_xml_data_measure_duration]
    active_xml_data_measure_duration_column_titles = active_xml_data_measure_duration[0::2]
    active_xml_data_measure_duration_column_data = active_xml_data_measure_duration[1::2]
    for a in range(0,len(active_xml_data_measure_duration_column_data)):
        if active_xml_data_measure_duration_column_data != 'NA':
            active_xml_data_measure_duration_column_data[a] = float(active_xml_data_measure_duration_column_data[a]) / 1000000

# Process Data into Dataframe #
active_xml_dataframe_titles = active_xml_session_column_titles + active_xml_data_evaluation_column_titles + active_xml_data_measure_duration_column_titles
active_xml_dataframe_rowdata = active_xml_session_column_data + active_xml_data_evaluation_column_data + active_xml_data_measure_duration_column_data

active_xml_dataframe = pd.DataFrame(data=[active_xml_dataframe_rowdata], columns=active_xml_dataframe_titles)
active_xml_qc_pass =
print(active_xml_dataframe)








