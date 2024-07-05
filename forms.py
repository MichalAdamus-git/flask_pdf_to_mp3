from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL

class upload_form(FlaskForm):
    filename = StringField(label='file_name', validators=[DataRequired()])
    file = FileField(label = 'Uploaed your file', validators=[FileRequired()])
    submit = SubmitField(label='convert')