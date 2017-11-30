# -------------------------------------------- DECOMPRESSION PROGRAM -----------------------------------------------------------
#Input parameters are:
#  Collection
#  Internal object structure used in workflow
#  Action that will be applied on all files in Path : gunzip ( decompress .gz Files )
#Output parameter:
#  Status
# -------------------------------- TEIL1 : DECOMPRESS ONE FILE FROM INPUT PATH ------------------------------------------------
# gunzip will only decompress zip file. The other files wont be effected.
# After compression : Unlink and register new file in iCAT
# Beispiel : Unregister ./irm -r -U /tempZone2/home/irods/Archiv 
# And then : register new ./ireg -C /home/irobot/Desktop/iRODS/Vault/home/irods/Archiv /tempZone2/home/irods/Archiv

decompression1 {
  *Work=``{ 
	    msiGetObjectPath(*File,*obj,*status); 
	    msiSplitPath(*obj,*Collection,*Data); 
	    msiExecStrCondQuery("SELECT DATA_PATH where COLL_NAME = '*Collection' AND DATA_NAME like '*Data'",*F); 
	    foreach(*F){
	    	msiGetValByKey(*F,"DATA_PATH",*Path); 
	    	writeLine("stdout",*Path); 
		msiExecCmd("gunzip",*Path,"null","null","null",*Result); 
		writeLine("stdout","Decompression erledigt");		
	    	}
# VORSICHT : mit DATA_ID
#		msiGetValByKey(*F,"DATA_ID",*Id); 
#		writeLine("stdout",*Id);
# Beispiel : msiPhyPathReg(*DestCollection,*Resource,*SourceDirectory,"null",*Stat);
#		*DestCollection = substr("*obj",0,strlen(*obj)-3); 
#		*SourceDirectory = substr("*Path",0,strlen(*Path)-3);
#		msiPhyPathReg(*DestCollection,"StorageResc2",*SourceDirectory,"null",*Stat);
#		writeLine("stdout","The local collection *SourceDirectory is mounted under the logical collection *DestCollection");	   		
# Set back Data Type Name into generic 	
#		msiSetDataType(*DataID,*DestCollection,"generic",*Status);
         }``;
  msiCollectionSpider(*Coll,*File,*Work,*Status); 
  writeLine("stdout","Operations completed");
}
INPUT *Coll="/tempZone2/home/irods"
OUTPUT ruleExecOut

# --------------------------------- TEIL2 : DECOMPRESS ALL FILES USING DATABASE QUERY -----------------------------------------
#decompress2 {
#		msiExecStrCondQuery("SELECT DATA_NAME,DATA_PATH where COLL_NAME = '*Coll'",*F); 
#		foreach(*F) {
#			msiGetValByKey(*F,"DATA_NAME",*Name);
#			writeLine("stdout",*Name);
#			msiGetValByKey(*F,"DATA_PATH",*Path); 
#			msiExecCmd("gunzip",*Path,"null","null","null",*Result); 
#			writeLine("stdout","Unkomprimierung erfolgreich");
#		}
#		writeLine("stdout","Operation erledigt");
#}
#INPUT *Coll = "/tempZone2/home/irods%"
#OUTPUT ruleExecOut
