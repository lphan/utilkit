# Compress only one File from first input Path
# Aufruf mit ./irule -l -F basisansatz.r
# -l : 
basisansatz{
# Split Collection und Daten from input	
	msiSplitPath(*Coll,*Collection,*Name); 
	writeLine("stdout","Collection is *Collection and file is *Name");
# Query data from iCAT Database
	msiExecStrCondQuery("SELECT DATA_SIZE,DATA_PATH,DATA_ID where COLL_NAME = '*Collection' AND DATA_NAME like '*Name'",*F);  	
        foreach (*F) {
		# Get Physical Path of file to compress
		msiGetValByKey(*F,"DATA_PATH",*Path); 
		writeLine("stdout","1. Physical Path is "++*Path);
		# Get Size of File before compressing
		msiGetValByKey(*F,"DATA_SIZE",*Size);
		writeLine("stdout","2. Original Size is "++*Size);
		# Make full iRODS Path of file	
		msiGetObjectPath(*Collection++"/"++*Name,*Ladress,*status);
		writeLine("stdout","3. iRODS Path is "++*Ladress);
		# DATA ID				
		msiGetValByKey(*F,"DATA_ID",*DataID);
		writeLine("stdout","4. DATA ID = "++*DataID++" ");			
		# Compress file				
		msiExecCmd("gzip",*Path,"null","null","null",*Result); 
		writeLine("stdout","Compression successfull");				
	}
	writeLine("stdout","********** BEGIN CHECK ZIP FILES ************");
	# Update new logical iRODS-Path
	*NewLadress = "*Ladress"++".gz";
	writeLine("stdout","-> New iRODS Path .gz : "++*NewLadress);
	# Update new physical Path 
	*NewPath = "*Path"++".gz";
	writeLine("stdout","-> New physical Path .gz : "++*NewPath);				
	# Register new file with *Ladress and *NewPath
	*NewZipName = "*Name"++".gz";
	writeLine("stdout","-> New Name .gz : "++*NewZipName);
	msiPhyPathReg(*NewLadress,*StorageResc,*NewPath,"null",*Stat);	
	# Set New Object ID - and then New Data Typ . Setting new DataTyp needs DATA ID 
	msiExecStrCondQuery("SELECT DATA_ID where COLL_NAME = '*Collection' AND DATA_NAME = '*NewZipName'",*ID);	
	foreach(*ID) {
		msiGetValByKey(*ID,"DATA_ID",*NewDataID);
		writeLine("stdout","-> New DATA ID = "++*NewDataID++" ");
		msiSetDataType(*NewDataID,*NewLadress,"ascii compressed Lempel-Ziv",*Status); 
		}
	# Query Size of new Zip-File from iCAT -> AND DATA_NAME ...
	msiExecStrCondQuery("SELECT DATA_SIZE where DATA_NAME = '*NewZipName' AND DATA_TYPE_NAME = 'ascii compressed Lempel-Ziv'",*Z);
	# Access Size of Zip-File after compressing
	foreach(*Z) {		
		msiGetValByKey(*Z,"DATA_SIZE",*ZipSize);
		writeLine("stdout","Zip Size is "++*ZipSize);					
		}
	*Win = double(*Size) - double(*ZipSize); 
	writeLine("stdout","Moment WIN Capacity is *Win");
}
INPUT *Coll = "/tempZone2/home/irods/StorageResc2/bigfile.big", *StorageResc = "StorageResc2"
OUTPUT ruleExecOut
