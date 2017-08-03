import pandas as pd
import pymongo
import json
import os
import csv


def import_content(filepath):
    mg_client = pymongo.MongoClient('localhost', 27017)

    # database name
    db_name = mg_client['floodpred']

    # collection name
    coll_name = 'floodpred'
    db_cm = db_name[coll_name]
    cdir = os.path.dirname(__file__)
    file_res = os.path.join(cdir, filepath)

    csvfile = open(file_res, 'r')
    fieldnames = ("waterlevel", "start_time", "predict_hours",
                  "imagepath", "date_time")
    reader = csv.DictReader(csvfile, fieldnames)

    # insert json-data into mongodb
    data = []
    for line in reader:
        data.append(line)

    # convert data into pandas data core frame
    df = pd.DataFrame(data)

    # convert pandas_data into json-data
    data_json = json.loads(df.to_json(orient='records'))
    db_cm.remove()

    # insert json-data into database
    db_cm.insert(data_json)

if __name__ == "__main__":
    filepath = 'floodpred-wui/src/main/java/META-INF/data.csv'
    import_content(filepath)
