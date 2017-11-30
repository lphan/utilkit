# ----------------------------------------------------- List File Ressource -------------------------------------------------------------------- #
# 																		 |
# ---------------------------------------------------------------------------------------------------------------------------------------------- #
basisansatz2 {
	# Abfrage an iCAT 
	*i = 0;
	*ContInxOld = 1;
	*Condition = "COLL_NAME like '*Coll' AND RESC_NAME = '*StorageResc'";
	msiMakeGenQuery("DATA_PATH, DATA_SIZE, DATA_NAME",*Condition,*GenQInp);
	msiExecGenQuery(*GenQInp, *GenQOut);
	msiGetContInxFromGenQueryOut(*GenQOut,*ContInxNew);
	# Condition variable check if any rows still exist
	while(*ContInxOld > 0) {
	  	foreach(*GenQOut) {
			msiGetValByKey(*GenQOut, "DATA_NAME", *Name);
			writeLine("stdout","Name : *Name");
			msiGetValByKey(*GenQOut, "DATA_PATH", *Path);
			writeLine("stdout","*Path");
			msiGetValByKey(*GenQOut, "DATA_SIZE", *Fsize);
			writeLine("stdout","-> Size : *Fsize");
			*i = *i +1;
	    	}
		*ContInxOld = *ContInxNew;
		# get more rows in case data > 256 rows.
		if(*ContInxOld > 0) {msiGetMoreRows(*GenQInp,*GenQOut,*ContInxNew);}
  	}
	writeLine("stdout","Insgesamt : *i Dateien ");
	writeLine("stdout","Operation erledigt");
}
INPUT *Coll = "/tempZone2/home/irods%", *StorageResc = "FTPResc2"
OUTPUT ruleExecOut
