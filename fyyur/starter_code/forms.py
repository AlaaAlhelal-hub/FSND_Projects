from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import (
StringField,
SelectField,
SelectMultipleField,
DateTimeField,
TextAreaField,
BooleanField)
from wtforms.validators import(
DataRequired,
URL,
Length,
ValidationError
)
import re #Regexp

state_choices = [
    ('AL', 'AL'),
    ('AK', 'AK'),
    ('AZ', 'AZ'),
    ('AR', 'AR'),
    ('CA', 'CA'),
    ('CO', 'CO'),
    ('CT', 'CT'),
    ('DE', 'DE'),
    ('DC', 'DC'),
    ('FL', 'FL'),
    ('GA', 'GA'),
    ('HI', 'HI'),
    ('ID', 'ID'),
    ('IL', 'IL'),
    ('IN', 'IN'),
    ('IA', 'IA'),
    ('KS', 'KS'),
    ('KY', 'KY'),
    ('LA', 'LA'),
    ('ME', 'ME'),
    ('MT', 'MT'),
    ('NE', 'NE'),
    ('NV', 'NV'),
    ('NH', 'NH'),
    ('NJ', 'NJ'),
    ('NM', 'NM'),
    ('NY', 'NY'),
    ('NC', 'NC'),
    ('ND', 'ND'),
    ('OH', 'OH'),
    ('OK', 'OK'),
    ('OR', 'OR'),
    ('MD', 'MD'),
    ('MA', 'MA'),
    ('MI', 'MI'),
    ('MN', 'MN'),
    ('MS', 'MS'),
    ('MO', 'MO'),
    ('PA', 'PA'),
    ('RI', 'RI'),
    ('SC', 'SC'),
    ('SD', 'SD'),
    ('TN', 'TN'),
    ('TX', 'TX'),
    ('UT', 'UT'),
    ('VT', 'VT'),
    ('VA', 'VA'),
    ('WA', 'WA'),
    ('WV', 'WV'),
    ('WI', 'WI'),
    ('WY', 'WY'),
]

geners_choices=[
    ('Alternative', 'Alternative'),
    ('Blues', 'Blues'),
    ('Classical', 'Classical'),
    ('Country', 'Country'),
    ('Electronic', 'Electronic'),
    ('Folk', 'Folk'),
    ('Funk', 'Funk'),
    ('Hip-Hop', 'Hip-Hop'),
    ('Heavy Metal', 'Heavy Metal'),
    ('Instrumental', 'Instrumental'),
    ('Jazz', 'Jazz'),
    ('Musical Theatre', 'Musical Theatre'),
    ('Pop', 'Pop'),
    ('Punk', 'Punk'),
    ('R&B', 'R&B'),
    ('Reggae', 'Reggae'),
    ('Rock n Roll', 'Rock n Roll'),
    ('Soul', 'Soul'),
    ('Other', 'Other'),
]


#---------Validation Methods----------
def validate_phone(form, field):
    if not re.search(r'^[1-9]\d{2}-\d{3}-\d{4}$', field.data):
        raise ValidationError("error: Phone number should only contain digits (xxx-xxx-xxxx)")

def validate_start_time(form, field):
    if field.data < datetime.today():
        raise ValidationError("error: The start date should not be earlier than today")



# -------- Show Form --------
class ShowForm(FlaskForm):
    artist_id = StringField(
        'artist_id',
        validators=[DataRequired()]
    )
    venue_id = StringField(
        'venue_id',
        validators=[DataRequired()]
    )

    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired(), validate_start_time],
        default =datetime.today()
    )


# -------- Venue Form --------
class VenueForm(FlaskForm):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired(), Length(max=120, message="city field error: you\'ve exceeded the maximum character limit (120)")]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=state_choices
    )
    address = StringField(
        'address', validators=[DataRequired(), Length(max=120, message="address field error: you\'ve exceeded the maximum character limit (120)")]
    )
    phone = StringField(
        'phone', validators=[DataRequired(), validate_phone]
    )
    image_link = StringField(
        'image_link', validators=[DataRequired(),URL(require_tld=True, message="URL error: image link invalid "), Length(max=600, message="city field error: you\'ve exceeded the maximum character limit (600)")]

    )
    genres = SelectMultipleField(
        # TODO implement enum restriction
        'genres', validators=[DataRequired(), Length(max=120, message="genres field error: you\'ve exceeded the maximum character limit (120)")],
        choices=geners_choices
    )
    facebook_link = StringField(
        'facebook_link',validators=[DataRequired(), URL(require_tld=True, message="URL error: facebook link invalid "), Length(max=120, message="facebook_link field error: you\'ve exceeded the maximum character limit (120)")]
    )
    website = StringField(
        'website',validators=[DataRequired(), URL(require_tld=True, message="URL error: website link invalid "), Length(max=120, message="website field error: you\'ve exceeded the maximum character limit (120)")]
    )
    seeking_talent = BooleanField(
        'seeking_talent'
    )
    seeking_description = TextAreaField(
        'seeking_description', validators=[Length(max=255, message='seeking description field error: you\'ve exceeded the maximum character limit (255)')]
    )






# -------- Artist Form --------
class ArtistForm(FlaskForm):

    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired(), Length(max=120, message="city field error: you\'ve exceeded the maximum character limit (120)")]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=state_choices
    )
    phone = StringField(
        # TODO implement validation logic for state
        'phone',validators=[DataRequired(),validate_phone]
    )
    image_link = StringField(
        'image_link', validators=[DataRequired(), URL(require_tld=True, message="URL error: image link invalid "), Length(max=600, message="image_link field error: you\'ve exceeded the maximum character limit (600)")]
    )
    genres = SelectMultipleField(
        # TODO implement enum restriction
        'genres', validators=[DataRequired(), Length(max=120, message="genres field error: you\'ve exceeded the maximum character limit (120)")],
        choices=geners_choices
    )
    facebook_link = StringField(
        # TODO implement enum restriction
        'facebook_link', validators=[DataRequired(), URL(require_tld=True, message="URL error: facebook link invalid "), Length(max=120, message="facebook link field error: you\'ve exceeded the maximum character limit (120)")]
    )
    website = StringField(
        'website',validators=[DataRequired(), URL(require_tld=True, message="URL error: website link invalid "), Length(max=120, message="website field error: you\'ve exceeded the maximum character limit (120)")]
    )
    seeking_venue = BooleanField(
    'seeking_venue'
    )
    seeking_description = TextAreaField(
        'seeking_description', validators=[Length(max=255, message='seeking description field error: you\'ve exceeded the maximum character limit (255)')]
    )
# TODO IMPLEMENT NEW ARTIST FORM AND NEW SHOW FORM
