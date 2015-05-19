from app import db
from models import BlogPost


#only run drop_all() in test, when adding a new column, this will delete previous data.
#db.drop_all()

#create database and db tables
db.create_all()

# insert
db.session.add(BlogPost("Good","bulldog.jpg","I\'m good."))
db.session.add(BlogPost("AdminPage","bulldog.jpg","This better works!"))

# commit the changes
db.session.commit()
