# -------------------------------------------------------- Löschen Replikation Ansatz  -------------------------------------------------------------
# Basisansatz vom Löschen : Algorithmen läuft ähnlich wie bei der Komprimierungsansatz.
# Idee Erweiterungsansatz 1: Einführung von neuen Metadaten "REPLICATION". 
# Überprüfung von Replikation. Wenn Replikation > 0, wird Replikation reduziert. Sonst, können die Daten wegen Datenverlust nicht gelöscht werden.
# Die Anzahl der Replikation ist = Anzahl der gebundene Ressourcen. 
# ***** Szenario : ***** 
# Benutzer möchte freie Speicherkapazität am StorageResource sogenannte zb. StorageResc2 gewinnen. Alle Dateien in diesem StorageResc2 besitzt schon eine  # Replikation in anderen Ressource zb. FTPResc2, werden gelöscht. Der Datenverlust kann vermeiden, weil eine Kopie von der Datei in Ressource FTPResc2 schon gesichert wird.
# ********************************* Beispiel - Replikation Bedingung : gleiche Name aber in anderer Ressource ***********************************
# Ablauf vom Programm : Alle Daten werden überprüft ob es eine Replikation woanders (andere Ressource) liegt.
# ---------------------------------------------------------------------------------------------------------------------------------------------------
deleteReplikation {	
	*Sum = 0;
	*i = 0;
	*ContInxOld = 1;
	# Query all file at StorageResc
	*Condition = "COLL_NAME like '*Coll' AND DATA_REPL_NUM > '0'"; 
	msiMakeGenQuery("COLL_NAME,DATA_NAME,DATA_SIZE",*Condition,*GenQInp);
	msiExecGenQuery(*GenQInp, *F);
	msiGetContInxFromGenQueryOut(*F,*ContInxNew);
	# Condition variable check if any rows still exist
	while(*ContInxOld > 0) {	
		foreach(*F) {
			msiGetValByKey(*F,"DATA_NAME",*Name1);
			msiGetValByKey(*F,"COLL_NAME",*CollName1);
			*SourceFile=*CollName1++"/"++*Name1;
			msiExecStrCondQuery("SELECT RESC_NAME where COLL_NAME = '*CollName1' AND DATA_NAME ='*Name1' AND DATA_REPL_NUM = '1'",*R);
				foreach(*R) {
					msiGetValByKey(*R,"RESC_NAME",*Resource);
					writeLine("stdout","File with Namme *Name1 has copy at *Resource");				
				}
			writeLine("stdout","---> The file *Name1 at *StorageResc is deleted");
			msiDataObjTrim(*SourceFile,*StorageResc,"null","1","null",*Status);
			msiGetValByKey(*F,"DATA_SIZE",*Size1);
			writeLine("stdout","---> Win free memory : *Size");
			*i = *i + 1;
			*Sum = *Sum + double(*Size);				
		}
	# New Value for variable ContInxOld
	*ContInxOld = *ContInxNew;
	# get more rows in case data > 256 rows.
	if(*ContInxOld > 0) {msiGetMoreRows(*GenQInp,*F,*ContInxNew);}
	}
	writeLine("stdout","Sum of deleted files : *i");
	writeLine("stdout","Sum of free memory : *Sum Byte");
}
#Resc1 : wo man freie Speicherkapazität braucht.
INPUT *Coll = "/tempZone2/home/irods%",*StorageResc = "StorageResc2"
OUTPUT ruleExecOut
