from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(600), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=False)
    shows = db.relationship("Show",backref='venues', lazy=True)
    genres = db.Column(db.String(120), nullable=False)
    num_upcoming_shows = db.Column(db.Integer, default=0)
    website = db.Column(db.String(120), nullable=False)
    seeking_talent = db.Column(db.Boolean, nullable=False)
    seeking_description = db.Column(db.String(255), nullable=True)



class Artist(db.Model):
    __tablename__ = 'artists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(600), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=False)
    shows = db.relationship("Show", backref="artists", lazy=True)
    num_upcoming_shows = db.Column(db.Integer, default=0)
    website = db.Column(db.String(120), nullable=False)
    seeking_venue = db.Column(db.Boolean, nullable=False)
    seeking_description = db.Column(db.String(255), nullable=True)



# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__="shows"
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), primary_key=True)
    start_time=db.Column(db.DateTime, primary_key=True)
