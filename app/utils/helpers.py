import os
from werkzeug.utils import secure_filename
from flask import current_app

def allowed_file(filename):
    """Verifica si el archivo tiene una extensión permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_uploaded_file(file, subfolder=''):
    """Guarda un archivo subido"""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_folder = current_app.config['UPLOAD_FOLDER']
        if subfolder:
            upload_folder = os.path.join(upload_folder, subfolder)
        
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        return filepath
    return None

def format_date(date, format='%d/%m/%Y'):
    """Formatea una fecha"""
    if date:
        return date.strftime(format)
    return ''

def truncate_text(text, length=100):
    """Trunca un texto a una longitud máxima"""
    if text and len(text) > length:
        return text[:length] + '...'
    return text or ''

def get_file_size(filepath):
    """Obtiene el tamaño de un archivo en bytes"""
    try:
        return os.path.getsize(filepath)
    except:
        return 0

