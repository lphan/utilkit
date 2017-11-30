# ---------------------------------------------------------------- Verschieben Ansatz  -------------------------------------------------------------
# Idee : User besitzt 2 StorageResc, braucht X freie Speicherkapazität bei Storage A (Quell), verschieben die Daten an Storage B(Desc) bis X erfüllt 
# ist oder nicht. 
# --------------------------------------------------------------------------------------------------------------------------------------------------
verschiebenansatz1 {
	*temp= 0;
#	Verbesserungsmöglich : die verschiebende Daten werden absteigend nach DATA_SIZE sortiert bevor sie verschoben werden.
	*I = 0;
	*ContInxOld = 1;
	*Condition = "COLL_NAME like '*Coll' AND RESC_NAME = '*QuellResource'";
	msiMakeGenQuery("COLL_NAME, order_desc(DATA_SIZE), DATA_NAME",*Condition,*GenQInp);
#	msiMakeGenQuery("COLL_NAME, DATA_SIZE, DATA_NAME",*Condition,*GenQInp);
	msiExecGenQuery(*GenQInp, *QR);
	msiGetContInxFromGenQueryOut(*QR,*ContInxNew);
	# Condition variable check if any rows still exist
	while(*ContInxOld > 0) {
		foreach(*QR) {
			msiGetValByKey(*QR,"DATA_SIZE",*Size);
			if ( *temp < *X ) {
				msiGetValByKey(*QR,"DATA_NAME",*Name);
				msiGetValByKey(*QR,"COLL_NAME",*Collname);
				*SourceFile = *Collname++"/"++*Name;
				msiDataObjPhymv(*SourceFile,*DescResource,*QuellResource,"0","null",*Status);
				writeLine("stdout","File *SourceFile mit Size *Size wurde von *QuellResource nach *DescResource verschoben");
				*temp = *temp + double(*Size);
				*I = *I + 1;
				# reduziert die Speicheranforderung um die nächste Daten für Verschieben effiziente auszuwählen. 
				# weil sich die Größe der verschobene Daten die freie Speicherkapazität entscheidet.
				# Vorteil über Komprimierung, die geschaffte Speicherkapazität von Komprimierung kann nicht vorhergesehen werden.
				# Auswahl der Daten anpassbar mit *X (zb. X = 5 , send D >= 5 )
				*Noch = *X - *temp;			
				writeLine("stdout","---> Speicheranforderung bleibt noch : *Noch ");
			}		
		}
		*ContInxOld = *ContInxNew;
		# get more rows in case data > 256 rows.
		if(*ContInxOld > 0) {msiGetMoreRows(*GenQInp,*QR,*ContInxNew);}
	}
	if (*temp >= *X) {
		writeLine("stdout","Erfolgreich, die freie Speicherkapazität *temp wurde geschafft ");
		writeLine("stdout","Anzahl der verschobene Dateien : *I");
		}
	else {
		writeLine("stdout","Leider nur *temp freie Speicherkapazität wurde geschafft.");
		writeLine("stdout","Anzahl der verschobene Dateien : *I");
		}
}
# Bewertung : Nachteil vom Ansatz ohne Sortierung : gewonne Speicherkapazität (*temp = 7349500 ) >> Speicheranforderung. (*X = 2000000) 
# Verbesserungsmöglichkeit : Sortieren, oder Verschieben die Daten mit bestimmten Eigenschaften ( nach Format, Size ) indem die SQL-Anfrage optimiert sind. zb. SELECT ... WHERE DATA_TYPE_NAME = '...' AND DATA_SIZE > ...	
# Nachteil von Sortierung : die Datei mit größten Größer ist >> Speicheranforderung. Das Ergebnis sowie die Leistung sind stark abhängig von der Eigenschaften gespeicherter Daten bzw. die Größe der gespeicherte Daten und die verschiebende Daten. Ein Algorithmus, die die Reihenfolge der verschiebende Dateien vorsortiert, ist in dem Fall nötig. Zb. Such die Datei mit der Größe nah an Speicheranforderung, die nächste verschobene Datei  
# QuellResource : wo man seine Daten speichern möchte und freie Speicherkapazität
# DescResource1 : wo man die Daten vom QuellRessource dahin verschieben will, um die freie Speicherkapazität zu schaffen.
# X : die freie Speicherkapazität die Nutzer braucht.
INPUT *Coll = "/tempZone2/home/irods%",*QuellResource = "FTPResc2",*DescResource = "StorageResc2",*X= 15000000
OUTPUT ruleExecOut
