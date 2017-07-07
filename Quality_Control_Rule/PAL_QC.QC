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

    QC_Analysis_Names = ["PALAnalysis","PALAquisition","PALPunishIncor","PALMustInitiate","PALMustTouch","PALInitialTrain","PALHabit2","PALHabit1"]
    PAL_Main_Files = ['Mouse dPAL v3','Mouse sPAL v3','Mouse dPAL 1 v3','Mouse dPAL 2 v3','Mouse dPAL 3 v3','Mouse dPAL 4 v3','Mouse dPAL 5 v3','Mouse dPAL 6 Retention v3','Mouse dPAL 6 v3','Mouse sPAL 1 v3','Mouse sPAL v3','Mouse dPAL RETENTION 1 v3']
    PAL_Acq_Files = ['Mouse dPAL acquisition 1 v3','Mouse dPAL acquisition 2 v3','Mouse dPAL acquisition 3 v3','Mouse dPAL acquisition 4 v3','Mouse dPAL acquisition 5 v3','Mouse dPAL acquisition 6 v3','Mouse sPAL acquisition 1 v3','Mouse sPAL acquisition v3']
    PAL_Punish_Files = ['Mouse PAL Punish Incorrect Training v3 Jan2015MOD','Mouse PAL Punish Incorrect Training v3']
    PAL_Initiate_Files = ['Mouse PAL Must Initiate Training v3']
    PAL_Touch_Files = ['Mouse PAL Must Touch Training v3']
    PAL_Initial_Files = ['Mouse PAL Initial Touch Training v3']
    PAL_Habit2_Files = ['Mouse PAL Habituation 2 v2']
    PAL_Habit1_Files = ['Mouse PAL Habituation 1 v2']
    QC_Protocol_List = [PAL_Main_Files,PAL_Acq_Files,PAL_Punish_Files,PAL_Initiate_Files,PAL_Touch_Files,PAL_Initial_Files,PAL_Habit2_Files,PAL_Habit1_Files]
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
        if ((qc_session_time < 3599.99) or (qc_session_time == 'NA')) and ((qc_session_trials < 36) or (qc_session_trials == 'NA')):
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
        active_day_acq_results_list = dataframe_list[1]
        active_day_punish_results_list = dataframe_list[2]
        active_day_initiate_results_list = dataframe_list[3]
        active_day_touch_results_list = dataframe_list[4]
        active_day_initial_results_list = dataframe_list[5]
        active_day_habit2_results_list = dataframe_list[6]
        active_day_habit1_results_list = dataframe_list[7]

        if session_data['AnalysisName'].iat[0] == "PALAnalysis":
            if len(active_day_main_results_list) > 0:
                active_day_main_results_list.append(session_data)
            elif len(active_day_main_results_list) == 0:
                active_day_main_results_list = [session_data]
        if session_data['AnalysisName'].iat[0] == "PALAquisition":
            if len(active_day_acq_results_list) > 0:
                active_day_acq_results_list.append(session_data)
            elif len(active_day_acq_results_list) == 0:
                active_day_acq_results_list = [session_data]
        if session_data['AnalysisName'].iat[0] == "PALPunishIncor":
            if len(active_day_punish_results_list) > 0:
                active_day_punish_results_list.append(session_data)
            elif len(active_day_punish_results_list) == 0:
                active_day_punish_results_list = [session_data]
        if session_data['AnalysisName'].iat[0] == "PALMustInitiate":
            if len(active_day_initiate_results_list) > 0:
                active_day_initiate_results_list.append(session_data)
            elif len(active_day_initiate_results_list) == 0:
                active_day_initiate_results_list = [session_data]
        if session_data['AnalysisName'].iat[0] == "PALMustTouch":
            if len(active_day_touch_results_list) > 0:
                active_day_touch_results_list.append(session_data)
            elif len(active_day_touch_results_list) == 0:
                active_day_touch_results_list = [session_data]
        if session_data['AnalysisName'].iat[0] == "PALInitialTrain":
            if len(active_day_initial_results_list) > 0:
                active_day_initial_results_list.append(session_data)
            elif len(active_day_initial_results_list) == 0:
                active_day_initial_results_list = [session_data]
        if session_data['AnalysisName'].iat[0] == "PALHabit2":
            if len(active_day_habit2_results_list) > 0:
                active_day_habit2_results_list.append(session_data)
            elif len(active_day_habit2_results_list) == 0:
                active_day_habit2_results_list = [session_data]
        if session_data['AnalysisName'].iat[0] == "PALHabit1":
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

    QC_Analysis_Names = ["PALAnalysis", "PALAquisition", "PALPunishIncor", "PALMustInitiate", "PALMustTouch",
                         "PALInitialTrain", "PALHabit2", "PALHabit1"]

    pal_filepath = exp_dir + "\\" + exp_folder_name + "_PAL_Main_Data.csv"
    pal_acq_filepath = exp_dir + "\\" + exp_folder_name + "_PAL_Acquisition_Data.csv"
    pal_punish_filepath = exp_dir + "\\" + exp_folder_name + "_PAL_Punish_Data.csv"
    pal_initiate_filepath = exp_dir + "\\" + exp_folder_name + "_PAL_MustInitiate_Data.csv"
    pal_touch_filepath = exp_dir + "\\" + exp_folder_name + "_PAL_MustTouch_Data.csv"
    pal_initial_filepath = exp_dir + "\\" + exp_folder_name + "_PAL_InitialTouch_Data.csv"
    pal_hab2_filepath = exp_dir + "\\" + exp_folder_name + "_PAL_Habituation2_Data.csv"
    pal_hab1_filepath = exp_dir + "\\" + exp_folder_name + "_PAL_Habituation1_Data.csv"

    for dataframe in range(0,len(dataframe_list)):
        combined_data = dataframe_list[dataframe]
        combined_data = combined_data.loc[:,~combined_data.columns.duplicated()]

        if combined_data['AnalysisName'].iat[0] == QC_Analysis_Names[0]:
            if os.stat(pal_filepath).st_size != 0:
                pal_main_data_main = pd.read_csv(pal_filepath)
                pal_main_data_main = pd.concat([pal_main_data_main,combined_data], ignore_index = True, verify_integrity=True)
                pal_main_data_main.to_csv(pal_filepath, index=False)
            elif os.stat(pal_filepath).st_size == 0:
                combined_data.to_csv(pal_filepath, index=False)

        if combined_data['AnalysisName'].iat[0] == QC_Analysis_Names[1]:
            if os.stat(pal_acq_filepath).st_size != 0:
                pal_acq_data_acq = pd.read_csv(pal_acq_filepath)
                pal_acq_data_acq = pd.concat([pal_acq_data_acq,combined_data], ignore_index = True)
                pal_acq_data_acq.to_csv(pal_acq_filepath, index=False)
            elif os.stat(pal_acq_filepath).st_size == 0:
                combined_data.to_csv(pal_acq_filepath, index=False)

        if combined_data['AnalysisName'].iat[0] == QC_Analysis_Names[2]:
            if os.stat(pal_punish_filepath).st_size != 0:
                pal_punish_data_punish = pd.read_csv(pal_punish_filepath)
                pal_punish_data_punish = pd.concat([pal_punish_data_punish,combined_data], ignore_index = True)
                pal_punish_data_punish.to_csv(pal_punish_filepath, index=False)
            elif os.stat(pal_punish_filepath).st_size == 0:
                combined_data.to_csv(pal_punish_filepath, index=False)

        if combined_data['AnalysisName'].iat[0] == QC_Analysis_Names[3]:
            if os.stat(pal_initiate_filepath).st_size != 0:
                pal_initiate_data_initiate = pd.read_csv(pal_initiate_filepath)
                pal_initiate_data_initiate = pd.concat([pal_initiate_data_initiate,combined_data], ignore_index = True)
                pal_initiate_data_initiate.to_csv(pal_initiate_filepath, index=False)
            elif os.stat(pal_initiate_filepath).st_size == 0:
                combined_data.to_csv(pal_initiate_filepath, index=False)

        if combined_data['AnalysisName'].iat[0] == QC_Analysis_Names[4]:
            if os.stat(pal_touch_filepath).st_size != 0:
                pal_touch_data_touch = pd.read_csv(pal_touch_filepath)
                pal_touch_data_touch = pd.concat([pal_touch_data_touch,combined_data], ignore_index = True)
                pal_touch_data_touch.to_csv(pal_touch_filepath, index=False)
            elif os.stat(pal_touch_filepath).st_size == 0:
                combined_data.to_csv(pal_touch_filepath, index=False)

        if combined_data['AnalysisName'].iat[0] == QC_Analysis_Names[5]:
            if os.stat(pal_initial_filepath).st_size != 0:
                pal_initial_data_initial = pd.read_csv(pal_initial_filepath)
                pal_initial_data_initial = pd.concat([pal_initial_data_initial,combined_data], ignore_index = True)
                pal_initial_data_initial.to_csv(pal_initial_filepath, index=False)
            elif os.stat(pal_initial_filepath).st_size == 0:
                combined_data.to_csv(pal_initial_filepath, index=False)

        if combined_data['AnalysisName'].iat[0] == QC_Analysis_Names[6]:
            if os.stat(pal_hab2_filepath).st_size != 0:
                pal_hab2_data_hab2 = pd.read_csv(pal_hab2_filepath)
                pal_hab2_data_hab2 = pd.concat([pal_hab2_data_hab2,combined_data], ignore_index = True)
                pal_hab2_data_hab2.to_csv(pal_hab2_filepath, index=False)
            elif os.stat(pal_hab2_filepath).st_size == 0:
                combined_data.to_csv(pal_hab2_filepath, index=False)

        if combined_data['AnalysisName'].iat[0] == QC_Analysis_Names[7]:
            if os.stat(pal_hab1_filepath).st_size != 0:
                pal_hab1_data_hab1 = pd.read_csv(pal_hab1_filepath)
                pal_hab1_data_hab1 = pd.concat([pal_hab1_data_hab1,combined_data], ignore_index = True)
                pal_hab1_data_hab1.to_csv(pal_hab1_filepath, index=False)
            elif os.stat(pal_hab1_filepath).st_size == 0:
                combined_data.to_csv(pal_hab1_filepath, index=False)

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

    for y in range(0,len(pal_protocol_list)):
        selected_filepath = pal_protocol_list[y]
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
    pal_filepath = exp_dir + "\\" + exp_folder_name + "_PAL_Main_Data.csv"
    pal_acq_filepath = exp_dir + "\\" + exp_folder_name + "_PAL_Acquisition_Data.csv"
    pal_punish_filepath = exp_dir + "\\" + exp_folder_name + "_PAL_Punish_Data.csv"
    pal_initiate_filepath = exp_dir + "\\" + exp_folder_name + "_PAL_MustInitiate_Data.csv"
    pal_touch_filepath = exp_dir + "\\" + exp_folder_name + "_PAL_MustTouch_Data.csv"
    pal_initial_filepath = exp_dir + "\\" + exp_folder_name + "_PAL_InitialTouch_Data.csv"
    pal_hab2_filepath = exp_dir + "\\" + exp_folder_name + "_PAL_Habituation2_Data.csv"
    pal_hab1_filepath = exp_dir + "\\" + exp_folder_name + "_PAL_Habituation1_Data.csv"
    pal_protocol_list = [pal_filepath,pal_acq_filepath,pal_punish_filepath,pal_initiate_filepath,pal_touch_filepath,pal_initial_filepath,pal_hab2_filepath,pal_hab1_filepath]

    return