# Web User Interface

- Build:
	- modify pom.xml and build via Maven and IDE IntelliJ
	- deploy war-file created in target into application server Wildfly

- Done:
	- connect to Database and display result on Web page

- Todo:
	- pass parameters from Web Interface to Python-function via Web Service Interface

- Issues:
	- Jython only work with Python2, currently no update for Python3 -> Flask or Django is possibly the choice

	- Folder image is getting large, need to get it out of deployment of war-file, but need a way to call folder 'image' outside war-deployment, better to keep retrieving images from inside java-backend code. Currently JSF does not refresh new images


