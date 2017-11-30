# -------------------------------------------- 2.Verbesserung vom Basisansatz. ----------------------------------------------------------
# | 			Speicheranforderung X wird angegeben. Die Komprimierung findet statt bis X erfüllt wird.			|
# |			Ergänzung : mit Sortieren. Idee ist : Select order_desc(DATA_SIZE) 						|
# -------------------------------------------------------------------------------------------------------------------------------------
verbesserungsansatz2{
	# Sum ist Gewinn von freier Speicherkapazität.
	*Sum = 0;
	# Anzahl der an die Komprimierungsprozess teilgenommene Dateien
	*I = 0;
	#msiExecStrCondQuery("SELECT COLL_NAME,DATA_ID,DATA_NAME,DATA_SIZE,DATA_PATH where COLL_NAME like '*Coll' AND RESC_NAME = '*StorageResource'",*F);
	*ContInxOld = 1;
	*Condition = "COLL_NAME like '*Coll' AND RESC_NAME = '*StorageResc'";
	msiMakeGenQuery("COLL_NAME,DATA_PATH,order_desc(DATA_SIZE),DATA_NAME,DATA_ID",*Condition,*GenQInp);
	msiExecGenQuery(*GenQInp, *F);
	msiGetContInxFromGenQueryOut(*F,*ContInxNew);
	# Condition variable check if any rows still exist
	while(*ContInxOld > 0) {
		foreach(*F) {
			# If Sum < Request of capacity, files from Path *Coll will be compressed
			if (*Sum < *X ) { 
				# Get Data_Name of file
				msiGetValByKey(*F,"DATA_NAME",*Name);
				writeLine("stdout","1. DATA NAME is "++*Name);
				# Get Physical Path of file to compress
				msiGetValByKey(*F,"DATA_PATH",*Path); 
				writeLine("stdout","2. Physical Path is "++*Path);
				# Get Size of File before compressing
				msiGetValByKey(*F,"DATA_SIZE",*Size);
				writeLine("stdout","3. Original Size is "++*Size);
				# Get iRODS Path of Collection saving file
				msiGetValByKey(*F,"COLL_NAME",*CollName);
				writeLine("stdout","4. Collection Path is"++*CollName);
				# Make full iRODS Path of file	
				msiGetObjectPath(*CollName++"/"++*Name,*Ladress,*status);
				writeLine("stdout","5. iRODS Path is "++*Ladress);
				# DATA ID				
				msiGetValByKey(*F,"DATA_ID",*DataID);
				writeLine("stdout","6. DATA ID = "++*DataID++" ");			
				msiExecCmd("gzip",*Path,"null","null","null",*Result); 
				writeLine("stdout","Komprimierung erfolgreich");
				# sum of executed file
				*I = *I + 1;
# Unlink old file ( must be done with manually with ./irm -r -U iRodsPath ) -> ??????						
				writeLine("stdout","********** BEGIN CHECK ZIP FILES ************");
				# Update new logical iRODS-Path
				*NewLadress = *Ladress++".gz";
				writeLine("stdout","5.1 New iRODS Path .gz : "++*NewLadress);
				# Update new physical Path 
				*NewPath = *Path++".gz";
				writeLine("stdout","2.1 New physical Path .gz :" ++*NewPath);				
				# Register new file with *Ladress and *NewPath
				msiPhyPathReg(*NewLadress,*StorageResc,*NewPath,"null",*Stat);
				*NewZipName = "*Name"++".gz";
				writeLine("stdout","1.2 New Name .gz :" ++*NewZipName);
				# Set New Object ID - and then New Data Typ . 3. HIER Problem ist OBJECT ID 
				msiExecStrCondQuery("SELECT DATA_ID where COLL_NAME = '*CollName' AND DATA_NAME = '*NewZipName'",*ID);	
				foreach(*ID) {
					msiGetValByKey(*ID,"DATA_ID",*NewDataID);
					writeLine("stdout","6.2 New DATA ID = "++*NewDataID++" ");
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
		}
		# New Value for variable ContInxOld
		*ContInxOld = *ContInxNew;
		# get more rows in case data > 256 rows.
		if(*ContInxOld > 0) {msiGetMoreRows(*GenQInp,*F,*ContInxNew);}
	}
	writeLine("stdout","Operation finished. Summary Result :");
	if (*Sum < *X) {
		writeLine("stdout","Sorry, just got *Sum Byte free memory capacity");
		writeLine("stdout","The number of .gz compressed files is : *I");
		}
	else {
		writeLine("stdout","Erfolgreiche Komprimierung, *Sum freie Speicherkapazität !!!");
		writeLine("stdout","The number of .gz compressed files is : *I");
	}
}
INPUT *Coll = "/tempZone2/home/irods/FTPResc2%",*StorageResc = "FTPResc2",*X = 1500000
OUTPUT ruleExecOut
