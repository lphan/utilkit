# Download one Zip File from INPUT
# Step 1: Check DATA_TYPE_NAME = 'ascii compressed Lempel-Ziv'
# Step 2: If TRUE then Download, else Error Message "Format of File is not Zip"
downloadZipFiles{
		msiSplitPath(*SourceFile,*Coll,*File);
		msiExecStrCondQuery("SELECT DATA_TYPE_NAME where COLL_NAME = '*Coll' AND DATA_NAME = '*File'",*Z);
		foreach(*Z) {
			# Get Data_Name of file
			writeLine("stdout","1. File Name : "++*File);
			# Get Data Type of Files
			msiGetValByKey(*Z,"DATA_TYPE_NAME",*Type);
			writeLine("stdout","2. Format Type is "++*Type);
			if (*Type=='ascii compressed Lempel-Ziv') {
				writeLine("stdout"," Zip Format. Begin to Download");
				msiDataObjGet(*SourceFile,"localPath=*TargetLocal*File++++forceFlag=",*Status);	
			}
			else {
				writeLine("stdout"," File has another type : "++*Type++", so cannot download");
			}	
		}
		
}
INPUT *SourceFile = "/tempZone2/home/irods/maps.pdf.gz",*TargetLocal = "/home/irobot/Desktop/"
OUTPUT ruleExecOut
