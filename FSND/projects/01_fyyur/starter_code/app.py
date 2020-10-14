#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
Flask,
render_template,
request,
Response,
flash,
redirect,
url_for
)
from models import app, db, Venue, Artist, Show
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
from flask_wtf import CsrfProtect



#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

moment = Moment(app)
app.config.from_object('config')

#----------------------------------------------------------------------------#
# csrf Token
#----------------------------------------------------------------------------#
csrf = CsrfProtect()
csrf.init_app(app)


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

#  Search for Venue
#  ----------------------------------------------------------------
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
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


#  Show Venue
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)
  past_shows = db.session.query(Artist, Show).join(Show).join(Venue).\
  filter(
        Show.venue_id == venue_id,
        Show.artist_id == Artist.id,
        Show.start_time < datetime.now()
        ).\
        all()
  upcoming_shows = db.session.query(Artist, Show).join(Show).join(Venue).\
  filter(
      Show.venue_id == venue_id,
      Show.artist_id == Artist.id,
      Show.start_time >= datetime.now()
      ).\
      all()

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
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": str(show.start_time)
    } for artist, show  in past_shows] ,
    "upcoming_shows": [{
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": str(show.start_time)
    } for artist, show  in upcoming_shows],
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
  errorFlag=False
  try:
      form=VenueForm(request.form)
      newVenue = Venue()
      if request.method=='POST' and form.validate():
          form.populate_obj(newVenue)
          db.session.add(newVenue)
          db.session.commit()
      else:
          errorFlag=True
          for error in form.errors:
              error_message = str(form.errors[error][0])
              flash(error_message)
  except:
      errorFlag=True
      flash('There is an error \'' + request.form['name'] + '\' could not be added.')
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()

  if not errorFlag:
      flash('Venue ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html')

#  DELETE Venue
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    errorondelete=False
    try:
        venue=Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
    except:
        errorondelete=True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if not errorondelete:
        flash('Venue was successfully deleted!')
    else:
        flash('There is an error, could not be deleted.')
    return  render_template('pages/home.html')



#  EDIT Venue
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  form.name.data = venue.name
  form.genres.data = venue.genres
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.website.data = venue.website
  form.facebook_link.data = venue.facebook_link
  form.image_link.data = venue.image_link
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  errorFlag=False
  try:
      form = VenueForm(request.form)
      if request.method=='POST' and form.validate():
          venue = Venue.query.get(venue_id)
          form.populate_obj(venue)
          db.session.commit()
      else:
          errorFlag=True
          for error in form.errors:
              error_message = str(form.errors[error][0])
              flash(error_message)
  except:
      errorFlag=True
      flash('There is an error Venue \'' + request.form['name'] + '\' could not be edited.')
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()
  if not errorFlag:
      flash('Venue ' + request.form['name'] + ' was successfully edited!')

  return redirect(url_for('show_venue', venue_id=venue_id))


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
    past_shows = db.session.query(Venue, Show).join(Show).join(Artist).\
    filter(
          Show.artist_id == artist_id,
          Show.venue_id == Venue.id,
          Show.start_time < datetime.now()
          ).\
          all()
    upcoming_shows = db.session.query(Venue, Show).join(Show).join(Artist).\
    filter(
        Show.artist_id == artist_id,
        Show.venue_id == Venue.id,
        Show.start_time >= datetime.now()
        ).\
        all()

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
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": [{
      "venue_id": venue.id,
      "venue_name": venue.name,
      "venue_image_link": venue.image_link,
      "start_time": str(show.start_time)
    }  for venue, show in past_shows],
    "upcoming_shows": [{
      "venue_id": venue.id,
      "venue_name": venue.name,
      "venue_image_link": venue.image_link,
      "start_time": str(show.start_time)
    }  for venue, show in upcoming_shows],
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
    }
    return render_template('pages/show_artist.html', artist=data)

#  Edit Artist
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  # TODO: populate form with fields from artist with ID <artist_id>
  artist = Artist.query.get(artist_id)
  form.name.data = artist.name
  form.genres.data = artist.genres
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.website.data = artist.website
  form.facebook_link.data = artist.facebook_link
  form.image_link.data = artist.image_link
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  errorFlag=False
  form = ArtistForm(request.form)
  try:
      if request.method=='POST' and  form.validate():
          artist = Artist.query.get(artist_id)
          form.populate_obj(artist)
          db.session.commit()
      else:
          errorFlag=True
          for error in form.errors:
              error_message = str(form.errors[error][0])
              flash(error_message)
  except:
      errorFlag=True
      flash('There is an error Artist \'' + request.form['name'] + '\' could not be edited.')
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()

  if not errorFlag:
      flash('Artist ' + request.form['name'] + ' was successfully edited!')

  return redirect(url_for('show_artist', artist_id=artist_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  errorFlag=False
  form = ArtistForm(request.form)
  try:
      newArtist = Artist()
      if request.method=='POST' and form.validate():
          form.populate_obj(newArtist)
          db.session.add(newArtist)
          db.session.commit()
      else:
          errorFlag=True
          for error in form.errors:
              error_message = str(form.errors[error][0])
              flash(error_message)

  except:
      errorFlag=True
      flash('There is an error Artist \'' + request.form['name'] + '\' could not be added.')
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()

  if not errorFlag:
      flash('Artist ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html')

#  DELETE Artist
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
    errorondelete=False
    try:
        artist=Artist.query.get(artist_id)
        db.session.delete(artist)
        db.session.commit()
    except:
        errorondelete=True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if not errorondelete:
        flash('Artist was successfully deleted!')
    else:
        flash('There is an error, could not be deleted.')
    return  render_template('pages/home.html')


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
      form=ShowForm(request.form)
      newShow = Show()
      if request.method=='POST' and form.validate():
          venue = Venue.query.get(request.form.get('venue_id'))
          venue.num_upcoming_shows = venue.num_upcoming_shows + 1
          artist = Artist.query.get(request.form.get('artist_id'))
          artist.num_upcoming_shows = artist.num_upcoming_shows + 1
          form.populate_obj(newShow)
          db.session.add(newShow)
          db.session.commit()
      else:
          errorFlag=True
          for error in form.errors:
              error_message = str(form.errors[error][0])
              flash(error_message)

  except  AttributeError as ae:
      errorFlag=True
      db.session.rollback()
      flash('The artist or veneu does not exist!')
  except:
      errorFlag=True
      db.session.rollback()
      print(sys.exc_info())
      flash('An error occurred. Show could not be listed.')
  finally:
      db.session.close()

  if not errorFlag:
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
