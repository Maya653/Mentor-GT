from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, DateField, SelectField, TextAreaField, IntegerField, FloatField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, Email

class DocenteForm(FlaskForm):
    """Formulario para perfil del docente"""
    cvu = StringField('CVU', validators=[Optional(), Length(max=50)])
    nombre_completo = StringField('Nombre Completo', validators=[DataRequired(), Length(max=255)])
    curp = StringField('CURP', validators=[Optional(), Length(max=18)])
    rfc = StringField('RFC', validators=[Optional(), Length(max=13)])
    sexo = SelectField('Sexo', choices=[('', 'Seleccionar'), ('M', 'Masculino'), ('F', 'Femenino')], validators=[Optional()])
    fecha_nacimiento = DateField('Fecha de Nacimiento', validators=[Optional()])
    pais_nacimiento = StringField('País de Nacimiento', validators=[Optional(), Length(max=100)])
    nacionalidad = StringField('Nacionalidad', validators=[Optional(), Length(max=100)])
    estado_civil = SelectField('Estado Civil', choices=[
        ('', 'Seleccionar'), ('soltero', 'Soltero'), ('casado', 'Casado'), 
        ('divorciado', 'Divorciado'), ('viudo', 'Viudo')
    ], validators=[Optional()])
    domicilio = TextAreaField('Domicilio', validators=[Optional()])
    correo_principal = StringField('Correo Principal', validators=[Optional(), Email(), Length(max=255)])
    orcid = StringField('ORCID ID', validators=[Optional(), Length(max=100)],
                       render_kw={"placeholder": "0000-0001-2345-6789"})
    researcher_id = StringField('Researcher ID', validators=[Optional(), Length(max=100)])
    scopus_author_id = StringField('Scopus Author ID', validators=[Optional(), Length(max=100)],
                                   render_kw={"placeholder": "Ej: 8243686100"})
    pubmed_query = StringField('PubMed (Búsqueda de autor)', validators=[Optional(), Length(max=255)],
                               render_kw={"placeholder": "Ej: Pérez García JM[Author]"})
    submit = SubmitField('Guardar')

