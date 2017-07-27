
Flood prediction  
=
 
### Script Design
----------------- 
(1) floodings.xlsx
- This file contains the basic data measured, will be used for analyzing and prediction

(2) floodpred.py
- This file contains core-functions to parse excel file "floodings.xlsx"

(3) start.py
- This file is a start-script, contains parameters (path to textfile and save location), input by Users.

(4) setup.py
run this file first to install all dependencies

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
- Call CLI
    > python3 floodpred.py
