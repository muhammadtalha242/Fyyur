

#----------------------------------------------------------------------------#
# Imports #talha
#----------------------------------------------------------------------------#
# HEllo WORLD !!!
import json
import dateutil.parser
import babel
from datetime import datetime
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)
# TODO: connect to a local postgresql database (DONE)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean())
    seeking_description = db.Column(db.String(500))

    shows = db.relationship("Show",
                            backref=db.backref('Venue',
                                               cascade="all,delete"), lazy=True)

    def __repr__(self):
        return '<Venue:  id: {}, name: {}>'.format(self.id, self.name)

    def getDict(self):
        return self.__dict__

    def get_past_shows(self):
        past_shows = []
        for show in self.shows:
            if (show.start_time < datetime.now()):
                past_shows.append({

                    "artist_id": show.artist_id,
                    "start_time": str(show.start_time),
                    "artist_name": show.Artist.name,
                    "artist_image_link": show.Artist.image_link
                })
        return past_shows

    def get_upcoming_shows(self):
        upcoming_shows = []
        for show in self.shows:
            if (show.start_time > datetime.now()):
                upcoming_shows.append({

                    "artist_id": show.artist_id,
                    "start_time": str(show.start_time),
                    "artist_name": show.Artist.name,
                    "artist_image_link": show.Artist.image_link
                })
        return upcoming_shows

    # TODO: implement any missing fields, as a database migration using Flask-Migrate (DONE)


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean())
    seeking_description = db.Column(db.String(500))

    shows = db.relationship("Show", backref="Artist", lazy=True)

    def __repr__(self):
        return '<Artist id: {}, name: {}>'.format(self.id, self.name,)

    def getDict(self):
        return self.__dict__

    def get_past_shows(self):
        past_shows = []
        for show in self.shows:
            if (show.start_time < datetime.now()):
                past_shows.append({

                    "venue_id": show.venue_id,
                    "start_time": str(show.start_time),
                    "venue_name": show.Venue.name,
                    "venue_image_link": show.Venue.image_link
                })
        return past_shows

    def get_upcoming_shows(self):
        upcoming_shows = []
        for show in self.shows:
            if (show.start_time > datetime.now()):
                upcoming_shows.append({

                    "venue_id": show.venue_id,
                    "start_time": str(show.start_time),
                    "venue_name": show.Venue.name,
                    "venue_image_link": show.Venue.image_link
                })
        return upcoming_shows

    # TODO: implement any missing fields, as a database migration using Flask-Migrate (DONE)


class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.now(), nullable=False)

    def __repr__(self):
        return '<Show artist_id: {}, venue_id: {}, start_time: {}>'.format(self.artist_id, self.venue_id, self.start_time)

    def getDict(self):
        return self.__dict__

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration. (DONE)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"

    return babel.dates.format_datetime(date, format, locale='en_US')


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
    # TODO: replace with real venues data. (DONE)
    # num_shows should be aggregated based on number of upcoming shows per venue.

    data = []
    for city_state in Venue.query.with_entities(Venue.city, Venue.state).group_by(Venue.city, Venue.state).all():
        cs = {}
        cs['city'] = city_state.city
        cs['state'] = city_state.state
        cs['venues'] = []
        for venue in Venue.query.filter_by(city=city_state.city).all():
            cs.get("venues").append({
                'id': venue.id,
                'name': venue.name,
                'num_upcoming_shows': len(Venue.get_upcoming_shows(venue))})
        data.append(cs)
   
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive. (DONE)
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    search_term = request.form.get('search_term', '')

    search_response = Venue.query.filter(
        Venue.name.ilike(f"%{search_term}%")).all()
    data = []
    for venue in search_response:
        data.append({"id": venue.id, "name": venue.name,
                     "num_upcoming_shows": len(Venue.get_upcoming_shows(venue))})

    response = {
        "count": len(data),
        "data": data
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id (DONE)

    venue = Venue.query.filter_by(id=venue_id).first()
    data = venue.getDict()
    data['genres'] = venue.genres.split(',')
    past_shows = Venue.get_past_shows(venue)
    upcoming_shows = Venue.get_upcoming_shows(venue)
    data["past_shows"] = past_shows
    data["upcoming_shows"] = upcoming_shows
    data["past_shows_count"] = len(past_shows) if len(past_shows) > 0 else 0
    data["upcoming_shows_count"] = len(
        upcoming_shows) if len(upcoming_shows) > 0 else 0

   
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
    venue_form_data = VenueForm()
    name = venue_form_data.name.data
    phone = venue_form_data.phone.data
    address = venue_form_data.address.data
    city = venue_form_data.city.data
    image_url = venue_form_data.image_link.data
    facebook_url = venue_form_data.facebook_link.data
    state = venue_form_data.state.data
    genres = ', '.join(venue_form_data.genres.data)
    seeking_talent = venue_form_data.seeking_talent.data
    seeking_description = venue_form_data.seeking_description.data
    website = venue_form_data.website.data

    new_venue = Venue(name=name, city=city, state=state, address=address, phone=phone, image_link=image_url,
                  facebook_link=facebook_url, genres=genres,
                  website=website, seeking_talent=seeking_talent,
                  seeking_description=seeking_description)
    
    

    # on successful db insert, flash success

    try:
      db.session.add(new_venue)
      db.session.commit()
      
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except Exception  as e:
    # TODO: on unsuccessful db insert, flash an error instead.  (DONE)
   
      
      db.session.rollback()
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
      db.session.flush()
      print(e)
  
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using  (DONE)
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
      venue = Venue.query.filter_by(id=venue_id).delete()
      
      db.session.commit()
      flash('Venue  successfully deleted.')

    except Exception  as e:      
      db.session.rollback()
      flash('Venue could not be deleted')
      db.session.flush()
      print(e)
    return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    artists = Artist.query.all()
    data = []
    for artist in artists:
        data.append({
            "id": artist.id,
            "name": artist.name,
        })
   
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get('search_term', '')

    search_response = Artist.query.filter(
        Artist.name.ilike(f"%{search_term}%")).all()
    data = []
    for artist in search_response:
        data.append({"id": artist.id, "name": artist.name, "num_upcoming_shows": len(
            Artist.get_upcoming_shows(artist))})

    response = {
        "count": len(data),
        "data": data
    }

   
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using artist_id

    artist = Artist.query.filter_by(id=artist_id).first()
    data = artist.getDict()
    data['genres'] = artist.genres.split(',')
    past_shows = Artist.get_past_shows(artist)
    upcoming_shows = Artist.get_upcoming_shows(artist)
    data["past_shows"] = past_shows
    data["upcoming_shows"] = upcoming_shows
    data["past_shows_count"] = len(past_shows) if len(past_shows) > 0 else 0
    data["upcoming_shows_count"] = len(
        upcoming_shows) if len(upcoming_shows) > 0 else 0

    
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.filter_by(id=artist_id).first()

    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    
    artist_form_data = ArtistForm()
    artist = Artist.query.filter_by(id=artist_id).first()
    artist.name = artist_form_data.name.data
    artist.phone = artist_form_data.phone.data
    artist.city = artist_form_data.city.data
    artist.image_url = artist_form_data.image_link.data
    artist.facebook_url = artist_form_data.facebook_link.data
    artist.state = artist_form_data.state.data
    artist.genres = ', '.join(artist_form_data.genres.data)
    artist.seeking_venue = artist_form_data.seeking_venue.data
    artist.seeking_description = artist_form_data.seeking_description.data
    artist.website = artist_form_data.website.data

    

    # on successful db insert, flash success

    try:
      # db.session.add(artist)
      db.session.commit()
      
      flash('Artist ' + request.form['name'] + ' was successfully updated!')

    except Exception  as e:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
      
      db.session.rollback()
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
      db.session.flush()
      print(e)
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.filter_by(id=venue_id).first()
  
    # TODO: populate form with values from venue with ID <venue_id> (DONE)
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing (DONE)
    # venue record with ID <venue_id> using the new attributes
    
    venue_form_data = VenueForm()
    venue = Venue.query.filter_by(id=venue_id).first()
    venue.name = venue_form_data.name.data
    venue.phone = venue_form_data.phone.data
    venue.address = venue_form_data.address.data
    venue.city = venue_form_data.city.data
    venue.image_url = venue_form_data.image_link.data
    venue.facebook_url = venue_form_data.facebook_link.data
    venue.state = venue_form_data.state.data
    venue.genres = ', '.join(venue_form_data.genres.data)
    venue.seeking_talent = venue_form_data.seeking_talent.data
    venue.seeking_description = venue_form_data.seeking_description.data
    venue.website = venue_form_data.website.data


    try:
      # db.session.add(venue)
      db.session.commit()
      
      flash('Venue ' + request.form['name'] + ' was successfully Updated!')
    except Exception  as e:
    # TODO: on unsuccessful db insert, flash an error instead. (DONE)

      
      db.session.rollback()
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be Updated.')
      db.session.flush()
      print(e)



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
    # TODO: modify data to be the data object returned from db insertion  (DONE)
    artist_form_data = ArtistForm()
    name = artist_form_data.name.data
    phone = artist_form_data.phone.data
    city = artist_form_data.city.data
    image_url = artist_form_data.image_link.data
    facebook_url = artist_form_data.facebook_link.data
    state = artist_form_data.state.data
    genres = ', '.join(artist_form_data.genres.data)
    seeking_venue = artist_form_data.seeking_venue.data
    seeking_description = artist_form_data.seeking_description.data
    website = artist_form_data.website.data

    new_artist = Artist(name=name, city=city, state=state, phone=phone, image_link=image_url,
                  facebook_link=facebook_url, genres=genres,
                  website=website, seeking_venue=seeking_venue,
                  seeking_description=seeking_description)


    print('new_artist to be created: ',new_artist)

    # on successful db insert, flash success

    try:
      db.session.add(new_artist)
      db.session.commit()
      
      flash('Artist ' + request.form['name'] + ' was successfully listed!')

    except Exception  as e:
    # TODO: on unsuccessful db insert, flash an error instead.  (DONE)
   
      
      db.session.rollback()
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
      db.session.flush()
      print(e)
 
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.

    data = []
    for artist in Artist.query.all():
        for show in artist.shows:
            s = show.getDict()
            s['artist_name'] = artist.name
            s['artist_image_link'] = artist.image_link
            s['venue_name'] = Venue.query.filter_by(
                id=show.venue_id).first().name
            s["start_time"] = str((show.start_time))
            data.append(s)

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
    show_form_data = ShowForm()
    artist_id = show_form_data.artist_id.data
    venue_id = show_form_data.venue_id.data
    start_time = show_form_data.start_time.data

    new_show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)


    

    # on successful db insert, flash success

    try:
      db.session.add(new_show)
      db.session.commit()
      
      flash('Show was successfully listed!')

    except Exception  as e:
    # TODO: on unsuccessful db insert, flash an error instead.      
      db.session.rollback()
      flash('An error occurred. Show could not be listed.')
      db.session.flush()
      print(e)

   
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
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
