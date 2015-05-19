A blog with a CRUD admin page.





------------------config settings------------------

DataBase setting for local run:
app.config["SQLALCHEMY_DATABASE_URI"] 
	= 'mysql+pymysql://root:password@localhost:3306/bts'

*should pip install pymysql for the python mysql driver.




>> import models << should come after db=SQLAlchemy(app).