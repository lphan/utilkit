#----------------------------- BASIS ANSATZ: DELETE ALL FILES FROM INPUT PATH -----------------------------
# Using: MikroService msiCollectionSpider, apply actions on all files in input-collection
# Extensition with other attributes NAME, FORMAT, SIZE, DATE into condition where ...
# Example : Select ... where DATA_NAME = '...' AND DATA_SIZE = '' AND DATA_TYPE_NAME = '' AND DATA_MODIFY_TIME = '' AND DATA_EXPIRY = '' usw.

basisansatz1 {
	  *Work=``{ 
	# Abfrage logische Adresse von Daten
		    msiGetObjectPath(*File,*obj,*status); 
	#	    writeLine("stdout","*obj");
	# Trennen Collection und Daten	
		    msiSplitPath(*obj,*Collection,*Data); 
		    writeLine("stdout","Collection is *Collection and file is *Data");
	# Abfrage an iCAT 
		    msiExecStrCondQuery("SELECT DATA_PATH where COLL_NAME = '*Collection' AND DATA_NAME like '*Data'",*F); 
	 	    foreach(*F){
			    msiGetValByKey(*F,"DATA_PATH",*Path); 
	# Gibt die vollständige physikalische Adresse von Daten aus.
			    writeLine("stdout",*Path); 
	# Delete all Files at resource *Resc

			    writeLine("stdout","Compression erledigt");
		    }	
		  }``;
	  msiCollectionSpider(*Coll,*File,*Work,*Status); 
	  writeLine("stdout","Operations completed");	
}
INPUT *Coll="/tempZone2/home/irods"
OUTPUT ruleExecOut
