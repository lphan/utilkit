# ----------------------------------------------------- Verschieben Ansatz 2 --------------------------------------------------------------------
# Idee : Einführung von Quota, ResourceGroup. Verwendungsansatz : Verschieben von Daten zwischen 2 StorageResc.					|
# Ggb. : User besitzt mehrere StorageResc, braucht X freie Speicherkapazität. 									|
# Quota bei allen Storage Ressource werden ermittelt. Welche StorageResc hat am meisten freie Speicherkapazität, wird ausgewählt. 		|	
# Falls X ausreicht, ok. Sonst, gewinn freier Speicherkapazität bei ausgewählten StorageRessource mit Verschiebensansatz, indem die Daten von	| 	  # ausgewählter  StorageRessource zu anderen Storage Ressource verschoben werden.								|
# -----------------------------------------------------------------------------------------------------------------------------------------------
verschiebenansatz2 {
# Überprüft die Zustände von Quota bei allen Storage Ressourcen
	writeLine("stdout","****** QuellResource   : *QuellResource ");
	writeLine("stdout","****** TargetResource1 : *TargetResource1 "); 
	writeLine("stdout","****** TargetResource2 : *TargetResource2 ");
	writeLine("stdout","------ Speicheranforderung : *X ");
	msiExecStrCondQuery("SELECT SUM(DATA_SIZE) where COLL_NAME like '*Coll' AND RESC_NAME = '*QuellResource' ",*QR);
	foreach(*QR) {
		msiGetValByKey(*QR,"DATA_SIZE",*QSize);
		if (*QSize =="") {
			writeLine("stdout","1. *QuellResource benutzte Speicherkapazität = 0 ");
		}
		else {
			writeLine("stdout","1. *QuellResource benutzte Speicherkapazität = "++*QSize);
		}
	}
	*Qfree = *QuotaQuellResc - double(*QSize);
	writeLine("stdout","---> *QuellResource freie Speicherkapazität = *Qfree");

	msiExecStrCondQuery("SELECT SUM(DATA_SIZE) where COLL_NAME like '*Coll' AND RESC_NAME = '*TargetResource1' ",*TR1);
	foreach(*TR1) {
		msiGetValByKey(*TR1,"DATA_SIZE",*TSize1);
		if (*TSize1 =="") {
			writeLine("stdout","2. *TargetResource1 benutzte Speicherkapazität = 0 ");
		}
		else {
			writeLine("stdout","2. *TargetResource1 benutzte Speicherkapazität =   "++*TSize1);
		}
	}
	*Tfree1 = *QuotaTargetResc1 - double(*TSize1);
	writeLine("stdout","---> *TargetResource1 freie Speicherkapazität = *Tfree1");

	msiExecStrCondQuery("SELECT SUM(DATA_SIZE) where COLL_NAME like '*Coll' AND RESC_NAME = '*TargetResource2' ",*TR2);
	foreach(*TR2) {
		msiGetValByKey(*TR2,"DATA_SIZE",*TSize2);
		if (*TSize2 =="") {
			writeLine("stdout","3. *TargetResource2 benutzte Speicherkapazität = 0 ");
		}
		else {
			writeLine("stdout","3. *TargetResource2 benutzte Speicherkapazität = "++*TSize2);
		}
	}
	*Tfree2 = *QuotaTargetResc2 - double(*TSize2);
	writeLine("stdout","---> *TargetResource2 freie Speicherkapazität = *Tfree2");
	
}

# QuellResource : wo man seine Daten speichern möchte und freie Speicherkapazität
# TargetResource1 und TargetResource2 : wo man die Daten vom QuellRessource dahin verschieben will, um die freie Speicherkapazität zu schaffen.
# Quota QuellResource : Quota usage of User. ./iquota zu sehen
# Quota TargetResource1 und TargetResource2 : Quota usage of User. ./iquota zu sehen
# X : die freie Speicherkapazität die Nutzer braucht.
# GridResc2 : 10 MB, StorageResc2 : 30Mb, FTPResc2 : 10MB 
INPUT *Coll = "/tempZone2/home/irods%",*QuellResource ="StorageResc2",*TargetResource1 = "FTPResc2",*TargetResource2 = "GridResc2",*QuotaQuellResc = 30000000,*QuotaTargetResc1 = 10000000,*QuotaTargetResc2 = 10000000,*X = 15000000
OUTPUT ruleExecOut
