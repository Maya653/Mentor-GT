import re
from wtforms.validators import ValidationError

def validate_email(form, field):
    """Validador personalizado para email"""
    email = field.data
    if email:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValidationError('Email inválido')

def validate_orcid(form, field):
    """Validador para ORCID ID"""
    orcid = field.data
    if orcid:
        pattern = r'^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$'
        if not re.match(pattern, orcid):
            raise ValidationError('ORCID ID inválido. Formato: 0000-0000-0000-0000')

def validate_doi(form, field):
    """Validador para DOI"""
    doi = field.data
    if doi:
        pattern = r'^10\.\d{4,}/.+'
        if not re.match(pattern, doi):
            raise ValidationError('DOI inválido. Formato: 10.xxxx/...')

def validate_year(form, field):
    """Validador para año"""
    year = field.data
    if year:
        current_year = 2024  # Puede ser dinámico
        if year < 1900 or year > current_year + 1:
            raise ValidationError(f'Año debe estar entre 1900 y {current_year + 1}')

