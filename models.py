from app import db
import datetime
from datetime import date

class BlogPost(db.Model):

    __tablename__ = "posts"
    __table_args__ = {'extend_existing':True}

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    pub_date = db.Column(db.Date)
    img_url = db.Column(db.Text)
    content = db.Column(db.Text, nullable=False)


    def __init__(self, title, img_url, content, pub_date=None):
        self.title = title
        if pub_date is None:
            pub_date = datetime.date.today()
        self.pub_date = pub_date
        self.img_url = img_url
        self.content = content


    def __repr__(self):
        return '<{}>'.format(self.title)


