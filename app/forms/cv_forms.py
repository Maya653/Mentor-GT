from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired

class CVForm(FlaskForm):
    formato = SelectField('Formato', choices=[
        ('pdf', 'PDF'),
        ('word', 'Word (DOCX)')
    ], validators=[DataRequired()])
    
    tipo_cv = SelectField('Tipo de CV', choices=[
        ('academico', 'Académico'),
        ('sni', 'SNI (Sistema Nacional de Investigadores)'),
        ('conacyt', 'CONACyT')
    ], validators=[DataRequired()])
    
    submit = SubmitField('Generar CV')

