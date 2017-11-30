# Download all Zip File from INPUT
# Step 1: Check DATA_TYPE_NAME = 'ascii compressed Lempel-Ziv'
# Step 2: If TRUE then Download, else Error Message "Format of File is not Zip"
downloadZipFiles{
		msiExecStrCondQuery("SELECT COLL_NAME,DATA_NAME,DATA_TYPE_NAME where COLL_NAME like '*Coll' ",*Z);
		foreach(*Z) {
			# Get Data Type of Files
			msiGetValByKey(*Z,"DATA_TYPE_NAME",*Type);
			writeLine("stdout","2. Format Type is "++*Type);
			if (*Type=='ascii compressed Lempel-Ziv') {
				# Get Data_Name of file
				msiGetValByKey(*Z,"DATA_NAME",*Name);
				writeLine("stdout","1. File Name : "++*Name);
				msiGetValByKey(*Z,"COLL_NAME",*CollName);
				writeLine("stdout","2. Collection Path is"++*CollName);
				writeLine("stdout"," Zip Format. Begin to Download");
				*SourceFile = *CollName++"/"++*Name;
				writeLine("stdout","Hilfsvariable : "++*SourceFile);
				msiDataObjGet(*SourceFile,"localPath=*TargetLocal*Name++++forceFlag=",*Status);	
				writeLine("stdout"," Download File *Name finished");
			}
			else {
				writeLine("stdout"," File has another type : "++*Type++", so cannot download");
			}	
		}
		writeLine("stdout","Operation finished");
}
INPUT *Coll = "/tempZone2/home/irods%",*TargetLocal = "/home/irobot/Desktop/"
OUTPUT ruleExecOut
