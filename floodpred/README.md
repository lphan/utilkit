
Flood prediction  
=
 
### Script Design
----------------- 
(1) floodings.xlsx
- This file contains the basic data measured, will be used for analyzing and prediction

(2) floodpred.py
- This file contains help-functions and visualization functions

(3) data.py
- This file contains import-data from excel

(4) predict.py
- This file contains core-function to predict waterlevel

(5) data.csv
- This file contains history parameters input, will be used for user interface

(6) dbconn.py 
- This file contains function to synchronize data from csv-file and database Mongo

(7) setup.py
- This file helps to install all dependencies

(8) floodpred.log
- This file contains basic log informations

(9) Folder Doc
- This folder contains documentations about this program

### Preparation
---------------

(1) Prerequisites:
- pip (check version of pip and upgrade it if possible)        
    > pip --version
    > pip install --upgrade pip

- it's recommended to test this script in virtual environment:
    > pip install virtualenv

(2) Dependencies:
- use virtualenv to create test environment:
    > virtualenv floodpred
- activate virtual environment:
    > . floodpred/bin/activate 
- install dependencies:
    > python setup.py install

### Run the script 
------------------
- Call program
    > python3 floodpred.py

- Update data between csv-file and Database
    > python3 dbconn.py
