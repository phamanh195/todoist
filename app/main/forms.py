from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, HiddenField
from wtforms.validators import Required


class NoteForm(FlaskForm):
    note = StringField('Note:', validators=[Required()])
    submit = SubmitField('Add')


class EditNoteForm(FlaskForm):
    note = StringField('Note', validators=[Required()])
    status = BooleanField('Have done yet?')
    previous = HiddenField('Previous URL')
    submit = SubmitField('Update')