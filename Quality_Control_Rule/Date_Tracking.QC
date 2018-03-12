import pandas as pd
import numpy as np
import datetime

def QC_DateTrack(exp_dir):
    tracking_path = exp_dir + "\\" + "Tracking_Data.csv"
    tracking_data = pd.read_csv(tracking_path)
    tracking_data = tracking_data.drop_duplicates()

    error_path = exp_dir + "\\" + "error_report.csv"

    qc_animal_list = tracking_data['AnimalID'].tolist()
    qc_animal_list = list(set(qc_animal_list))

    bad_file_list = list()

    for a in range(0,len(qc_animal_list)):
        active_id = qc_animal_list[a]
        temp_data = tracking_data[tracking_data['AnimalID'] == active_id]
        temp_dates = temp_data['Date/Time'].tolist()
        temp_dates = sorted(temp_dates,
                                         key=lambda x: datetime.datetime.strptime(x, '%m/%d/%Y%I:%M:%S%p'))
        temp_dates_formatted = [datetime.datetime.strptime(a,'%m/%d/%Y%I:%M:%S%p') for a in temp_dates]
        for b in range(0,len(temp_dates)):
            current_date = temp_dates_formatted[b]
            if b < (len(temp_dates) - 1):
                for c in range((b+1),len(temp_dates)):
                    check_date = temp_dates_formatted[c]
                    if current_date.date() == check_date.date():
                        current_filename = temp_data.loc[temp_data['Date/Time'] == temp_dates[b],'Filename'].to_string()
                        check_filename = temp_data.loc[temp_data['Date/Time'] == temp_dates[c],'Filename'].to_string()
                        bad_file_list.append(current_filename)
                        bad_file_list.append(check_filename)
    if len(bad_file_list) > 0:
        for a in range(0,len(bad_file_list)):

