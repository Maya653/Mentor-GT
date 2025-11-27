from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional

class UsuarioForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=100)])
    apellidos = StringField('Apellidos', validators=[Length(max=100)])
    password = PasswordField('Contraseña', validators=[Optional(), Length(min=6)])
    rol = SelectField('Rol', choices=[('profesor', 'Profesor'), ('admin', 'Administrador')], 
                     validators=[DataRequired()])
    activo = BooleanField('Activo', default=True)
    submit = SubmitField('Guardar')

