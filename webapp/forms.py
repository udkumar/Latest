from wtforms import StringField, SubmitField, FileField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileField, FileAllowed, FileRequired


class VideoUploadForm(FlaskForm):
	subject = StringField('Select Subject', validators=[DataRequired(), Length(min=4, max =50)])
	standard = StringField('Select Standard', validators=[DataRequired(), Length(min=4, max =50)])
	chapter = StringField('Chepter title', validators=[DataRequired(), Length(min=4, max =50)])
	videoUrl = StringField('Video Url', validators=[DataRequired(), Length(min=3, max =50)])
	file = FileField('Select File', validators=[FileRequired(), FileAllowed(['mp4', 'avi'], 'mp4 or avi only!')])
	submit = SubmitField('Upload Video')