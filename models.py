from peewee import Model, CharField, IntegerField, TextField, DateTimeField, ForeignKeyField
import datetime
from flask_login import UserMixin
from peewee import MySQLDatabase

db = MySQLDatabase(
    'notes_app',
    host='localhost',
    port=3306,  # Default MySQL port
    user='notes',
    password='qwe123'
)

class BaseModel(Model):
    class Meta:
        database = db
        
class MyUser(UserMixin, BaseModel):
    username = CharField(max_length=255, null=False, unique=True)
    email = CharField(max_length=255, null=False, unique=True)
    age = IntegerField()
    full_name = CharField(max_length=255, null=True)
    password = CharField(max_length=255, null=False)
    
class Note(BaseModel):
    user = ForeignKeyField(MyUser, backref='notes')
    note_text = TextField()
    created_date = DateTimeField(default=datetime.datetime.now)
    note_color = CharField(max_length=255, null=True)

class Card(BaseModel):
    user = ForeignKeyField(MyUser, backref='cards')
    title = CharField(max_length=255, null=False)
    description = CharField(max_length=255, null=False)
    created_date = DateTimeField(default=datetime.datetime.now)

db.create_tables([MyUser, Note, Card])
