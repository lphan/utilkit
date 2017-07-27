import pandas as pd

# import data from excel file (4 time slots 1993, 1995, 2013, 2016)
# Data can be updated manually via Excel-file & update import lines accordingly
try:
    hw = pd.ExcelFile('floodings.xlsx')
    hw1993 = hw.parse('HW1993')
    hw1995 = hw.parse('HW1995')
    hw2013 = hw.parse('HW2013')
    hw2016 = hw.parse('HW2016')

    hwall = hw1993.append(hw1995).append(hw2013).append(hw2016)
    MAX_LENGTH_IDX = 96    # calculated from 0:00 to 24:00, stepsize 15 minutes

except IOError as e:
    print ("Error import data from Excel file")
    import sys
    sys.exit()
