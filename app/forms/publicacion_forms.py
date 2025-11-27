from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, NumberRange

class PublicacionForm(FlaskForm):
    titulo = StringField('Título', validators=[DataRequired(), Length(max=500)])
    autores = TextAreaField('Autores', validators=[Optional()], 
                           render_kw={"placeholder": "Separados por comas"})
    revista = StringField('Revista/Editorial', validators=[Optional(), Length(max=300)])
    volumen = StringField('Volumen', validators=[Optional(), Length(max=50)])
    numero = StringField('Número', validators=[Optional(), Length(max=50)])
    paginas = StringField('Páginas', validators=[Optional(), Length(max=50)])
    año = IntegerField('Año', validators=[DataRequired(), NumberRange(min=1900, max=2100)])
    doi = StringField('DOI', validators=[Optional(), Length(max=200)])
    isbn = StringField('ISBN', validators=[Optional(), Length(max=100)])
    tipo = SelectField('Tipo', choices=[
        ('articulo', 'Artículo'),
        ('libro', 'Libro'),
        ('capitulo', 'Capítulo de Libro'),
        ('ponencia', 'Ponencia'),
        ('resumen', 'Resumen'),
        ('otro', 'Otro')
    ], validators=[DataRequired()])
    indizada = BooleanField('Indizada (JCR, Scopus, etc.)', default=False)
    submit = SubmitField('Guardar')

