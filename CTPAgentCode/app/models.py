from app import db

class Status(db.Model):
    __tablename__ = 'status'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(128),  unique=True)
    value = db.Column(db.String(128))

class Flag(db.Model):
    __tablename__='flags'
    id = db.Column(db.Integer, primary_key=True)
    flag=db.Column(db.Boolean)