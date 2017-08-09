import pandas as pd
from pathlib import Path
from pandas import read_csv
import datetime

# import data from excel file (4 time slots 1993, 1995, 2013, 2016)
# Data can be updated manually via Excel-file & update import lines accordingly
try:
    print ("Starting to import data ...\n")
    hw = pd.ExcelFile('floodings.xlsx')
    hw1993 = hw.parse('HW1993')
    hw1995 = hw.parse('HW1995')
    hw2013 = hw.parse('HW2013')
    hw2016 = hw.parse('HW2016')

    pathcsv = "./floodpred-wui/src/main/webapp/META-INF/data.csv"
    mf = Path(pathcsv)
    if mf.is_file():
        csv_data = read_csv(pathcsv, header=None).values
        hwall = hw1993.append(hw1995).append(hw2013).append(hw2016)
        # print (len(hwall))

        # Convert data from csv into Timestamp- and Datetime-format
        # and append new data to hwall
        # TODO: error 1 data point, can not run method 2
        for data in csv_data:
            timestamp = pd.Timestamp(data[0], tz=None)
            time = datetime.time(data[2])
            add_data = pd.DataFrame([[timestamp, time, data[1]]],
                                    columns=['Datum', 'Zeit', 'W [cm]'])

            hwall = hwall.append(add_data, ignore_index=True)

        # print (len(hwall))
        # print (hwall)
    else:
        hwall = hw1993.append(hw1995).append(hw2013).append(hw2016)

    MAX_LENGTH_IDX = 96    # calculated from 0:00 to 24:00, stepsize 15 minutes

except IOError as e:
    print ("Error import data from Excel file")
    import sys
    sys.exit()
