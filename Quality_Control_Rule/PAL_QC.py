import os
import pandas as pd
import numpy as np
import time
import datetime

def Create_Data(exp_dir):
    exp_path_list = exp_dir.split("\\")
    exp_folder_name = exp_path_list[(len(exp_path_list) - 1)]
    pal_filepath = exp_dir + "\\" + exp_folder_name + "_PAL_Main_Data.csv"
    pal_acq_filepath = exp_dir + "\\" + exp_folder_name + "_PAL_Acquisition_Data.csv"
    pal_punish_filepath = exp_dir + "\\" + exp_folder_name + "_PAL_Punish_Data.csv"
    pal_initiate_filepath = exp_dir + "\\" + exp_folder_name + "_PAL_MustInitiate_Data.csv"
    pal_touch_filepath = exp_dir + "\\" + exp_folder_name + "_PAL_MustTouch_Data.csv"
    pal_initial_filepath = exp_dir + "\\" + exp_folder_name + "_PAL_InitialTouch_Data.csv"
    pal_hab2_filepath = exp_dir + "\\" + exp_folder_name + "_PAL_Habituation2_Data.csv"
    pal_hab1_filepath = exp_dir + "\\" + exp_folder_name + "_PAL_Habituation1_Data.csv"

    if os.path.isfile(pal_filepath) != True:
        pal = open(pal_filepath, 'w')
        pal.close()
    if os.path.isfile(pal_acq_filepath) != True:
        pal = open(pal_acq_filepath, 'w')
        pal.close()
    if os.path.isfile(pal_punish_filepath) != True:
        pal = open(pal_punish_filepath, 'w')
        pal.close()
    if os.path.isfile(pal_initiate_filepath) != True:
        pal = open(pal_initiate_filepath, 'w')
        pal.close()
    if os.path.isfile(pal_touch_filepath) != True:
        pal = open(pal_touch_filepath, 'w')
        pal.close()
    if os.path.isfile(pal_initial_filepath) != True:
        pal = open(pal_initial_filepath, 'w')
        pal.close()
    if os.path.isfile(pal_hab2_filepath) != True:
        pal = open(pal_hab2_filepath, 'w')
        pal.close()
    if os.path.isfile(pal_hab1_filepath) != True:
        pal = open(pal_hab1_filepath, 'w')
        pal.close()

def QC_Solo(session_data, exp_dir):
    qc_trial_error = False
    qc_session = session_data
    qc_session_filename = qc_session["Filename"].iat[0]
    config_file = exp_dir + "\\" + "id_config.csv"
    error_file = exp_dir + "\\" + "error_report.csv"
    qc_config_file = open(config_file,'r')
    qc_config_file_contents = qc_config_file.readlines()
    qc_config_file.close()
    qc_config_file_contents = [items.strip("\n") for items in qc_config_file_contents]
    for a in range(0,len(qc_config_file_contents)):
        if "[Animal ID List]" in qc_config_file_contents[a]:
            qc_config_start_index = a
        if "END_LIST" in qc_config_file_contents[a]:
            qc_config_end_index = a
    qc_config_id_contents = qc_config_file_contents[(qc_config_start_index + 1):qc_config_end_index]
    qc_config_id_titles = qc_config_id_contents[0].split(",")
    qc_config_id_titles = list(filter(None, qc_config_id_titles))
    qc_config_id_title_alias_index = qc_config_id_titles.index("Aliases")
    qc_config_id_information = qc_config_id_contents[1:]
    qc_config_id_list = list()
    qc_config_dob_list = list()
    qc_config_alias_list = list()
    for a in range(0,len(qc_config_id_information)):
        active_id_list = qc_config_id_information[a].split(",")
        active_id_list = list(filter(None, active_id_list))
        active_id = active_id_list[0]
        active_dob = active_id_list[1]
        active_alias_list = list(active_id_list[qc_config_id_title_alias_index:])
        qc_config_id_list.append(active_id)
        qc_config_dob_list.append(active_dob)
        qc_config_alias_list.append(active_alias_list)

    qc_session_col_titles = list(qc_session.columns.values)

    qc_session_anid = qc_session["AnimalID"].iat[0]
    for a in range(0,len(qc_config_alias_list)):
        active_alias_check_list = list(qc_config_alias_list[a])
        if qc_session_anid in active_alias_check_list:
            qc_session_trueid = qc_config_id_list[a]
        else:
            qc_session_trueid = "NA"
    if qc_session_trueid == "NA":
        error_date = time.strftime("%d/%m/%Y")
        error_file_active = open(error_file,'a')
        error_file_active.write("\n")
        error_file_active.write('%s,%s,The file does not contain a known/matching Animal ID. Please verify aliases in config file. File was removed.' % (error_date,qc_session_filename))
        error_file_active.close()
        qc_trial_error = True
        return
    qc_session_acc = qc_session["EndSummary-%Correct"].iat[0]
    qc_session_corr = qc_session['EndSummary-NoCorrectionTrials'].iat[0]
    qc_session_time = qc_session['EndSummary-Condition'].iat[0]
    qc_session_trials = qc_session['EndSummary-TrialsCompleted'].iat[0]
    if (qc_session_time < 3599.99) and (qc_session_trials < 36):
        error_date = time.strftime("%d/%m/%Y")
        error_file_active = open(error_file,'a')
        error_file_active.write("\n")
        error_file_active.write('%s,%s,The file contains less than the maximum trials and less than the maximum time. This file does not conform to experiment protocols. File was removed' % (error_date,qc_session_filename))
        error_file_active.close()
        qc_trial_error = True
    if ((qc_session_acc == "NaN") or (qc_session_acc == "")):
        qc_session.set_value(0,'EndSummary-%Correct', 0)
        qc_session_acc = 0
    if ((qc_session_corr == "NaN") or (qc_session_corr == "")):
        qc_session.set_value(0,'EndSummary-NoCorrectionTrials',0)
    if qc_trial_error == True:
        qc_session = str()

    return qc_session


def QC_Day(combined_data, exp_dir):
    qc_combined = combined_data

    bad_filepath = exp_dir + "\\" + "BadXML"

    qc_id_list = qc_combined['AnimalID'].tolist()

    qc_date_list = qc_combined['Date/Time'].tolist()

    qc_id_unique = list(set(qc_id_list))
    qc_id_unique_count = list()
    for a in range(0,len(qc_id_unique)):
        qc_id_unique_count.insert(a,0)
        for b in range(0,len(qc_id_list)):
            if qc_id_unique[a] == qc_id_list[b]:
                qc_id_unique_count[a] += 1

    for a in range(0,len(qc_id_unique_count)):
        qc_bad_row_index_list = list()
        qc_bad_duplicate_filenames = list()
        if qc_id_unique_count[a] > 1:
            flagged_id = qc_id_unique[a]
            for b in range(0,len(qc_id_list)):
                if qc_id_list[b] == flagged_id:
                    qc_bad_row_index_list.append(b)
            for b in range(0,len(qc_bad_row_index_list)):
                curr_index = qc_bad_row_index_list[b]
                curr_date = datetime.strptime(qc_date_list[curr_index],'%m/%d/%Y%I:%M:%S%p')
                for c in range((b + 1),len(qc_bad_row_index_list)):
                    check_index = qc_bad_row_index_list[c]
                    check_date = datetime.strptime(qc_date_list[check_index],'%m/%d/%Y%I:%M:%S%p')
                    bad_original = qc_combined.at[curr_index,'Filename']
                    if curr_date.date() == check_date.date():
                        bad_file = qc_combined.at[check_index,'Filename']
                        qc_bad_duplicate_filenames.append(bad_original)
                        qc_bad_duplicate_filenames.append(bad_file)

    if len(qc_bad_duplicate_filenames) > 0:
        for a in range(0, len(qc_bad_duplicate_filenames)):
           qc_combined = qc_combined.loc[qc_combined['Filename'] != qc_bad_duplicate_filenames[a]]
           old_filepath = exp_dir + "\\" + qc_bad_duplicate_filenames[a]
           new_filepath = bad_filepath + "\\" + qc_bad_duplicate_filenames[a]
           os.rename(old_filepath,new_filepath)
    return qc_combined

def QC_DayWrite(combined_data,exp_dir):
    exp_path_list = exp_dir.split("\\")
    exp_folder_name = exp_path_list[(len(exp_path_list) - 1)]

    config_file = exp_dir + "\\" + "id_config.csv"
    error_file = exp_dir + "\\" + "error_report.csv"
    qc_config_file = open(config_file,'r')
    qc_config_file_contents = qc_config_file.readlines()
    qc_config_file.close()
    qc_config_file_contents = [items.strip("\n") for items in qc_config_file_contents]
    for a in range(0,len(qc_config_file_contents)):
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
    for a in range(0,len(qc_config_id_information)):
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
    for a in range(0,len(qc_config_id_list)):
        qc_config_factor_dict[qc_config_id_list[a]] = qc_config_factor_list[a]

    for a in range(0,len(qc_config_factor_titles)):
        combined_data[qc_config_factor_titles[a]] = ""
    for a in range(0,len(qc_config_factor_dict)):
        for b in range(0,len(qc_config_factor_titles)):
            combined_data.loc[combined_data.AnimalID == qc_config_id_list[a], qc_config_factor_titles[b]] = qc_config_factor_dict[qc_config_id_list[a]][b]
    combined_data['Week'] = ""
    combined_data['Day'] = ""

    pal_main_name_list = ['Mouse dPAL 1 v3', 'Mouse dPAL 2 v3', 'Mouse dPAL 3 v3', 'Mouse dPAL 4 v3', 'Mouse dPAL 5 v3', 'Mouse dPAL 6 v3', 'Mouse dPAL 6 Retention v3', 'Mouse dPAL RETENTION 1 v3', 'Mouse sPAL 1 v3','Mouse sPAL v3','Mouse dPAL v3','Mouse sPAL v3' ]
    pal_main_name_list = [a.replace(" ","") for a in pal_main_name_list]
    pal_acq_name_list = ['Mouse dPAL acquisition 1 v3', 'Mouse dPAL acquisition 2 v3','Mouse dPAL acquisition 3 v3','Mouse dPAL acquisition 4 v3','Mouse dPAL acquisition 5 v3','Mouse dPAL acquisition 6 v3','Mouse sPAL acquisition 1 v3','Mouse sPAL acquisition v3','Mouse dPAL acquisition v3']
    pal_acq_name_list = [a.replace(" ","") for a in pal_acq_name_list]
    pal_punish_name_list = ['Mouse PAL Punish Incorrect Training v3 Jan2015MOD','Mouse PAL Punish Incorrect Training v3']
    pal_punish_name_list = [a.replace(" ","") for a in pal_punish_name_list]
    pal_initiate_name_list = ['Mouse PAL Must Initiate Training v3']
    pal_initiate_name_list = [a.replace(" ","") for a in pal_initiate_name_list]
    pal_touch_name_list = ['Mouse PAL Must Touch Training v3']
    pal_touch_name_list = [a.replace(" ","") for a in pal_touch_name_list]
    pal_initial_name_list = ['Mouse PAL Initial Touch Training v3']
    pal_initial_name_list = [a.replace(" ","") for a in pal_initial_name_list]
    pal_hab2_name_list = ['Mouse PAL Habituation 2 v2']
    pal_hab2_name_list = [a.replace(" ","") for a in pal_hab2_name_list]
    pal_hab1_name_list = ['Mouse PAL Habituation 1 v2']
    pal_hab1_name_list = [a.replace(" ","") for a in pal_hab1_name_list]

    pal_filepath = exp_dir + "\\" + exp_folder_name + "_PAL_Main_Data.csv"
    pal_acq_filepath = exp_dir + "\\" + exp_folder_name + "_PAL_Acquisition_Data.csv"
    pal_punish_filepath = exp_dir + "\\" + exp_folder_name + "_PAL_Punish_Data.csv"
    pal_initiate_filepath = exp_dir + "\\" + exp_folder_name + "_PAL_MustInitiate_Data.csv"
    pal_touch_filepath = exp_dir + "\\" + exp_folder_name + "_PAL_MustTouch_Data.csv"
    pal_initial_filepath = exp_dir + "\\" + exp_folder_name + "_PAL_InitialTouch_Data.csv"
    pal_hab2_filepath = exp_dir + "\\" + exp_folder_name + "_PAL_Habituation2_Data.csv"
    pal_hab1_filepath = exp_dir + "\\" + exp_folder_name + "_PAL_Habituation1_Data.csv"

    pal_main_data = combined_data[combined_data['ScheduleName'].isin(pal_main_name_list)]
    if pal_main_data.empty != True:
        if os.stat(pal_filepath).st_size != 0:
            pal_main_data_main = pd.read_csv(pal_filepath)
            pal_main_data_main = pal_main_data_main.append(pal_main_data)
            pal_main_data_main.to_csv(pal_filepath, index=False)
        elif os.stat(pal_filepath).st_size == 0:
            pal_main_data.to_csv(pal_filepath, index=False)
        
    pal_acq_data = combined_data[combined_data['ScheduleName'].isin(pal_acq_name_list)]
    if pal_acq_data.empty != True:
        if os.stat(pal_filepath).st_size != 0:
            pal_acq_data_acq = pd.read_csv(pal_filepath)
            pal_acq_data_acq = pal_acq_data_acq.append(pal_acq_data)
            pal_acq_data_acq.to_csv(pal_filepath, index=False)
        elif os.stat(pal_filepath).st_size == 0:
            pal_acq_data.to_csv(pal_filepath, index=False)

    pal_punish_data = combined_data[combined_data['ScheduleName'].isin(pal_punish_name_list)]
    if pal_punish_data.empty != True:
        if os.stat(pal_filepath).st_size != 0:
            pal_punish_data_punish = pd.read_csv(pal_filepath)
            pal_punish_data_punish = pal_punish_data_punish.append(pal_punish_data)
            pal_punish_data_punish.to_csv(pal_filepath, index=False)
        elif os.stat(pal_filepath).st_size == 0:
            pal_punish_data.to_csv(pal_filepath, index=False)
        
    pal_initiate_data = combined_data[combined_data['ScheduleName'].isin(pal_initiate_name_list)]
    if pal_initiate_data.empty != True:
        if os.stat(pal_filepath).st_size != 0:
            pal_initiate_data_initiate = pd.read_csv(pal_filepath)
            pal_initiate_data_initiate = pal_initiate_data_initiate.append(pal_initiate_data)
            pal_initiate_data_initiate.to_csv(pal_filepath, index=False)
        elif os.stat(pal_filepath).st_size == 0:
            pal_initiate_data.to_csv(pal_filepath, index=False)
        
    pal_touch_data = combined_data[combined_data['ScheduleName'].isin(pal_touch_name_list)]
    if pal_touch_data.empty != True:
        if os.stat(pal_filepath).st_size != 0:
            pal_touch_data_touch = pd.read_csv(pal_filepath)
            pal_touch_data_touch = pal_touch_data_touch.append(pal_touch_data)
            pal_touch_data_touch.to_csv(pal_filepath, index=False)
        elif os.stat(pal_filepath).st_size == 0:
            pal_touch_data.to_csv(pal_filepath, index=False)
        
    pal_initial_data = combined_data[combined_data['ScheduleName'].isin(pal_initial_name_list)]
    if pal_initial_data.empty != True:
        if os.stat(pal_filepath).st_size != 0:
            pal_initial_data_initial = pd.read_csv(pal_filepath)
            pal_initial_data_initial = pal_initial_data_initial.append(pal_initial_data)
            pal_initial_data_initial.to_csv(pal_filepath, index=False)
        elif os.stat(pal_filepath).st_size == 0:
            pal_initial_data.to_csv(pal_filepath, index=False)
        
    pal_hab2_data = combined_data[combined_data['ScheduleName'].isin(pal_hab2_name_list)]
    if pal_hab2_data.empty != True:
        if os.stat(pal_filepath).st_size != 0:
            pal_hab2_data_hab2 = pd.read_csv(pal_filepath)
            pal_hab2_data_hab2 = pal_hab2_data_hab2.append(pal_hab2_data)
            pal_hab2_data_hab2.to_csv(pal_filepath, index=False)
        elif os.stat(pal_filepath).st_size == 0:
            pal_hab2_data.to_csv(pal_filepath, index=False)
        
    pal_hab1_data = combined_data[combined_data['ScheduleName'].isin(pal_hab1_name_list)]
    if pal_hab1_data.empty != True:
        if os.stat(pal_filepath).st_size != 0:
            pal_hab1_data_hab1 = pd.read_csv(pal_filepath)
            pal_hab1_data_hab1 = pal_hab1_data_hab1.append(pal_hab1_data)
            pal_hab1_data_hab1.to_csv(pal_filepath, index=False)
        elif os.stat(pal_filepath).st_size == 0:
            pal_hab1_data.to_csv(pal_filepath, index=False)

def QC_Animal(exp_dir):
    exp_path_list = exp_dir.split("\\")
    exp_folder_name = exp_path_list[(len(exp_path_list) - 1)]
    pal_filepath = exp_dir + "\\" + exp_folder_name + "_PAL_Main_Data.csv"
    pal_acq_filepath = exp_dir + "\\" + exp_folder_name + "_PAL_Acquisition_Data.csv"
    pal_punish_filepath = exp_dir + "\\" + exp_folder_name + "_PAL_Punish_Data.csv"
    pal_initiate_filepath = exp_dir + "\\" + exp_folder_name + "_PAL_MustInitiate_Data.csv"
    pal_touch_filepath = exp_dir + "\\" + exp_folder_name + "_PAL_MustTouch_Data.csv"
    pal_initial_filepath = exp_dir + "\\" + exp_folder_name + "_PAL_InitialTouch_Data.csv"
    pal_hab2_filepath = exp_dir + "\\" + exp_folder_name + "_PAL_Habituation2_Data.csv"
    pal_hab1_filepath = exp_dir + "\\" + exp_folder_name + "_PAL_Habituation1_Data.csv"
    pal_protocol_list = [pal_filepath,pal_acq_filepath,pal_punish_filepath,pal_initiate_filepath,pal_touch_filepath,pal_initial_filepath,pal_hab2_filepath,pal_hab1_filepath]

    for y in range(0,pal_protocol_list):
        selected_filepath = pal_protocol_list[a]
        if os.stat(selected_filepath).st_size != 0:
            dateparse = lambda x: pd.datetime.strptime(x, '%Y-%m-%dT%H:%M:%S.%f ')
            total_data = pd.read_csv(selected_filepath, parse_dates=['Date/Time'], date_parser=dateparse)
            qc_animal_list = total_data['AnimalID'].tolist()
            qc_animal_list = list(set(qc_animal_list))

            for x in range(0, len(qc_animal_list)):
                active_animal_data = total_data.loc[total_data.AnimalID == qc_animal_list[x]]
                active_animal_date_list = active_animal_data['Date/Time'].tolist()
                active_animal_date_list = sorted(active_animal_date_list,
                                                 key=lambda x: datetime.datetime.strptime(x, '%m/%d/%Y%I:%M:%S%p'))
                for a in range(0, len(active_animal_date_list)):
                    total_data.loc[((total_data['AnimalID'] == qc_animal_list) & (
                        total_data['Date/Time'] == active_animal_date_list[a])), 'Day'] = a + 1
                    week = int(5 * round(a / 5))
                    total_data.loc[((total_data['AnimalID'] == qc_animal_list) & (
                        total_data['Date/Time'] == active_animal_date_list[a])), 'Week'] = week

            total_data.to_csv(selected_filepath, index=False)


def QC_Overall(total_data):
    return