# ---------------------------------------------------------------- Verschieben Ansatz  -------------------------------------------------------------
# Idee : User besitzt 2 StorageResc, braucht die freie Speicherkapazität bei Storage A (Quell), werden alle Daten von Storage A an Storage B(Desc) verschoben.
# --------------------------------------------------------------------------------------------------------------------------------------------------
verschiebenansatz {
	*temp= 0;
	*I = 0;
	*ContInxOld = 1;
	*Condition = "COLL_NAME like '*Coll' AND RESC_NAME = '*QuellResource'";
	msiMakeGenQuery("COLL_NAME, DATA_SIZE, DATA_NAME",*Condition,*GenQInp);
	msiExecGenQuery(*GenQInp, *QR);
	msiGetContInxFromGenQueryOut(*QR,*ContInxNew);
	# Condition variable check if any rows still exist
	while(*ContInxOld > 0) {
		foreach(*QR) {
			msiGetValByKey(*QR,"DATA_SIZE",*Size);
			msiGetValByKey(*QR,"DATA_NAME",*Name);
			msiGetValByKey(*QR,"COLL_NAME",*Collname);
			*SourceFile = *Collname++"/"++*Name;
			msiDataObjPhymv(*SourceFile,*DescResource,*QuellResource,"0","null",*Status);
			writeLine("stdout","File *SourceFile mit Size *Size wurde von *QuellResource nach *DescResource verschoben");
			*temp = *temp + double(*Size);
			*I = *I + 1;		
		}
		*ContInxOld = *ContInxNew;
		# get more rows in case data > 256 rows.
		if(*ContInxOld > 0) {msiGetMoreRows(*GenQInp,*QR,*ContInxNew);}
	}
	writeLine("stdout","Erfolgreich, die freie Speicherkapazität *temp wurde geschafft ");
	writeLine("stdout","Anzahl der verschobene Dateien : *I");
}

# Bewertung : Nachteil vom Ansatz ohne Sortierung : gewonne Speicherkapazität (*temp = 7349500 ) >> Speicheranforderung. (*X = 2000000) 
# Verbesserungsmöglichkeit : Sortieren, oder Verschieben die Daten mit bestimmten Eigenschaften ( nach Format, Size ) indem die SQL-Anfrage optimiert sind. zb. SELECT ... WHERE DATA_TYPE_NAME = '...' AND DATA_SIZE > ...	
# Nachteil von Sortierung : die Datei mit größten Größer ist >> Speicheranforderung. Das Ergebnis sowie die Leistung sind stark abhängig von der Eigenschaften gespeicherter Daten bzw. die Größe der gespeicherte Daten und die verschiebende Daten. Ein Algorithmus, die die Reihenfolge der verschiebende Dateien vorsortiert, ist in dem Fall nötig. Zb. Such die Datei mit der Größe nah an Speicheranforderung, die nächste verschobene Datei  
# QuellResource : wo man seine Daten speichern möchte und freie Speicherkapazität
# DescResource1 : wo man die Daten vom QuellRessource dahin verschieben will, um die freie Speicherkapazität zu schaffen.
# X : die freie Speicherkapazität die Nutzer braucht.
INPUT *Coll = "/tempZone2/home/irods%",*QuellResource = "FTPResc2",*DescResource = "StorageResc2"
OUTPUT ruleExecOut
