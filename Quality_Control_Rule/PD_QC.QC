import os
import pandas as pd
import numpy as np
import time
import datetime
import dateutil.parser as dparser
import collections
import math

def Create_Data(exp_dir):
    exp_path_list = exp_dir.split("\\")
    exp_folder_name = exp_path_list[(len(exp_path_list) - 1)]
    pd_filepath = exp_dir + "\\" + exp_folder_name + "_PD_Main_Data.csv"
    pd_acq_filepath = exp_dir + "\\" + exp_folder_name + "_PD_Acquisition_Data.csv"
    pd_punish_filepath = exp_dir + "\\" + exp_folder_name + "_PD_Punish_Data.csv"
    pd_initiate_filepath = exp_dir + "\\" + exp_folder_name + "_PD_MustInitiate_Data.csv"
    pd_touch_filepath = exp_dir + "\\" + exp_folder_name + "_PD_MustTouch_Data.csv"
    pd_initial_filepath = exp_dir + "\\" + exp_folder_name + "_PD_InitialTouch_Data.csv"
    pd_hab2_filepath = exp_dir + "\\" + exp_folder_name + "_PD_Habituation2_Data.csv"
    pd_hab1_filepath = exp_dir + "\\" + exp_folder_name + "_PD_Habituation1_Data.csv"

    if os.path.isfile(pd_filepath) != True:
        pd = open(pd_filepath, 'w')
        pd.close()
    if os.path.isfile(pd_acq_filepath) != True:
        pd = open(pd_acq_filepath, 'w')
        pd.close()
    if os.path.isfile(pd_punish_filepath) != True:
        pd = open(pd_punish_filepath, 'w')
        pd.close()
    if os.path.isfile(pd_initiate_filepath) != True:
        pd = open(pd_initiate_filepath, 'w')
        pd.close()
    if os.path.isfile(pd_touch_filepath) != True:
        pd = open(pd_touch_filepath, 'w')
        pd.close()
    if os.path.isfile(pd_initial_filepath) != True:
        pd = open(pd_initial_filepath, 'w')
        pd.close()
    if os.path.isfile(pd_hab2_filepath) != True:
        pd = open(pd_hab2_filepath, 'w')
        pd.close()
    if os.path.isfile(pd_hab1_filepath) != True:
        pd = open(pd_hab1_filepath, 'w')
        pd.close()

def QC_Solo(session_data, exp_dir):
    bad_filepath = exp_dir + "\\" + "BadXML"
    qc_trial_error = False
    qc_analysis_error = False
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
            break
        else:
            qc_session_trueid = "NA"
    if qc_session_trueid == "NA":
        error_date = time.strftime("%d/%m/%Y")
        error_file_active = open(error_file,'a')
        error_file_active.write("\n")
        error_file_active.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,1,The file does not contain a known/matching Animal ID. Please verify aliases in config file. File was removed.' % (error_date,qc_session_filename,qc_session['AnimalID'].iat[0],qc_session['Date/Time'].iat[0],qc_session['ScheduleName'].iat[0],qc_session['EndSummary-Condition.01'].iat[0],'na',qc_session['Max_Schedule_Time'].iat[0],qc_session['Max_Number_Trials'].iat[0]))
        error_file_active.close()
        qc_trial_error = True
        return

    QC_Analysis_Names = ["PDAnalysis","PDPunishIncor","PDMustInitiate","PDMustTouch","PDInitialTrain","PDHabit2","PDHabit1"]
    PD_Main_Files = ['Mouse Pairwise Discrimination v3','PD_Acquisition_1_v3','PD_Acquisition_2_v3','PD_Acquisition_3_v3','PD_Baseline_1_v3','PD_Baseline_2_v3','PD_Baseline_3_v3','PD_Maintenance_1_v3','PD_Maintenance_2_v3','PD_Maintenance_3_v3','PD_RetentionReversal_2_v3','PD_RetentionReversal_3_v3','PD_Reversal_1_v3','PD_Reversal_2_v3','PD_Reversal_3_v3']
    PD_Punish_Files = ['Mouse Pairwise Punish Incorrect Training v3','PD_Punish_Incorrect_RETRAIN_v3','PD_Punish_Incorrect_Training_v3']
    PD_Initiate_Files = ['Mouse Pairwise Must Initiate Training v3','PD_Must_Initiate_Training_v3','PD_Must_Initiate_RETRAIN_v3']
    PD_Touch_Files = ['Mouse Pairwise Must Touch Training v3','PD_Must_Touch_RETRAIN_v3','PD_Must_Touch_Training_v3']
    PD_Initial_Files = ['Mouse Pairwise Initial Touch Training v3','PD_Initial_Touch_RETRAIN_v3','PD_Initial_Touch_Training_v3',]
    PD_Habit2_Files = ['Mouse Pairwise Habituation 2 v2','PD_Habituation_2_v2']
    PD_Habit1_Files = ['Mouse Pairwise Habituation 1 v2','PD_Habituation_1_v2']
    QC_Protocol_List = [PD_Main_Files,PD_Punish_Files,PD_Initiate_Files,PD_Touch_Files,PD_Initial_Files,PD_Habit2_Files,PD_Habit1_Files]
    QC_Analysis_Type = str()
    QC_Analysis_Index = int()
    for a in range(0,len(QC_Analysis_Names)):
        if qc_session['AnalysisName'].iat[0] == QC_Analysis_Names[a]:
            QC_Analysis_Type = QC_Analysis_Names[a]
            QC_Analysis_Index = a
    Current_Protocol = QC_Protocol_List[QC_Analysis_Index]
    for a in range(0,len(Current_Protocol)):
        Current_File = Current_Protocol[a].replace(" ", "")
        if qc_session['ScheduleName'].iat[0] == Current_File:
            qc_analysis_error = False
            break
        else:
            qc_analysis_error = True

    if qc_analysis_error == True:
        qc_trial_error = True
        error_file_active = open(error_file, 'a')
        error_date = time.strftime("%d/%m/%Y")
        error_file_active.write("\n")
        error_file_active.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,2,The file does not have an appropriate analysis routine for the given file structure. Please regenerate this session.' % (error_date,qc_session_filename,qc_session['AnimalID'].iat[0],qc_session['Date/Time'].iat[0],qc_session['ScheduleName'].iat[0],qc_session['EndSummary-Condition.01'].iat[0],'na',qc_session['Max_Schedule_Time'].iat[0],qc_session['Max_Number_Trials'].iat[0]))
        error_file_active.close()


    if qc_session['AnalysisName'].iat[0] in QC_Analysis_Names[0]:
        qc_session_acc = qc_session["EndSummary-%Correct.01"].iat[0]
        qc_session_corr = qc_session['EndSummary-NoCorrectionTrials.01'].iat[0]
        qc_session_time = qc_session['EndSummary-Condition.01'].iat[0]
        if qc_session_time == 'NA':
            qc_session_time = 0
        qc_session_trials = qc_session['EndSummary-TrialsCompleted.01'].iat[0]
        if qc_session_trials == 'NA':
            qc_session_trials = 0
        if ((qc_session_time < 3599.99) or (qc_session_time == 'NA')) and ((qc_session_trials < 30) or (qc_session_trials == 'NA')):
            error_date = time.strftime("%d/%m/%Y")
            error_file_active = open(error_file,'a')
            error_file_active.write("\n")
            error_file_active.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,3,The file contains less than the maximum trials and less than the maximum time. This file does not conform to experiment protocols. File was removed' % (error_date,qc_session_filename,qc_session['AnimalID'].iat[0],qc_session['Date/Time'].iat[0],qc_session['ScheduleName'].iat[0],qc_session['EndSummary-Condition.01'].iat[0],qc_session['EndSummary-TrialsCompleted.01'].iat[0],qc_session['Max_Schedule_Time'].iat[0],qc_session['Max_Number_Trials'].iat[0]))
            error_file_active.close()
            qc_trial_error = True
        if ((qc_session_acc == "NaN") or (qc_session_acc == "") or (qc_session_acc == 'NA')):
            qc_session.set_value(0,'EndSummary-%Correct.01', 0)
            qc_session_acc = 0
        if ((qc_session_corr == "NaN") or (qc_session_corr == "") or (qc_session_acc == 'NA')):
            qc_session.set_value(0,'EndSummary-NoCorrectionTrials.01',0)
    if qc_trial_error == True:
        qc_session = ""

    return qc_session


def QC_Protocol_Bind(session_data, dataframe_list, exp_dir):
    analyed_file_location = exp_dir + "\\" + "analyzed_xml.csv"
    bad_filepath = exp_dir + "\\" + "BadXML"
    if len(dataframe_list) == 0:
        active_day_main_results_list = list()
        dataframe_list.append(active_day_main_results_list)
        active_day_acq_results_list = list()
        dataframe_list.append(active_day_acq_results_list)
        active_day_punish_results_list = list()
        dataframe_list.append(active_day_punish_results_list)
        active_day_initiate_results_list = list()
        dataframe_list.append(active_day_initiate_results_list)
        active_day_touch_results_list = list()
        dataframe_list.append(active_day_touch_results_list)
        active_day_initial_results_list = list()
        dataframe_list.append(active_day_initial_results_list)
        active_day_habit2_results_list = list()
        dataframe_list.append(active_day_habit2_results_list)
        active_day_habit1_results_list = list()
        dataframe_list.append(active_day_habit1_results_list)

    if isinstance(session_data, pd.DataFrame):
        current_xml = session_data['Filename'].iat[0]
        analyzed_file = open(analyed_file_location, "a")
        analyzed_file.write("\n")
        analyzed_file.write(current_xml)
        analyzed_file.close()

        active_day_main_results_list = dataframe_list[0]
        active_day_punish_results_list = dataframe_list[1]
        active_day_initiate_results_list = dataframe_list[2]
        active_day_touch_results_list = dataframe_list[3]
        active_day_initial_results_list = dataframe_list[4]
        active_day_habit2_results_list = dataframe_list[5]
        active_day_habit1_results_list = dataframe_list[6]

        if session_data['AnalysisName'].iat[0] == "PDAnalysis":
            if len(active_day_main_results_list) > 0:
                active_day_main_results_list.append(session_data)
            elif len(active_day_main_results_list) == 0:
                active_day_main_results_list = [session_data]
        if session_data['AnalysisName'].iat[0] == "PDPunishIncor":
            if len(active_day_punish_results_list) > 0:
                active_day_punish_results_list.append(session_data)
            elif len(active_day_punish_results_list) == 0:
                active_day_punish_results_list = [session_data]
        if session_data['AnalysisName'].iat[0] == "PDMustInitiate":
            if len(active_day_initiate_results_list) > 0:
                active_day_initiate_results_list.append(session_data)
            elif len(active_day_initiate_results_list) == 0:
                active_day_initiate_results_list = [session_data]
        if session_data['AnalysisName'].iat[0] == "PDMustTouch":
            if len(active_day_touch_results_list) > 0:
                active_day_touch_results_list.append(session_data)
            elif len(active_day_touch_results_list) == 0:
                active_day_touch_results_list = [session_data]
        if session_data['AnalysisName'].iat[0] == "PDInitialTrain":
            if len(active_day_initial_results_list) > 0:
                active_day_initial_results_list.append(session_data)
            elif len(active_day_initial_results_list) == 0:
                active_day_initial_results_list = [session_data]
        if session_data['AnalysisName'].iat[0] == "PDHabit2":
            if len(active_day_habit2_results_list) > 0:
                active_day_habit2_results_list.append(session_data)
            elif len(active_day_habit2_results_list) == 0:
                active_day_habit2_results_list = [session_data]
        if session_data['AnalysisName'].iat[0] == "PDHabit1":
            if len(active_day_habit1_results_list) > 0:
                active_day_habit1_results_list.append(session_data)
            elif len(active_day_habit1_results_list) == 0:
                active_day_habit1_results_list = [session_data]
        dataframe_list = [active_day_main_results_list, active_day_acq_results_list, active_day_punish_results_list,
                          active_day_initiate_results_list, active_day_touch_results_list,
                          active_day_initial_results_list, active_day_habit2_results_list,
                          active_day_habit1_results_list]

    if not isinstance(session_data, pd.DataFrame):
        old_path = exp_dir + "\\" + session_data
        new_path = bad_filepath + "\\" + session_data
        os.rename(old_path, new_path)

    return dataframe_list

def QC_Dataframe_Bind(dataframe_list,exp_dir):
    return

def QC_Day(dataframe_list, exp_dir):
    for dataframe in range(0,len(dataframe_list)):
        qc_combined = dataframe_list[dataframe]
        qc_day_error = False
        error_file = exp_dir + "\\" + "error_report.csv"

        bad_filepath = exp_dir + "\\" + "BadXML"

        qc_id_list = qc_combined['AnimalID'].tolist()

        qc_id_unique = list(set(qc_id_list))

        for a in range(0, len(qc_id_unique)):
            animal_data = qc_combined[qc_combined['AnimalID'] == qc_id_unique[a]]
            animal_date = animal_data['Date/Time'].tolist()
            animal_date = [datetime.datetime.strptime(a, '%m/%d/%Y%I:%M:%S%p') for a in animal_date]
            animal_date = [a.date() for a in animal_date]
            animal_date_set = list(set(animal_date))
            date_duplicates = [k for k, v in collections.Counter(animal_date).items() if v > 1]
            if len(date_duplicates) > 0:
                for date in date_duplicates:
                    bad_data = qc_combined[
                        (qc_combined['AnimalID'] == qc_id_unique[a]) & (qc_combined['Date/Time'] == date)]
                    qc_combined = qc_combined[
                        -(qc_combined['AnimalID'] == qc_id_unique[a]) & -(qc_combined['Date/Time'] == date)]
                    bad_files = bad_data['Filename'].tolist()
                    for file in bad_files:
                        error_file_active = open(error_file, 'a')
                        error_date = time.strftime("%d/%m/%Y")
                        error_file_active.write("\n")
                        error_file_active.write(
                            '%s,%s,%s,%s,%s,%s,%s,%s,%s,4,The file has a known duplicate within the dataset. One of these files is incorrect. Please review.' % (error_date,file,qc_id_unique[a],date,'na','na','na','na','na'))
                        error_file_active.close()
                        old_filepath = exp_dir + "\\" + file
                        new_filepath = bad_filepath + "\\" + file
                        os.rename(old_filepath, new_filepath)

        dataframe_list[dataframe] = qc_combined
    return dataframe_list


def QC_DayWrite(dataframe_list,exp_dir):
    exp_path_list = exp_dir.split("\\")
    exp_folder_name = exp_path_list[(len(exp_path_list) - 1)]

    config_file = exp_dir + "\\" + "id_config.csv"
    error_file = exp_dir + "\\" + "error_report.csv"

    QC_Analysis_Names = ["PDAnalysis", "PDAquisition", "PDPunishIncor", "PDMustInitiate", "PDMustTouch",
                         "PDInitialTrain", "PDHabit2", "PDHabit1"]

    pd_filepath = exp_dir + "\\" + exp_folder_name + "_PD_Main_Data.csv"
    pd_acq_filepath = exp_dir + "\\" + exp_folder_name + "_PD_Acquisition_Data.csv"
    pd_punish_filepath = exp_dir + "\\" + exp_folder_name + "_PD_Punish_Data.csv"
    pd_initiate_filepath = exp_dir + "\\" + exp_folder_name + "_PD_MustInitiate_Data.csv"
    pd_touch_filepath = exp_dir + "\\" + exp_folder_name + "_PD_MustTouch_Data.csv"
    pd_initial_filepath = exp_dir + "\\" + exp_folder_name + "_PD_InitialTouch_Data.csv"
    pd_hab2_filepath = exp_dir + "\\" + exp_folder_name + "_PD_Habituation2_Data.csv"
    pd_hab1_filepath = exp_dir + "\\" + exp_folder_name + "_PD_Habituation1_Data.csv"

    for dataframe in range(0,len(dataframe_list)):
        combined_data = dataframe_list[dataframe]

        if combined_data['AnalysisName'].iat[0] == QC_Analysis_Names[0]:
            if os.stat(pd_filepath).st_size != 0:
                pd_main_data_main = pd.read_csv(pd_filepath)
                pd_main_data_main = pd_main_data_main.append(combined_data)
                pd_main_data_main.to_csv(pd_filepath, index=False)
            elif os.stat(pd_filepath).st_size == 0:
                combined_data.to_csv(pd_filepath, index=False)

        if combined_data['AnalysisName'].iat[0] == QC_Analysis_Names[1]:
            if os.stat(pd_acq_filepath).st_size != 0:
                pd_acq_data_acq = pd.read_csv(pd_acq_filepath)
                pd_acq_data_acq = pd_acq_data_acq.append(combined_data)
                pd_acq_data_acq.to_csv(pd_acq_filepath, index=False)
            elif os.stat(pd_acq_filepath).st_size == 0:
                combined_data.to_csv(pd_acq_filepath, index=False)

        if combined_data['AnalysisName'].iat[0] == QC_Analysis_Names[2]:
            if os.stat(pd_punish_filepath).st_size != 0:
                pd_punish_data_punish = pd.read_csv(pd_punish_filepath)
                pd_punish_data_punish = pd_punish_data_punish.append(combined_data)
                pd_punish_data_punish.to_csv(pd_punish_filepath, index=False)
            elif os.stat(pd_punish_filepath).st_size == 0:
                combined_data.to_csv(pd_punish_filepath, index=False)

        if combined_data['AnalysisName'].iat[0] == QC_Analysis_Names[3]:
            if os.stat(pd_initiate_filepath).st_size != 0:
                pd_initiate_data_initiate = pd.read_csv(pd_initiate_filepath)
                pd_initiate_data_initiate = pd_initiate_data_initiate.append(combined_data)
                pd_initiate_data_initiate.to_csv(pd_initiate_filepath, index=False)
            elif os.stat(pd_initiate_filepath).st_size == 0:
                combined_data.to_csv(pd_initiate_filepath, index=False)

        if combined_data['AnalysisName'].iat[0] == QC_Analysis_Names[4]:
            if os.stat(pd_touch_filepath).st_size != 0:
                pd_touch_data_touch = pd.read_csv(pd_touch_filepath)
                pd_touch_data_touch = pd_touch_data_touch.append(combined_data)
                pd_touch_data_touch.to_csv(pd_touch_filepath, index=False)
            elif os.stat(pd_touch_filepath).st_size == 0:
                combined_data.to_csv(pd_touch_filepath, index=False)

        if combined_data['AnalysisName'].iat[0] == QC_Analysis_Names[5]:
            if os.stat(pd_initial_filepath).st_size != 0:
                pd_initial_data_initial = pd.read_csv(pd_initial_filepath)
                pd_initial_data_initial = pd_initial_data_initial.append(combined_data)
                pd_initial_data_initial.to_csv(pd_initial_filepath, index=False)
            elif os.stat(pd_initial_filepath).st_size == 0:
                combined_data.to_csv(pd_initial_filepath, index=False)

        if combined_data['AnalysisName'].iat[0] == QC_Analysis_Names[6]:
            if os.stat(pd_hab2_filepath).st_size != 0:
                pd_hab2_data_hab2 = pd.read_csv(pd_hab2_filepath)
                pd_hab2_data_hab2 = pd_hab2_data_hab2.append(combined_data)
                pd_hab2_data_hab2.to_csv(pd_hab2_filepath, index=False)
            elif os.stat(pd_hab2_filepath).st_size == 0:
                combined_data.to_csv(pd_hab2_filepath, index=False)

        if combined_data['AnalysisName'].iat[0] == QC_Analysis_Names[7]:
            if os.stat(pd_hab1_filepath).st_size != 0:
                pd_hab1_data_hab1 = pd.read_csv(pd_hab1_filepath)
                pd_hab1_data_hab1 = pd_hab1_data_hab1.append(combined_data)
                pd_hab1_data_hab1.to_csv(pd_hab1_filepath, index=False)
            elif os.stat(pd_hab1_filepath).st_size == 0:
                combined_data.to_csv(pd_hab1_filepath, index=False)

def QC_Animal(exp_dir):
    exp_path_list = exp_dir.split("\\")
    exp_folder_name = exp_path_list[(len(exp_path_list) - 1)]
    pd_filepath = exp_dir + "\\" + exp_folder_name + "_PD_Main_Data.csv"
    pd_acq_filepath = exp_dir + "\\" + exp_folder_name + "_PD_Acquisition_Data.csv"
    pd_punish_filepath = exp_dir + "\\" + exp_folder_name + "_PD_Punish_Data.csv"
    pd_initiate_filepath = exp_dir + "\\" + exp_folder_name + "_PD_MustInitiate_Data.csv"
    pd_touch_filepath = exp_dir + "\\" + exp_folder_name + "_PD_MustTouch_Data.csv"
    pd_initial_filepath = exp_dir + "\\" + exp_folder_name + "_PD_InitialTouch_Data.csv"
    pd_hab2_filepath = exp_dir + "\\" + exp_folder_name + "_PD_Habituation2_Data.csv"
    pd_hab1_filepath = exp_dir + "\\" + exp_folder_name + "_PD_Habituation1_Data.csv"
    pd_protocol_list = [pd_filepath,pd_acq_filepath,pd_punish_filepath,pd_initiate_filepath,pd_touch_filepath,pd_initial_filepath,pd_hab2_filepath,pd_hab1_filepath]

    for y in range(0,len(pd_protocol_list)):
        selected_filepath = pd_protocol_list[y]
        if os.stat(selected_filepath).st_size != 0:
            dateparse = lambda x: pd.datetime.strptime(x, '%Y-%m-%dT%H:%M:%S.%f ')
            total_data = pd.read_csv(selected_filepath)
            os.remove(selected_filepath)
            qc_animal_list = total_data['AnimalID'].tolist()
            qc_animal_list = list(set(qc_animal_list))

            for x in range(0, len(qc_animal_list)):
                active_animal_data = total_data.loc[total_data.AnimalID == qc_animal_list[x]]
                active_animal_date_list = active_animal_data['Date/Time'].tolist()
                active_animal_date_list = sorted(active_animal_date_list,
                                                 key=lambda x: datetime.datetime.strptime(x, '%m/%d/%Y%I:%M:%S%p'))
                for a in range(0, len(active_animal_date_list)):
                    total_data.loc[((total_data['AnimalID'] == qc_animal_list[x]) & (
                        total_data['Date/Time'] == active_animal_date_list[a])), 'Day'] = a + 1
                    week = int(math.ceil((a+1)/5))
                    total_data.loc[((total_data['AnimalID'] == qc_animal_list[x]) & (
                        total_data['Date/Time'] == active_animal_date_list[a])), 'Week'] = week

            total_data.to_csv(selected_filepath, index=False)


def QC_Overall(exp_dir):
    exp_path_list = exp_dir.split("\\")
    exp_folder_name = exp_path_list[(len(exp_path_list) - 1)]
    pd_filepath = exp_dir + "\\" + exp_folder_name + "_PD_Main_Data.csv"
    pd_acq_filepath = exp_dir + "\\" + exp_folder_name + "_PD_Acquisition_Data.csv"
    pd_punish_filepath = exp_dir + "\\" + exp_folder_name + "_PD_Punish_Data.csv"
    pd_initiate_filepath = exp_dir + "\\" + exp_folder_name + "_PD_MustInitiate_Data.csv"
    pd_touch_filepath = exp_dir + "\\" + exp_folder_name + "_PD_MustTouch_Data.csv"
    pd_initial_filepath = exp_dir + "\\" + exp_folder_name + "_PD_InitialTouch_Data.csv"
    pd_hab2_filepath = exp_dir + "\\" + exp_folder_name + "_PD_Habituation2_Data.csv"
    pd_hab1_filepath = exp_dir + "\\" + exp_folder_name + "_PD_Habituation1_Data.csv"
    pd_protocol_list = [pd_filepath,pd_acq_filepath,pd_punish_filepath,pd_initiate_filepath,pd_touch_filepath,pd_initial_filepath,pd_hab2_filepath,pd_hab1_filepath]

    return