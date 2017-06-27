import tkinter
from tkinter import *
import tkinter.filedialog
from tkinter import filedialog
import os
import pandas as pd
import numpy as np
import collections
import xml.parsers.expat as etp
import xml.etree.ElementTree as et
import xml.etree.cElementTree as etd
import time
import datetime

curr_working_dir = os.getcwd()
qc_dir = curr_working_dir + "\\" + "Quality_Control_Rule"
sys.path.insert(0,qc_dir)
qc_list = list()
for file in os.listdir(qc_dir):
    qc_list.append(file)
qc_list = [a.replace(".py", "") for a in qc_list]

experiment_directory_list = list()
#experiment_directory_list.append('C:\\Users\\dpalmer\\PycharmProjects\\ABETIIXML')
experiment_directory_list.append('C:\\TestPAL')
for exp_directory in range(0,len(experiment_directory_list)):
    exp_dir = experiment_directory_list[exp_directory]
    exp_path_list = exp_dir.split("\\")
    exp_folder_name = exp_path_list[(len(exp_path_list) - 1)]
    config_file_location = exp_dir + "\\" + "id_config.csv"
    error_file_location = exp_dir + "\\" + "error_report.csv"
    analyed_file_location = exp_dir + "\\" + "analyzed_xml.csv"
    bad_filepath = exp_dir + "\\" + "BadXML"
    if not os.path.exists(bad_filepath):
        os.makedirs(bad_filepath)
    if os.path.isfile(config_file_location) != True:
        config_file = open(config_file_location, 'w')
        config_file.write('[QC Analysis]')
        config_file.write("\n")
        config_file.write('QC = ')
        config_file.write("\n")
        config_file.write("\n")
        config_file.write('[Animal ID List]')
        config_file.write("\n")
        config_file.write("ID,DOB,Factor1,Factor2,Aliases")
        config_file.write('\n')
        config_file.write('\n')
        config_file.write('\n')
        config_file.write('END_LIST')
        config_file.write('\n')
        config_file.write('\n')
        config_file.write('[Example]')
        config_file.write('\n')
        config_file.write("In the cell beside 'QC = ' add the appropriate Quality Control File")
        config_file.write('\n')
        config_file.write(
            "Your Animal ID List must contain at least (ID,Aliases, & DOB). You can add as many IV following as desired.")
        config_file.write('\n')
        config_file.write(
            "ID: The exact mouse ID you want reported. Aliases: Any mistyping or alternate names the same animal may go by. Must be at the end of your data. Can use as many columns as needed. Include main ID always!!! DOB: Birthdate of animal in the following format dd/mm/yyyy")
        config_file.write('\n')
        config_file.write(
            "Your last ID information should be in the row before END. You may add as many rows as needed")
        config_file.write('\n')
        config_file.write('Example:')
        config_file.write('\n')
        config_file.write('ID,DOB,Sex,Genotype,Strain, Aliases')
        config_file.write('\n')
        config_file.write('gt01x01,01/01/2015,Female,WT,3xTG,gt01x1,gt1x01,gtt01x01')
        config_file.close()
    if os.path.isfile(analyed_file_location) != True:
        analyzed_file = open(analyed_file_location, 'w')
        analyzed_file.write("File List")
        analyzed_file.write("\n")
        analyzed_file.close()
    if os.path.isfile(error_file_location) != True:
        error_file = open(error_file_location, 'w')
        error_file.write('Date,FileName,Error')
        error_file.write("\n")
        error_file.close()
        message = "The program will terminate. Please edit the config file and restart."
        print(message)
        sys.exit()
    config_file = open(config_file_location, 'r')
    config_file_details = config_file.readlines()
    config_file.close()
    config_file_details = [items.strip("\n") for items in config_file_details]
    qc_file_row = list()
    qc_file = str()

    qc_file_row = config_file_details[1]
    qc_file_row = qc_file_row.split(",")
    qc_file_row = list(filter(None, qc_file_row))
    qc_file = qc_file_row[1]
    import_string = "import %s" % (qc_file)
    exec(import_string)

    create_string = "%s.Create_Data(exp_dir=exp_dir)" % (qc_file)
    exec(create_string)

    analyzed_file = open(analyed_file_location, "r")
    analyzed_file_list = analyzed_file.readlines()
    analyzed_file_list = analyzed_file_list[1:]
    xml_file_list = list()
    for file in os.listdir(exp_dir):
        if file.endswith(".xml"):
            xml_file_list.append(file)

    new_xml_file_list = list(set(analyzed_file_list)^set(xml_file_list))

    def xml_cleanup_func(xml_string):
        node_start = "<"
        node_end = ">"
        xml_new_string = xml_string
        xml_new_string_length = len(xml_new_string)
        for a in range(0, xml_new_string_length):
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
        return ['NA' if a == '' else a for a in data]


    # active_xml_path = filedialog.askopenfile()
    active_day_results = str()
    for x in range(0, len(new_xml_file_list)):
        current_xml = new_xml_file_list[x]
        active_xml_load = et.parse('TCNLAB1_Sys5PALAPP4M_Mouse dPAL 1 v3_214.xml')
        active_xml_load_root = active_xml_load.getroot()
        active_xml_load_session = active_xml_load_root[1]
        active_xml_load_data = active_xml_load_root[2]

        # Load Session Data#
        active_xml_session_string = et.tostring(active_xml_load_session)
        active_xml_session_string = bytes.decode(active_xml_session_string)
        active_xml_session_string_listed = active_xml_session_string.splitlines()
        active_xml_session_string_listed = [a.replace(" ", "") for a in active_xml_session_string_listed]
        active_xml_session_string_listed = [a.replace("</Information>", "") for a in active_xml_session_string_listed]
        active_xml_session_string_listed = [a.replace("<Information>", "") for a in active_xml_session_string_listed]
        active_xml_session_string_listed = [a.replace("<SessionInformation>", "") for a in
                                            active_xml_session_string_listed]
        active_xml_session_string_listed = [a.replace("</SessionInformation>", "") for a in
                                            active_xml_session_string_listed]
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
        active_xml_data_string_listed = [a.replace(" ", "") for a in active_xml_data_string_listed]
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
            for a in range(0, len(active_xml_data_string_listed)):
                if "Evaluation" in active_xml_data_string_listed[a]:
                    active_data_evaluation_index.append(a)
                else:
                    active_data_evaluation_index = active_data_evaluation_index
            final_evaluation_column = max(active_data_evaluation_index) + 1
            first_evaluation_column = min(active_data_evaluation_index) - 1
            active_xml_data_evaluation = active_xml_data_string_listed[
                                         first_evaluation_column:(final_evaluation_column + 1)]
            active_xml_data_evaluation = [a.replace("<SourceType>Evaluation</SourceType>", "") for a in
                                          active_xml_data_evaluation]
            active_xml_data_evaluation = list(filter(None, active_xml_data_evaluation))
            active_xml_data_name_index = list()
            for a in range(0, len(active_xml_data_evaluation)):
                if "<Name>" in active_xml_data_evaluation[a]:
                    active_xml_data_name_index.append(a)
                else:
                    active_xml_data_name_index = active_xml_data_name_index
            for a in range(0, len(active_xml_data_name_index)):
                current_index = active_xml_data_name_index[a]
                if current_index != max(active_xml_data_name_index):
                    following_index = active_xml_data_name_index[(a + 1)]
                    if following_index - current_index == 1:
                        active_xml_data_evaluation.insert(following_index, "NA")
                        active_xml_data_name_index[(a + 1):] = [b + 1 for b in active_xml_data_name_index[(a + 1):]]
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
            for a in range(0, len(active_xml_data_evaluation_column_data)):
                if active_xml_data_evaluation_column_data[a] != 'NA':
                    active_xml_data_evaluation_column_data[a] = float(active_xml_data_evaluation_column_data[a])

        # Process Measure Data if Found #
        if any("Measure" in a for a in active_data_types):
            for a in range(0, len(active_xml_data_string_listed)):
                if "Measure" in active_xml_data_string_listed[a]:
                    active_data_measure_index.append(a)
                else:
                    active_data_measure_index = active_data_measure_index
            first_measure_column = min(active_data_measure_index) - 1
            final_measure_column = max(active_data_measure_index) + 2
            active_xml_data_measure = active_xml_data_string_listed[first_measure_column:(final_measure_column + 1)]
            active_xml_data_measure = [a.replace("<SourceType>Measure</SourceType>", "") for a in
                                       active_xml_data_measure]
            active_xml_data_measure = list(filter(None, active_xml_data_measure))
            active_xml_data_measure_duration = list()
            active_xml_data_measure_start = list()
            active_xml_data_measure_dur_index = list()
            active_xml_data_measure_start_index = list()
            for a in range(0, len(active_xml_data_measure)):
                if ("<Name>" in active_xml_data_measure[a]) or ("<Time>" in active_xml_data_measure[a]):
                    active_xml_data_measure_start.append(active_xml_data_measure[a])
                if ("<Name>" in active_xml_data_measure[a]) or ("<Duration>" in active_xml_data_measure[a]):
                    active_xml_data_measure_duration.append(active_xml_data_measure[a])

            active_xml_data_measure_duration = [a.replace("<Name>", "") for a in active_xml_data_measure_duration]
            active_xml_data_measure_duration = [a.replace("</Name>", "") for a in active_xml_data_measure_duration]
            active_xml_data_measure_duration = [a.replace("<Duration>", "") for a in active_xml_data_measure_duration]
            active_xml_data_measure_duration = [a.replace("</Duration>", "") for a in active_xml_data_measure_duration]
            active_xml_data_measure_duration_column_titles = active_xml_data_measure_duration[0::2]
            active_xml_data_measure_duration_column_data = active_xml_data_measure_duration[1::2]
            for a in range(0, len(active_xml_data_measure_duration_column_data)):
                if active_xml_data_measure_duration_column_data != 'NA':
                    active_xml_data_measure_duration_column_data[a] = float(
                        active_xml_data_measure_duration_column_data[a]) / 1000000

        # Process Data into Dataframe #
        active_xml_dataframe_titles = active_xml_session_column_titles + active_xml_data_evaluation_column_titles + active_xml_data_measure_duration_column_titles
        active_xml_dataframe_titles_dict = dict()
        for a in range(0, len(active_xml_dataframe_titles)):
            if active_xml_dataframe_titles[a] in active_xml_dataframe_titles_dict:
                active_xml_dataframe_titles_dict[active_xml_dataframe_titles[a]] += 1
            else:
                active_xml_dataframe_titles_dict[active_xml_dataframe_titles[a]] = 1
        active_xml_dataframe_titles_dict = {a: b for a, b in active_xml_dataframe_titles_dict.items() if b > 1}
        active_xml_dataframe_title_dict_names = list(active_xml_dataframe_titles_dict.keys())
        for a in range(0, len(active_xml_dataframe_title_dict_names)):
            repeat_freq = active_xml_dataframe_titles_dict[active_xml_dataframe_title_dict_names[a]]
            repeat_freq_corr = repeat_freq + 1
            repeat_seq = list(range(1, repeat_freq_corr))
            repeat_seq = [str(a) for a in repeat_seq]
            repeat_start_index = active_xml_dataframe_titles.index(active_xml_dataframe_title_dict_names[a])
            for b in range(0, len(repeat_seq)):
                active_xml_dataframe_titles[(repeat_start_index + b)] = active_xml_dataframe_titles[
                                                                            (repeat_start_index + b)] + "." + \
                                                                        repeat_seq[b]

        active_xml_dataframe_rowdata = active_xml_session_column_data + active_xml_data_evaluation_column_data + active_xml_data_measure_duration_column_data

        active_xml_dataframe = pd.DataFrame(data=[active_xml_dataframe_rowdata], columns=active_xml_dataframe_titles)
        active_xml_dataframe["Filename"] = current_xml



        qc_single_pass_string = "QC_Solo(session_data=active_xml_dataframe, exp_dir=exp_dir)"
        qc_single_pass_string = "active_xml_qc_pass = " + qc_file + "." + qc_single_pass_string
        exec(qc_single_pass_string)
        if isinstance(active_xml_qc_pass,pd.DataFrame):
            if not active_day_results:
                active_day_results = active_xml_qc_pass
            else:
                active_day_results = active_day_results.append(active_xml_qc_pass)
            analyzed_file = open(analyed_file_location, "a")
            analyzed_file.write("\n")
            analyzed_file.write(current_xml)
            analyzed_file.close()
        else:
            old_path = exp_dir + "\\" + current_xml
            new_path = bad_filepath + "\\" + current_xml
            os.rename(old_path,new_path)

    day_qc_string = "active_day_qc_results = %s.QC_Day(combined_data=active_day_results, exp_dir=exp_dir)" % (qc_file)
    exec(day_qc_string)

    csv_save_string = "%s.QC_DayWrite(combined_data=active_day_qc_results,exp_dir=exp_dir)" % (qc_file)
    exec(csv_save_string)


    pal_animalqc_string = "%s.QC_Animal(exp_dir=exp_dir)" % (qc_file)
    exec(csv_save_string)