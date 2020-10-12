#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
from datetime import *
from wtforms.validators import ValidationError



#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

# TODO: connect to a local postgresql database
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
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=False)
    shows = db.relationship("Show",backref='venues', lazy=True)
    genres = db.Column(db.String(120), nullable=False)
    num_upcoming_shows = db.Column(db.Integer, default=0)
    website = db.Column(db.String(120), nullable=True)
    seeking_talent = db.Column(db.Boolean, nullable=True)
    seeking_description = db.Column(db.String(255), nullable=True)



class Artist(db.Model):
    __tablename__ = 'artists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=False)
    shows = db.relationship("Show", backref="artists", lazy=True)
    num_upcoming_shows = db.Column(db.Integer, default=0)
    website = db.Column(db.String(120), nullable=True)
    seeking_talent = db.Column(db.Boolean, nullable=True)
    seeking_description = db.Column(db.String(255), nullable=True)



# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__="shows"
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), primary_key=True)
    start_time=db.Column(db.DateTime, primary_key=True)




#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  # num_shows should be aggregated based on number of upcoming shows per venue.
  area_venues = db.session.query(Venue.city,Venue.state).group_by(Venue.city,Venue.state).all()
  data=[]
  for v in area_venues:
      venues = db.session.query(Venue.id,Venue.name,Venue.num_upcoming_shows).filter(Venue.city==v[0],Venue.state==v[1]).all()
      data.append({"city": v[0],
      "state": v[1],
      "venues":venues})
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
    term = '%' + request.form.get('search_term', '')+ '%'
    all_venue = Venue.query.with_entities(Venue.id, Venue.name, Venue.num_upcoming_shows).filter(Venue.name.ilike(term)).all()
    response=[]
    response = { "count": len(all_venue), "data": [{
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": venue.num_upcoming_shows,
          } for venue in all_venue]
        }
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.filter_by(id=venue_id).all()[0]
  venue_shows= db.session.query(Show).join(Venue, Show.venue_id == Venue.id).filter(Venue.id==venue_id).all()
  past_shows=[]
  upcoming_shows=[]
  for show in venue_shows:
      if  show.start_time <= datetime.now():
          past_shows.append(show)
      else:
          upcoming_shows.append(show)

  all_geners=venue.genres.replace('{', '')
  all_geners=all_geners.replace('}', '')
  arr_geners=all_geners.split(",")
  data={
    "id": venue.id,
    "name": venue.name,
    "genres": arr_geners,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description":venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": [{
      "artist_id": shows.artist_id,
      "artist_name": Artist.query.get(shows.artist_id).name,
      "artist_image_link": Artist.query.get(shows.artist_id).image_link,
      "start_time": str(shows.start_time)
    } for shows in past_shows] ,
    "upcoming_shows": [{
      "artist_id": shows.artist_id,
      "artist_name": Artist.query.get(shows.artist_id).name,
      "artist_image_link": Artist.query.get(shows.artist_id).image_link,
      "start_time": str(shows.start_time)
    } for shows in upcoming_shows],
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  errorFlag=False
  try:
      phone = request.form.get('phone').replace('-','')
      if not phone.isdigit() or len(phone)!=10:
          raise ValidationError()
      newVenue = Venue(
      name=request.form.get('name'),
      city=request.form.get('city'),
      state=request.form.get('state'),
      address=request.form.get('address'),
      genres=request.form.getlist('genres'),
      phone=request.form.get('phone'),
      image_link=request.form.get('image_link'),
      facebook_link=request.form.get('facebook_link'))
      db.session.add(newVenue)
      db.session.commit()
  except ValidationError:
      errorFlag=True
      flash('An error occurred. The phone number should be valid')
  except:
      errorFlag=True
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()
  if not errorFlag:
  # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  else:
  # TODO: on unsuccessful db insert, flash an error instead.
    flash('There is an error \'' + request.form['name'] + '\' could not be added.')

  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    errorondelete=False
      # TODO: Complete this endpoint for taking a venue_id, and using
      # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        db.session.delete(Venue.query.filter_by(venue_id))
        db.session.commit()
    except:
        errorondelete=True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if not errorondelete:
        flash('Venue  was successfully deleted!')
    else:
        flash('There is an error, could not be deleted.')

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
    return  render_template('pages/home.html')


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    artists = db.session.query(Artist.id, Artist.name).all()
    data=[]
    for a in artists:
        data.append({"id": a[0], "name": a[1]})
  # TODO: replace with real data returned from querying the database
    return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  term = '%' + request.form.get('search_term', '')+ '%'
  All_Artist = Artist.query.with_entities(Artist.id, Artist.name, Artist.num_upcoming_shows).filter(Artist.name.ilike(term)).all()
  response=[]
  response = { "count": len(All_Artist), "data": [{
          "id": artist.id,
          "name": artist.name,
          "num_upcoming_shows": artist.num_upcoming_shows,
        } for artist in All_Artist]
      }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    artist = Artist.query.filter_by(id=artist_id).all()[0]
    artist_shows= db.session.query(Show).join(Artist, Show.artist_id == Artist.id).filter(Artist.id==artist_id).all()
    past_shows=[]
    upcoming_shows=[]
    for show in artist_shows:
        if show.start_time <= datetime.now():
            past_shows.append(show)
        else:
            upcoming_shows.append(show)

    all_geners=artist.genres.replace('{', '')
    all_geners=all_geners.replace('}', '')
    arr_geners=all_geners.split(",")
    data={
    "id": artist.id,
    "name": artist.name,
    "genres": arr_geners,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_talent": artist.seeking_talent,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": [{
      "venue_id": shows.venue_id,
      "venue_name": Venue.query.get(shows.venue_id).name,
      "venue_image_link": Venue.query.get(shows.venue_id).image_link,
      "start_time": str(shows.start_time)
    }  for shows in past_shows],
    "upcoming_shows": [{
      "venue_id": shows.venue_id,
      "venue_name": Venue.query.get(shows.venue_id).name,
      "venue_image_link": Venue.query.get(shows.venue_id).image_link,
      "start_time": str(shows.start_time)
    }  for shows in upcoming_shows],
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
    }
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  # TODO: populate form with fields from artist with ID <artist_id>
  artist = Artist.query.get(artist_id)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
      artist = Artist.query.get(artist_id)
      artist.name = equest.form.get('name')
      artist.city=request.form.get('city')
      artist.state=request.form.get('state')
      artist.genres=request.form.getlist('genres')
      artist.phone=request.form.get('phone')
      artist.image_link=request.form.get('image_link')
      artist.facebook_link=request.form.get('facebook_link')
      db.session.commit()
  except:
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
      venue = Venue.query.get(venue_id)
      venue.name =request.form.get('name')
      venue.city=request.form.get('city')
      venue.state=request.form.get('state')
      venue.genres=request.form.getlist('genres')
      venue.phone=request.form.get('phone')
      venue.address=request.form.get('address')
      venue.image_link=request.form.get('image_link')
      venue.facebook_link=request.form.get('facebook_link')
      db.session.commit()
  except:
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  errorFlag=False
  try:
      phone = request.form.get('phone').replace('-','')
      if not phone.isdigit() or len(phone)!=10:
          raise ValidationError()
      newArtist = Artist(
      name=request.form.get('name'),
      city=request.form.get('city'),
      state=request.form.get('state'),
      genres=request.form.getlist('genres'),
      phone=request.form.get('phone'),
      image_link=request.form.get('image_link'),
      facebook_link=request.form.get('facebook_link'))
      db.session.add(newArtist)
      db.session.commit()
  except ValidationError:
      errorFlag=True
      flash('An error occurred. The phone number should be valid')
  except:
      errorFlag=True
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()
  if not errorFlag:
  # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  else:
  # TODO: on unsuccessful db insert, flash an error instead.
    flash('There is an error Artist \'' + request.form['name'] + '\' could not be added.')

  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  # num_shows should be aggregated based on number of upcoming shows per venue.
  try:
      today = datetime.now()
      all_shows= Show.query.filter(Show.start_time > today).all()
      data = []
      for show in all_shows:
        venue = Venue.query.get(show.venue_id)
        artist = Artist.query.get(show.artist_id)
        data.append({
          "venue_id": show.venue_id,
          "venue_name": venue.name,
          "artist_id": show.artist_id,
          "artist_name": artist.name,
          "artist_image_link": artist.image_link,
          "start_time": str(show.start_time)
          })
  except :
      print(sys.exc_info())

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  errorFlag=False
  try:
      Sdate=datetime.strptime(request.form['start_time'], '%Y-%m-%d %H:%M:%S')
      if Sdate < datetime.today():
          raise ValidationError()

      venueid=request.form.get('venue_id')
      artistid=request.form.get('artist_id')
      newShow = Show(artist_id=artistid,
      venue_id=venueid,
      start_time=request.form['start_time'])
      venue = Venue.query.get(venueid)
      venue.num_upcoming_shows = venue.num_upcoming_shows + 1
      artist = Artist.query.get(artistid)
      artist.num_upcoming_shows = artist.num_upcoming_shows + 1
      db.session.add(newShow)
      db.session.commit()
  except ValidationError:
      errorFlag=True
      flash('An error occurred. The start date should not be earlier than today')
  except:
      errorFlag=True
      db.session.rollback()
      print(sys.exc_info())
      flash('An error occurred. Show could not be listed.')
  finally:
      db.session.close()

  if not errorFlag:
      # on successful db insert, flash success
      flash('Show was successfully listed!')

  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
