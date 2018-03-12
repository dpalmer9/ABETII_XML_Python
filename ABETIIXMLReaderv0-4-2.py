import os
import sys
import pandas as pd
import numpy as np
import collections
import xml.etree.ElementTree as et
import time
import datetime
import wx
import math
import imp
from wx.adv import TaskBarIcon
from wx.adv import TaskBarIconEvent


def Folder_Monitor(folder_list):
    curr_working_dir = os.getcwd()
    qc_dir = curr_working_dir + "\\" + "Quality_Control_Rule"
    sys.path.insert(0, qc_dir)
    qc_list = list()
    for file in os.listdir(qc_dir):
        qc_list.append(file)
    qc_list = [a.replace(".QC", "") for a in qc_list]
    experiment_directory_list = folder_list

    for exp_directory in range(0, len(experiment_directory_list)):
        exp_dir = experiment_directory_list[exp_directory]
        exp_dir = exp_dir.replace("/","\\")
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
            wx.MessageBox("Processing Warning: You must complete the id_config file prior to running the processing")
            break
        if os.path.isfile(analyed_file_location) != True:
            analyzed_file = open(analyed_file_location, 'w')
            analyzed_file.write("File List")
            analyzed_file.write("\n")
            analyzed_file.close()
        if os.path.isfile(error_file_location) != True:
            error_file = open(error_file_location, 'w')
            error_file.write(
                'Date,FileName,MouseID,Session Date,Protocol Name,Total Session Length,Total Trials,Max Session Length,Max Trials,Error#,Error')
            error_file.write("\n")
            error_file.close()
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
        import_string = "%s = imp.load_source('%s', r'%s\\%s.QC')" % (qc_file,qc_file, qc_dir, qc_file)
        exec(import_string)

        create_string = "%s.Create_Data(exp_dir=exp_dir)" % (qc_file)
        exec(create_string)

        bad_analyzed_files = os.listdir(bad_filepath)

        analyzed_file = open(analyed_file_location, "r")
        analyzed_file_list = analyzed_file.readlines()
        analyzed_file.close()
        analyzed_file_list = analyzed_file_list[1:]
        analyzed_file_list = [a.replace("\n", "") for a in analyzed_file_list]
        xml_file_list = list()
        for file in os.listdir(exp_dir):
            if file.endswith(".xml"):
                xml_file_list.append(file)

        new_xml_file_list = list(set(analyzed_file_list) ^ set(xml_file_list))
        if "" in new_xml_file_list:
            new_xml_file_list.remove("")
        if len(new_xml_file_list) == 0:
            continue

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
        qc_master_dataframe_list = list()
        qc_dataframe_list = list()
        for x in range(0, len(new_xml_file_list)):
            current_xml = new_xml_file_list[x]
            current_filepath = exp_dir + "\\" + current_xml
            active_xml_load = et.parse(current_filepath)
            active_xml_load_root = active_xml_load.getroot()
            active_xml_load_session = active_xml_load_root[1]
            active_xml_load_data = active_xml_load_root[2]

            # Load Session Data#
            active_xml_session_string = et.tostring(active_xml_load_session)
            active_xml_session_string = bytes.decode(active_xml_session_string)
            active_xml_session_string_listed = active_xml_session_string.splitlines()
            active_xml_session_string_listed = [a.replace(" ", "") for a in active_xml_session_string_listed]
            active_xml_session_string_listed = [a.replace("</Information>", "") for a in
                                                active_xml_session_string_listed]
            active_xml_session_string_listed = [a.replace("<Information>", "") for a in
                                                active_xml_session_string_listed]
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

            active_data_count_index = list()
            active_data_measure_index = list()
            active_data_evaluation_index = list()

            active_xml_data_count_column_data = list()
            active_xml_data_count_column_titles = list()
            if any("Count" in a for a in active_data_types):
                for a in range(0, len(active_xml_data_string_listed)):
                    if "<SourceType>Count</SourceType>" in active_xml_data_string_listed[a]:
                        active_data_count_index.append(a)

                for a in range(0, len(active_data_count_index)):
                    current_title = active_xml_data_string_listed[(active_data_count_index[a] - 1)]
                    if (active_data_count_index[a] + 1) <= (len(active_xml_data_string_listed) - 1):
                        current_data = active_xml_data_string_listed[(active_data_count_index[a] + 1)]
                    else:
                        current_data = "NA"
                    if "Name" in current_title:
                        current_title = current_title.replace("<Name>", "")
                        current_title = current_title.replace("</Name>", "")
                        active_xml_data_count_column_titles.append(current_title)

                        if "Count" in current_data:
                            current_data = current_data.replace("<Count>", "")
                            current_data = current_data.replace("</Count>", "")
                            active_xml_data_count_column_data.append(float(current_data))
                        else:
                            active_xml_data_count_column_data.append("NA")

            active_xml_data_evaluation_column_titles = list()
            active_xml_data_evaluation_column_data = list()
            if any("Evaluation" in a for a in active_data_types):
                for a in range(0, len(active_xml_data_string_listed)):
                    if "<SourceType>Evaluation</SourceType>" in active_xml_data_string_listed[a]:
                        active_data_evaluation_index.append(a)

                for a in range(0, len(active_data_evaluation_index)):
                    current_title = active_xml_data_string_listed[(active_data_evaluation_index[a] - 1)]
                    if (active_data_evaluation_index[a] + 1) <= (len(active_xml_data_string_listed) - 1):
                        current_data = active_xml_data_string_listed[(active_data_evaluation_index[a] + 1)]
                    else:
                        current_data = "NA"

                    if "Name" in current_title:
                        current_title = current_title.replace("<Name>", "")
                        current_title = current_title.replace("</Name>", "")
                        active_xml_data_evaluation_column_titles.append(current_title)

                        if "Results" in current_data:
                            current_data = current_data.replace("<Results>", "")
                            current_data = current_data.replace("</Results>", "")
                            active_xml_data_evaluation_column_data.append(float(current_data))
                        else:
                            active_xml_data_evaluation_column_data.append("NA")

            active_xml_data_measure_duration_column_titles = list()
            active_xml_data_measure_duration_column_data = list()
            if any("Measure" in a for a in active_data_types):
                for a in range(0, len(active_xml_data_string_listed)):
                    if "<SourceType>Measure</SourceType>" in active_xml_data_string_listed[a]:
                        active_data_measure_index.append(a)

                for a in range(0, len(active_data_measure_index)):
                    current_title = active_xml_data_string_listed[(active_data_measure_index[a] - 1)]
                    if (active_data_measure_index[a] + 2) <= (len(active_xml_data_string_listed) - 1):
                        current_data = active_xml_data_string_listed[(active_data_measure_index[a] + 2)]
                    else:
                        current_data = "NA"
                    if "Name" in current_title:
                        current_title = current_title.replace("<Name>", "")
                        current_title = current_title.replace("</Name>", "")
                        active_xml_data_measure_duration_column_titles.append(current_title)

                        if "Duration" in current_data:
                            current_data = current_data.replace("<Duration>", "")
                            current_data = current_data.replace("</Duration>", "")
                            current_data = float(current_data) / 1000000
                            active_xml_data_measure_duration_column_data.append(float(current_data))

            # Process Data into Dataframe #
            active_xml_dataframe_titles = active_xml_data_evaluation_column_titles + active_xml_data_count_column_titles + active_xml_data_measure_duration_column_titles
            active_xml_dataframe_titles_dict = dict()
            for a in range(0, len(active_xml_dataframe_titles)):
                if active_xml_dataframe_titles[a] in active_xml_dataframe_titles_dict:
                    active_xml_dataframe_titles_dict[active_xml_dataframe_titles[a]] += 1
                else:
                    active_xml_dataframe_titles_dict[active_xml_dataframe_titles[a]] = 1
            active_xml_dataframe_titles_dict = {a: b for a, b in active_xml_dataframe_titles_dict.items() if b >= 1}
            active_xml_dataframe_title_dict_names = list(active_xml_dataframe_titles_dict.keys())
            for a in range(0, len(active_xml_dataframe_title_dict_names)):
                repeat_freq = active_xml_dataframe_titles_dict[active_xml_dataframe_title_dict_names[a]]
                repeat_freq_corr = repeat_freq + 1
                repeat_seq = list(range(1, repeat_freq_corr))
                repeat_seq = [str(a) for a in repeat_seq]
                repeat_start_index = active_xml_dataframe_titles.index(active_xml_dataframe_title_dict_names[a])
                for b in range(0, len(repeat_seq)):
                    if len(repeat_seq[b]) == 1:
                        repeat_seq[b] = '0' + repeat_seq[b]
                    active_xml_dataframe_titles[(repeat_start_index + b)] = active_xml_dataframe_titles[
                                                                                (repeat_start_index + b)] + "." + \
                                                                            repeat_seq[b]

            active_xml_dataframe_titles = active_xml_session_column_titles + active_xml_dataframe_titles

            active_xml_dataframe_rowdata = active_xml_session_column_data + active_xml_data_evaluation_column_data + active_xml_data_count_column_data + active_xml_data_measure_duration_column_data

            active_xml_dataframe = pd.DataFrame(data=[active_xml_dataframe_rowdata],
                                                columns=active_xml_dataframe_titles)
            active_xml_dataframe["Filename"] = current_xml

            qc_single_pass_string = "%s.QC_Solo(session_data=active_xml_dataframe, exp_dir=exp_dir)" % (qc_file)
            active_xml_qc_pass = eval(qc_single_pass_string)

            if not isinstance(active_xml_qc_pass, pd.DataFrame):
                active_xml_qc_pass = current_xml

            qc_dataframe_string = "%s.QC_Protocol_Bind(session_data=active_xml_qc_pass,dataframe_list=qc_dataframe_list, exp_dir=exp_dir)" % (
            qc_file)
            qc_dataframe_list = eval(qc_dataframe_string)

        if new_xml_file_list[0] == "":
            continue
        if 'Schedule_Description' in active_xml_session_column_titles:
            active_xml_session_column_titles.remove('Schedule_Description')
        active_xml_session_column_titles.append('Filename')
        empty_list_index = list()

        exp_path_list = exp_dir.split("\\")
        exp_folder_name = exp_path_list[(len(exp_path_list) - 1)]

        config_file = exp_dir + "\\" + "id_config.csv"
        error_file = exp_dir + "\\" + "error_report.csv"

        QC_Analysis_Names = ["PALAnalysis", "PALAquisition", "PALPunishIncor", "PALMustInitiate", "PALMustTouch",
                             "PALInitialTrain", "PALHabit2", "PALHabit1"]


        qc_config_file = open(config_file, 'r')
        qc_config_file_contents = qc_config_file.readlines()
        qc_config_file.close()
        qc_config_file_contents = [items.strip("\n") for items in qc_config_file_contents]
        for a in range(0, len(qc_config_file_contents)):
            if "[Animal ID List]" in qc_config_file_contents[a]:
                qc_config_start_index = a
            if "END_LIST" in qc_config_file_contents[a]:
                qc_config_end_index = a
        qc_config_id_contents = qc_config_file_contents[(qc_config_start_index + 1):qc_config_end_index]
        qc_config_id_titles = qc_config_id_contents[0].split(",")
        qc_config_id_titles = list(filter(None, qc_config_id_titles))

        qc_config_id_title_alias_index = qc_config_id_titles.index("Aliases")
        qc_config_factor_titles = qc_config_id_titles[2:qc_config_id_title_alias_index]
        qc_config_id_information = qc_config_id_contents[1:]
        qc_config_id_list = list()
        qc_config_dob_list = list()
        qc_config_alias_list = list()
        qc_config_factor_list = list()
        active_factor_range = range(2, qc_config_id_title_alias_index)
        active_factor_count = len(active_factor_range)
        for a in range(0, len(qc_config_id_information)):
            active_id_list = qc_config_id_information[a].split(",")
            active_id_list = list(filter(None, active_id_list))
            active_id = active_id_list[0]
            active_dob = active_id_list[1]
            active_alias_list = list(active_id_list[qc_config_id_title_alias_index:])
            active_factor_list = list(active_id_list[2:qc_config_id_title_alias_index])
            qc_config_id_list.append(active_id)
            qc_config_dob_list.append(active_dob)
            qc_config_alias_list.append(active_alias_list)
            qc_config_factor_list.append(active_factor_list)
        qc_config_factor_dict = dict()
        for a in range(0, len(qc_config_id_list)):
            qc_config_factor_dict[qc_config_id_list[a]] = qc_config_factor_list[a]


        for a in range(0, len(qc_dataframe_list)):
            current_datalist = qc_dataframe_list[a]
            if len(current_datalist) > 0:
                current_dataframe = current_datalist[0]
                if len(current_datalist) > 1:
                    current_dataframe = current_dataframe.append(current_datalist[1:], ignore_index=True)
                    current_dataframe = current_dataframe.drop_duplicates()

                qc_dataframe_list[a] = current_dataframe
            if len(current_datalist) == 0:
                empty_list_index.append(a)
        if len(empty_list_index) > 0:
            empty_list_index = sorted(empty_list_index, key=int, reverse=True)
            for a in range(0, len(empty_list_index)):
                del qc_dataframe_list[empty_list_index[a]]

        bin_list = ['Week', 'Day']
        for dataframe in range(0, len(qc_dataframe_list)):
            combined_data = qc_dataframe_list[dataframe]
            for a in range(0, len(qc_config_factor_titles)):
                combined_data[qc_config_factor_titles[a]] = ""
            for a in range(0, len(qc_config_factor_dict)):
                for b in range(0, len(qc_config_factor_titles)):
                    combined_data.loc[combined_data.AnimalID == qc_config_id_list[a], qc_config_factor_titles[b]] = \
                        qc_config_factor_dict[qc_config_id_list[a]][b]
            combined_data['Week'] = ""
            combined_data['Day'] = ""
            current_ordered_columns = active_xml_session_column_titles + qc_config_factor_titles + bin_list + [c
                                                                                                                     for
                                                                                                                     c
                                                                                                                     in
                                                                                                                     combined_data.columns
                                                                                                                     if
                                                                                                                     c not in active_xml_session_column_titles]
            combined_data = combined_data[current_ordered_columns]
            qc_dataframe_list[dataframe] = combined_data

        for dataframe in range(0,len(qc_dataframe_list)):
            combined_data = qc_dataframe_list[dataframe]
            data_column_titles = list(combined_data.columns.values)
            data_column_titles_filter = list(set(data_column_titles)^set(active_xml_session_column_titles))
            data_column_titles_filter = list(set(data_column_titles_filter)^set(bin_list))
            data_column_numstrip = [a[:(len(a) - 3)] for a in data_column_titles_filter]
            data_column_numstrip = list(set(data_column_numstrip))
            for a in range(0,len(data_column_numstrip)):
                title_count = 0
                title_index = list()
                for b in range(0,len(data_column_titles)):
                    if data_column_numstrip[a] in data_column_titles[b]:
                        title_count += 1
                        title_index.append(b)
                if title_count == 1:
                    old_title = data_column_titles[title_index[0]]
                    new_title = old_title[:(len(old_title) - 3)]
                    data_column_titles[title_index[0]] = new_title
            combined_data.columns = data_column_titles
            qc_dataframe_list[dataframe] = combined_data



        day_qc_string = '%s.QC_Day(dataframe_list=qc_dataframe_list, exp_dir=exp_dir)' % (qc_file)
        qc_dataframe_list = eval(day_qc_string)

        tracking_list = list()
        tracked_cols = ['AnimalID','Date/Time','ScheduleName','Filename','Week','Day']
        tracking_file_path = exp_dir + "\\" + "Tracking_Data.csv"
        for a in range(0,len(qc_dataframe_list)):
            tracking_raw = qc_dataframe_list[a]
            tracking_data = tracking_raw[tracked_cols]
            tracking_list.append(tracking_data)
        main_tracking_data = pd.concat(tracking_list, ignore_index=True)
        main_tracking_data = main_tracking_data.T.groupby(level=0).first().T
        main_tracking_data = main_tracking_data[tracked_cols]
        if os.path.isfile(tracking_file_path):
            tracking_csv = pd.read_csv(tracking_file_path)
            main_tracking_data = main_tracking_data.append(tracking_csv, ignore_index=True)
            main_tracking_data = main_tracking_data[tracked_cols]

        tracking_animal_list = main_tracking_data['AnimalID'].tolist()
        tracking_animal_list = list(set(tracking_animal_list))

        for x in range(0, len(tracking_animal_list)):
            active_animal_data = main_tracking_data.loc[main_tracking_data.AnimalID == tracking_animal_list[x]]
            active_animal_date_list = active_animal_data['Date/Time'].tolist()
            active_animal_date_list = sorted(active_animal_date_list,
                                             key=lambda x: datetime.datetime.strptime(x, '%m/%d/%Y%I:%M:%S%p'))
            for a in range(0, len(active_animal_date_list)):
                main_tracking_data.loc[((main_tracking_data['AnimalID'] == tracking_animal_list[x]) & (
                    main_tracking_data['Date/Time'] == active_animal_date_list[a])), 'Day'] = a + 1
                week = int(math.ceil((a+1)/5))
                main_tracking_data.loc[((main_tracking_data['AnimalID'] == tracking_animal_list[x]) & (
                    main_tracking_data['Date/Time'] == active_animal_date_list[a])), 'Week'] = week

        main_tracking_data = main_tracking_data.T.groupby(level=0).first().T
        main_tracking_data = main_tracking_data[tracked_cols]


        tracking_csv = open(tracking_file_path, 'w')
        main_tracking_data.to_csv(tracking_csv, index=False)
        tracking_csv.close()

        csv_save_string = "%s.QC_DayWrite(dataframe_list=qc_dataframe_list,exp_dir=exp_dir)" % (qc_file)
        exec(csv_save_string)

        del qc_dataframe_list

        pal_animalqc_string = "%s.QC_Animal(exp_dir=exp_dir)" % (qc_file)
        exec(pal_animalqc_string)

        wx.MessageBox("Processing Complete", "Folder Processing is Complete")

folder_data = open('Folder_List.txt','r')
folder_list = folder_data.readlines()
folder_data.close()

folder_list = [a.replace('\n', "") for a in folder_list]

TRAY_ICON = 'Logo_Icon.bmp'
TRAY_TOOLTIP = 'ABET II XML Analyzer'

def create_menu_item(menu, label, func):
    item = wx.MenuItem(menu, -1, label)
    menu.Bind(wx.EVT_MENU, func, id=item.GetId())
    menu.AppendItem(item)
    return item

class ProgramIcon(TaskBarIcon):

    TBMENU_FOLDER = wx.NewId()
    TBMENU_RUN = wx.NewId()
    TBMENU_EXIT = wx.NewId()

    def __init__(self):
        TaskBarIcon.__init__(self)
        self.icon = wx.Icon(TRAY_ICON, wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon, TRAY_TOOLTIP)
        self.Bind(wx.EVT_MENU, self.Folder_Window, id=self.TBMENU_FOLDER)
        self.Bind(wx.EVT_MENU, self.OnTaskBarClose, id=self.TBMENU_EXIT)
        self.Bind(wx.EVT_MENU, self.Run_Process, id=self.TBMENU_RUN)


    def CreatePopupMenu(self, evt=None):
        menu = wx.Menu()
        menu.Append(self.TBMENU_FOLDER, "Select Folders")
        menu.Append(self.TBMENU_RUN, "Run XML Processor")
        menu.AppendSeparator()
        menu.Append(self.TBMENU_EXIT, "Exit")
        return menu

    def Folder_Window(self,evt):


        self.wx_folder_frame = wx.Frame(None, wx.ID_ANY, "Folder List")
        self.panel = wx.Panel(self.wx_folder_frame)
        self.vbox1 = wx.BoxSizer(wx.VERTICAL)
        self.wx_folder_listbox = wx.ListBox(self.panel, choices=folder_list, size=(50,50))
        self.vbox1.Add(self.wx_folder_listbox, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL)
        self.add_folder_button = wx.Button(self.panel,label="Add Folder")
        self.add_folder_button.Bind(wx.EVT_BUTTON, self.Add_Folder)
        self.vbox1.Add(self.add_folder_button, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.remove_folder_button = wx.Button(self.panel,label="Remove Folder")
        self.remove_folder_button.Bind(wx.EVT_BUTTON, self.Remove_Folder)
        self.vbox1.Add(self.remove_folder_button, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.panel.SetSizer(self.vbox1)
        self.wx_folder_frame.Show()

    def Add_Folder(self,evt):
        self.new_folder = wx.DirSelector("Choose Directory to Monitor:")
        folder_list.append(self.new_folder)
        self.wx_folder_listbox.Append(self.new_folder)
        self.folder_data = open('Folder_List.txt', 'w')
        self.folder_data.writelines(folder_list)
        self.folder_data.close()

    def Remove_Folder(self,evt):
        self.selected_index = self.wx_folder_listbox.GetSelection()
        self.selected_string = self.wx_folder_listbox.GetString(self.selected_index)
        self.wx_folder_listbox.Delete(self.selected_index)
        folder_list.remove(self.selected_string)
        self.folder_data = open('Folder_List.txt', 'w')
        self.folder_data.writelines(folder_list)
        self.folder_data.close()


    def OnTaskBarClose(self,evt):
        self.Destroy()

    def Run_Process(self,evt):
        Folder_Monitor(folder_list)





if __name__ == '__main__':
    program = wx.App(False)
    taskbar = ProgramIcon()
    program.MainLoop()


