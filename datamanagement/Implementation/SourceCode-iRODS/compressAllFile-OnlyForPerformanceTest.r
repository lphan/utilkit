# -------------------------------------------------------------------------------------------------------------------------------------------- 
# 							Basis Ansatz mit Datenbank
# 						Compress all files in hierarchical Collection at one Storage Resource.
# Extensition with other attributes NAME, FORMAT, SIZE, DATE into condition where ...
# Example : Select ... where DATA_NAME = '...' AND DATA_SIZE = '' AND DATA_TYPE_NAME = '' AND DATA_MODIFY_TIME = '' AND DATA_EXPIRY = '' usw.
# -------------------------------------------------------------------------------------------------------------------------------------------- 
basisansatz2 {
	# Sum ist Gewinn von freier Speicherkapazität.
	*Sum = 0;
	# Anzahl der an die Komprimierungsprozess teilgenommene Dateien
	*I = 0;
	# Abfrage an iCAT 
	*ContInxOld = 1;
	*Condition = "COLL_NAME like '*Coll' AND RESC_NAME = '*StorageResc'";
	msiMakeGenQuery("COLL_NAME,DATA_PATH,DATA_SIZE,DATA_NAME,DATA_ID",*Condition,*GenQInp);
	msiExecGenQuery(*GenQInp, *GenQOut);
	msiGetContInxFromGenQueryOut(*GenQOut,*ContInxNew);
	# Condition variable check if any rows still exist
	while(*ContInxOld > 0) {
	  	foreach(*GenQOut) {
			msiGetValByKey(*GenQOut, "DATA_NAME", *Name);
			writeLine("stdout","Name : *Name");
			# Make full iRODS Path of file
			msiGetValByKey(*GenQOut, "COLL_NAME", *Collection);	
			msiGetObjectPath(*Collection++"/"++*Name,*Ladress,*status);
			writeLine("stdout","-> iRODS Path is "++*Ladress);
			# Physical Path
			msiGetValByKey(*GenQOut, "DATA_PATH", *Path);
			writeLine("stdout","-> *Path");
			# Size
			msiGetValByKey(*GenQOut, "DATA_SIZE", *Size);
			writeLine("stdout","-> Size : *Size");
			# DATA ID				
			msiGetValByKey(*GenQOut,"DATA_ID",*DataID);
			writeLine("stdout","-> DATA ID = "++*DataID++" ");
			msiExecCmd("gzip",*Path,"null","null","null",*Result); 
			writeLine("stdout","Compression successful");
			# sum of executed file
			*I = *I + 1;
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
			# Update *Sum as Win the free capacity. 
			*Sum = *Sum + *Win;
			writeLine("stdout","WIN Free Capacity is *Sum");
			writeLine("stdout"," --------------------------------------------- " );
		    	}
		*ContInxOld = *ContInxNew;
		# get more rows in case data > 256 rows.
		if(*ContInxOld > 0) {msiGetMoreRows(*GenQInp,*GenQOut,*ContInxNew);}
  	}
	writeLine("stdout","The number of .gz compressed files is : *I");
	writeLine("stdout","Operation erledigt");
}
INPUT *Coll = "/tempZone2/home/irods/FTPResc2%", *StorageResc = "FTPResc2"
OUTPUT ruleExecOut
