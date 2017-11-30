# ---------------------------------------- VERBESSERUNG zu VERSCHIEBENANSATZ 2 -------------------------------------
# Idee : Sortiert die Daten absteigend nach DATA_SIZE. Die Daten werden abwechselnd zwischen 2 Resourcen verschoben. 
# 						Anwendung : QUOTA
# ------------------------------------------------------------------------------------------------------------------
verschiebenansatz2 {
# Phase 1 : Überprüft die Zustände von Quota bei allen Storage Ressourcen
	writeLine("stdout","Speicheranforderung : *X");
	msiExecStrCondQuery("SELECT SUM(DATA_SIZE) where COLL_NAME like '*Resc' AND RESC_NAME = '*QuellResource' ",*QR);
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

	msiExecStrCondQuery("SELECT SUM(DATA_SIZE) where COLL_NAME like '*Resc' AND RESC_NAME = '*TargetResource1' ",*TR1);
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

	msiExecStrCondQuery("SELECT SUM(DATA_SIZE) where COLL_NAME like '*Resc' AND RESC_NAME = '*TargetResource2' ",*TR2);
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

	*temp= 0;
	*sumfile1= 0; 
	*sumfile2= 0; 
	*i1 = 0;
	*i2 = 0;

# Phase 2 : Verschieben die Daten an 2 Target-Ressourcen.
# VERBESSERUNG zu Ansatz1 : Die Daten werden nach DATA_SIZE ABSTEIGEND SORTIERT. Außerdem die Bedingung Tfree1 >= 0 und Tfree2 >= 0 kann abwechsel zwischen 2 TargetResource auswählen. Damit können mehrere Dateien von QuellResource an ZielTargetResc1 und TargetResc2 verschoben -> mehr Speicherplatz schaffen.
#Fehler Query -> msiExecStrCondQuery("SELECT COLL_NAME,DATA_NAME,order_desc(DATA_SIZE) where COLL_NAME like '*Coll' AND RESC_NAME = '*QuellResource'",*T1);
	*ContInxOld = 1;
	*Condition = "COLL_NAME like '*Coll' AND RESC_NAME = '*QuellResource'";
	msiMakeGenQuery("COLL_NAME, order_desc(DATA_SIZE), DATA_NAME",*Condition,*GenQInp);
	msiExecGenQuery(*GenQInp, *T1);
	msiGetContInxFromGenQueryOut(*T1,*ContInxNew);
	# Condition variable check if any rows still exist

	if ( *Tfree1 > *Tfree2 ) {
		writeLine("stdout","----------------------------- Beginne mit TargetResource 1 ------------------------------");
		while(*ContInxOld > 0) {
			foreach(*T1) {
				msiGetValByKey(*T1,"DATA_NAME",*Name);
				msiGetValByKey(*T1,"COLL_NAME",*Collname);
				msiGetValByKey(*T1,"DATA_SIZE",*Size);
			# -------------------- VERBESSERUNG zu Ansatz2 (vermeidet Überlastung von Quota) : *Tfree1 >= double(*Size) 
					if ( *temp < *X && *Tfree1 > 0 ) {
											
			#----------------------------------------------------------------------------------------------------------			
						*SourceFile = *Collname++"/"++*Name;
						msiDataObjPhymv(*SourceFile,*TargetResource1,*QuellResource,"0","null",*Status);
						writeLine("stdout","Die Datei *SourceFile ist schon an StorageResource *TargetResource1 verschoben");
						*temp = *temp + double(*Size);
						*Tfree1 = *Tfree1 - double(*Size);
						writeLine("stdout","--> Win: *Size");
						writeLine("stdout","--> Sum: *temp");
						writeLine("stdout","--> TargetResource1 noch : *Tfree1");
						*sumfile1 = *sumfile1 + double(*Size);
						*i1 = *i1 + 1;
					} 
					else if ( *temp < *X && *Tfree2 > 0 ) {
						# Verschieben Daten an TargetResource2			
						*SourceFile = *Collname++"/"++*Name;
						msiDataObjPhymv(*SourceFile,*TargetResource2,*QuellResource,"0","null",*Status);
						writeLine("stdout","Die Datei *SourceFile ist schon an StorageResource *TargetResource2 verschoben");
						*temp = *temp + double(*Size);
						*Tfree2 = *Tfree2 - double(*Size);
						writeLine("stdout","--> Win: *Size");
						writeLine("stdout","--> Sum: *temp");
						writeLine("stdout","--> TargetResource2 noch : *Tfree2");
						*sumfile2 = *sumfile2 + double(*Size);
						*i2 = *i2 + 1;
				}
			}
		*ContInxOld = *ContInxNew;
		# get more rows in case data > 256 rows.
		if(*ContInxOld > 0) {msiGetMoreRows(*GenQInp,*T1,*ContInxNew);}	
		}			
	} 
	else {
		writeLine("stdout","----------------------------- Beginne mit TargetResource 2 ------------------------------");
		while(*ContInxOld > 0) {
			foreach(*T1) {
				msiGetValByKey(*T1,"DATA_NAME",*Name);
				msiGetValByKey(*T1,"COLL_NAME",*Collname);
				msiGetValByKey(*T1,"DATA_SIZE",*Size);
				if ( *temp < *X && *Tfree2 > 0 ) {
						# Verschieben Daten an TargetResource2	
						*SourceFile = *Collname++"/"++*Name;
						msiDataObjPhymv(*SourceFile,*TargetResource2,*QuellResource,"0","null",*Status);
						writeLine("stdout","Die Datei *SourceFile ist schon an StorageResource *TargetResource2 verschoben");
						*temp = *temp + double(*Size);
						*Tfree2 = *Tfree2 - double(*Size);
						*sumfile2 = *sumfile2 + double(*Size);
						*i2 = *i2 + 1;	
						writeLine("stdout","--> Win: *Size");
						writeLine("stdout","--> Sum: *temp");
						writeLine("stdout","--> TargetResource2 noch : *Tfree2");				
				} 
				else if ( *temp < *X && *Tfree1 > 0 ) {
						# Verschieben Daten an TargetResource1
						*SourceFile = *Collname++"/"++*Name;
						msiDataObjPhymv(*SourceFile,*TargetResource1,*QuellResource,"0","null",*Status);
						writeLine("stdout","Die Datei *SourceFile ist schon an StorageResource *TargetResource1 verschoben");
						*temp = *temp + double(*Size);
						*Tfree1 = *Tfree1 - double(*Size);
						writeLine("stdout","--> Win: *Size");
						writeLine("stdout","--> Sum: *temp");
						writeLine("stdout","--> TargetResource1 noch : *Tfree1");
						*sumfile1 = *sumfile1 + double(*Size);
						*i1 = *i1 + 1;	
				}
			}
		*ContInxOld = *ContInxNew;
		# get more rows in case data > 256 rows.
		if(*ContInxOld > 0) {msiGetMoreRows(*GenQInp,*T1,*ContInxNew);}	
		}			
	}
	if (*temp >= *X) {
		writeLine("stdout","die freie Speicherkapazität *temp wurde geschafft ");
		writeLine("stdout","insgesamt : *sumfile1 an *TargetResource1 verschoben ");
		writeLine("stdout","insgesamt : *sumfile2 an *TargetResource2 verschoben ");
		writeLine("stdout","die Anzahl der verschobene Dateien an *TargetResource1 ist *i1, an *TargetResource2 ist *i2 ");
		}
	else {
		writeLine("stdout","Leider wurde nur *temp freie Speicherkapazität geschafft.");
		writeLine("stdout","insgesamt : *sumfile1 an *TargetResource1 verschoben ");
		writeLine("stdout","insgesamt : *sumfile2 an *TargetResource2 verschoben ");
		writeLine("stdout","die Anzahl der verschobene Dateien an *TargetResource1 ist *i1, an *TargetResource2 ist *i2 ");
	}
}

INPUT *Resc = "/tempZone2/home/irods%",*Coll = "/tempZone2/home/irods/StorageResc2/Storage1%",*QuellResource ="StorageResc2",*TargetResource1 = "FTPResc2",*TargetResource2 = "GridResc2",*QuotaQuellResc = 30000000,*QuotaTargetResc1 = 10000000,*QuotaTargetResc2 = 10000000,*X = 14000000
OUTPUT ruleExecOut
