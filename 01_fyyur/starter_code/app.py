#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from email.headerregistry import Address
from os import abort
import sys
from ast import If
from asyncio import current_task
from dataclasses import dataclass
from email.charset import SHORTEST
import json
from math import dist
from unittest import result
from urllib import response
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
from datetime import time
from datetime import date
from models import Venue, Artist, All_Shows
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
moment = Moment(app)
migrate = Migrate(app, db)

# TODO: Completed connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


# TODO - Completed Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

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
def upcoming_shows_venue(venueid):
  return (All_Shows.query.filter(All_Shows.venue_id == venueid).filter(All_Shows.start_time > datetime.now()).count())

def past_shows_venue(venueid):
  return (All_Shows.query.filter(All_Shows.venue_id == venueid).filter(All_Shows.start_time < datetime.now()).count())

def upcoming_shows_artist(artistid):
  return (All_Shows.query.filter(All_Shows.artist_id == artistid).filter(All_Shows.start_time > datetime.now()).count())

def past_shows_artist(artistid):
  return (All_Shows.query.filter(All_Shows.artist_id == artistid).filter(All_Shows.start_time < datetime.now()).count())

@app.route('/venues')
def venues():
  # TODO - Completed: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  distinct = Venue.query.distinct(Venue.city, Venue.state).all()
  for each in distinct:
    city_state = {"city" : each.city, "state" : each.state}
    venues = Venue.query.filter_by(city=each.city, state=each.state).all()

    formatted_venues = []
    for venue in venues:
      formatted_venues.append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": upcoming_shows_venue(venue.id)
      })
    city_state['venues'] = formatted_venues
    data.append(city_state)
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO - Completed: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response = {}
  response['data'] = []
  response['count'] = []
  search_term = request.form.get('search_term', '')
  response['data'] = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  response['count'] = len(response['data'])
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO - Completed : replace with real venue data from the venues table, using venue_id
  getvenue = Venue.query.get(venue_id)
  pastshowslist = All_Shows.query.filter(All_Shows.venue_id == venue_id).filter(All_Shows.start_time < datetime.now()).all()
  futureshowslist = All_Shows.query.filter(All_Shows.venue_id == venue_id).filter(All_Shows.start_time > datetime.now()).all()
  
  past_shows = []
  for show in pastshowslist:    
    artistget = Artist.query.get(show.artist_id)
    past_shows.append({
      "artist_id": artistget.id,
      "artist_name": artistget.name,
      "artist_image_link": artistget.image_link,
      "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    })
  upcoming_shows = []
  for show in futureshowslist:
    artistget = Artist.query.get(show.artist_id)
    upcoming_shows.append({
        "artist_id": artistget.id,
        "artist_name": artistget.name,
        "artist_image_link": artistget.image_link,
        "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    })
  data = {
      "id": getvenue.id,
      "name": getvenue.name,
      "genres": getvenue.genres.split(","),
      "city": getvenue.city,
      "state": getvenue.state,
      "phone": getvenue.phone,
      "seeking_talent": True if getvenue.seeking_talent in ('y', True) else False,
      "seeking_description": getvenue.seeking_description,
      "image_link": getvenue.image_link,
      "facebook_link": getvenue.facebook_link,
      "website_link": getvenue.website,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": past_shows_venue(venue_id),
      "upcoming_shows_count": upcoming_shows_venue(venue_id)
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
  # TODO: Completed modify data to be the data object returned from db insertion
  form = VenueForm(request.form)
  try:
      new_venue = Venue(
          name=form.name.data,
          city=form.city.data,
          state=form.state.data,
          address=form.address.data,
          phone=form.phone.data,
          genres=form.genres.data, 
          image_link=form.image_link.data,
          facebook_link=form.facebook_link.data,
          website=form.website_link.data,
          seeking_talent=True if form.seeking_talent.data in ('y', True) else False,
          seeking_description=form.seeking_description.data,
      )
      db.session.add(new_venue)
      db.session.commit()
      flash("Venue " + request.form["name"] + " was successfully listed!")
  except Exception:
      db.session.rollback()
      flash("Venue was not successfully listed.")
  finally:
      db.session.close()
    
  # TODO: Completed on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Completed Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
    error = False
    try:
        list = Venue.query.get(venue_id)
        db.session.delete(list)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: Completed replace with real data returned from querying the database
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: Completed implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response = {}
  response['data'] = []
  response['count'] = []
  search_term = request.form.get('search_term', '')
  response['data'] = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  response['count'] = len(response['data'])
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO - Completed: replace with real artist data from the artist table, using artist_id
  getartist = Artist.query.get(artist_id)
  pastshowslist = All_Shows.query.filter(All_Shows.artist_id == artist_id).filter(All_Shows.start_time < datetime.now()).all()
  futureshowslist = All_Shows.query.filter(All_Shows.artist_id == artist_id).filter(All_Shows.start_time > datetime.now()).all()
  
  past_shows = []
  for show in pastshowslist:    
    venue = Venue.query.get(show.venue_id)
    past_shows.append({
      "venue_id": venue.id,
      "venue_name": venue.name,
      "venue_image_link": venue.image_link,
      "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    })
  upcoming_shows = []
  for show in futureshowslist:
    venue = Venue.query.get(show.venue_id)
    upcoming_shows.append({
        "venue_id": venue.id,
        "venue_name": venue.name,
        "venue_image_link": venue.image_link,
        "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    })
  data = {
      "id": getartist.id,
      "name": getartist.name,
      "genres": getartist.genres,
      "city": getartist.city,
      "state": getartist.state,
      "phone": getartist.phone,
      "seeking_venue": True if getartist.seeking_venue in ('y', True) else False,
      "seeking_description": getartist.seeking_description,
      "image_link": getartist.image_link,
      "facebook_link": getartist.facebook_link,
      "website_link": getartist.website,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": past_shows_artist(artist_id),
      "upcoming_shows_count": upcoming_shows_artist(artist_id)
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  # TODO: Completed populate form with fields from artist with ID <artist_id>
  
  form.name.data = artist.name
  form.genres.data = artist.genres
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.website_link.data = artist.website
  form.facebook_link.data = artist.facebook_link
  form.seeking_venue.data = True if artist.seeking_venue in ('y', True) else False
  form.seeking_description.data = artist.seeking_description
  form.image_link.data = artist.image_link

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: Completed take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm(request.form)
  try:
    artist = Artist.query.get(artist_id)
    artist.name = form.name.data
    artist.genres = form.genres.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.website = form.website_link.data
    artist.facebook_link = form.facebook_link.data
    artist.seeking_venue = True if form.seeking_venue.data in ('y', True) else False
    artist.seeking_description = form.seeking_description.data
    artist.image_link = form.image_link.data

    db.session.commit()
    flash('The Artist has been successfully updated!')
  except:
    db.session.rollback()
    flash('An Error has occured')
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  # TODO: Commpleted populate form with values from venue with ID <venue_id>
  form.name.data = venue.name
  form.genres.data = venue.genres
  form.address.data = venue.address
  form.city.data = venue.city
  form.state.data = venue.state
  form.phone.data = venue.phone
  form.website_link.data = venue.website
  form.facebook_link.data = venue.facebook_link
  form.seeking_talent.data = True if venue.seeking_talent in ('y', True) else False
  form.seeking_description.data = venue.seeking_description
  form.image_link.data = venue.image_link

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: Completed take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(request.form)
  try:
    venue = Venue.query.get(venue_id)
    venue.name = form.name.data
    venue.genres = form.genres.data
    venue.address = form.address.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.phone = form.phone.data
    venue.website = form.website_link.data
    venue.facebook_link = form.facebook_link.data
    venue.seeking_talent = True if form.seeking_talent.data in ('y', True) else False
    venue.seeking_description = form.seeking_description.data
    venue.image_link = form.image_link.data

    db.session.commit()
    flash('The Venue has been successfully updated!')
  except:
    db.session.rollback()
    flash('An Error has occured')
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
  # TODO: Completed insert form data as a new Venue record in the db, instead
  # TODO: Completed modify data to be the data object returned from db insertion
  form = ArtistForm(request.form)
  try:
      new_artist = Artist(
          name=form.name.data,
          city=form.city.data,
          state=form.state.data,
          phone=form.phone.data,
          genres=form.genres.data,
          image_link=form.image_link.data,
          facebook_link=form.facebook_link.data,
          website=form.website_link.data,
          seeking_venue=True if form.seeking_venue.data in ('y', True) else False,
          seeking_description=form.seeking_description.data
      )
      db.session.add(new_artist)
      db.session.commit()
      flash("Artist " + request.form["name"] + " was successfully listed!")
  except Exception:
      db.session.rollback()
      flash("Artist was not successfully listed.")
  finally:
      db.session.close()
  # on successful db insert, flash success
  #flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: Completed on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO - Completed: replace with real venues data.
  shows_query = db.session.query(All_Shows).join(Artist).join(Venue).all()

  data = []
  for show in shows_query: 
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venues.name,
      "artist_id": show.artist_id,
      "artist_name": show.Artist.name, 
      "artist_image_link": show.Artist.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: completedinsert form data as a new Show record in the db, instead
  form = ShowForm(request.form)
  try:
      new_show = All_Shows(
          artist_id=form.artist_id.data,
          venue_id=form.venue_id.data,
          start_time=form.start_time.data
      )
      db.session.add(new_show)
      db.session.commit()
      flash("Show was successfully listed!")
  except Exception:
      db.session.rollback()
      flash("Show was not successfully listed.")
  finally:
      db.session.close()
  # on successful db insert, flash success
  #flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
