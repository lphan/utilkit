import pandas as pd
import json
import pymongo
from pymongo import MongoClient
client = MongoClient('localhost:27017')
db = client.floodpred


# Load all data from csv-file, overwrite/ update the old data either
# Data in CSV-file is the origin data, data in database will be synchronized as
# a copy
def import_data(filepath):
    mg_client = pymongo.MongoClient('localhost', 27017)

    # database name
    db_name = mg_client['floodpred']

    # collection name
    # TODO: create collection name if it does not exist
    coll_name = 'floodpred'
    db_cm = db_name[coll_name]

    # clean up database before import data from csv
    db_cm.remove()

    # ------------- OLD-CODE (without using pandas):-----
    # import os
    # import csv
    # open csv file
    # cdir = os.path.dirname(__file__)
    # file_res = os.path.join(cdir, filepath)
    # read content of csv file
    # csvfile = open(file_res, 'r')
    # fieldnames = ("waterlevel", "start_time", "predict_hours",
    #               "imagepath", "date_time")
    # reader = csv.DictReader(csvfile, fieldnames)

    # insert json-data into mongodb
    # data = []
    # for line in reader:
    #     data.append(line)
    # ---------------------------------------------------

    # convert data into pandas data core frame
    data = pd.read_csv(filepath, header=None)

    print ("Insert data into MongoDB")
    # Convert directly from csv to json-data and insert to database
    for elem in data.values:
        temp = {'datetime': elem[0], 'waterlevel_now': elem[1],
                'start_time': elem[2], 'predict_hours': elem[3],
                'figure_name': elem[4], 'predict_result': elem[5],
                'artificial_result': elem[6]}
        df = pd.DataFrame([temp],
                          columns=['datetime', 'waterlevel_now', 'start_time',
                                   'predict_hours', 'figure_name',
                                   'predict_result', 'artificial_result'])
        data_json = json.loads(df.to_json(orient='records'))

        # insert json-data into database
        print (data_json)

        db_cm.insert(data_json)


# Read data from MongoDB out
def read_data():
    try:
        floodCol = db.floodpred.find()
        print ("\nQuerying data from MongoDB .....\n")
        for fl in floodCol:
            print (fl)

    except Exception as e:
        print (str(e))


if __name__ == "__main__":
    filepath = './wui/src/main/webapp/resources/data.csv'
    import_data(filepath)
    read_data()
