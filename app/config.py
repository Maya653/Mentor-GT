import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, '..', 'instance', 'academic.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload settings
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'png'}
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # APIs Externas
    GOOGLE_SCHOLAR_API = os.environ.get('GOOGLE_SCHOLAR_API', '')
    
    # ORCID
    ORCID_ID = os.environ.get('ORCID_ID', '')
    
    # SCOPUS - Elsevier
    SCOPUS_API_KEY = os.environ.get('SCOPUS_API_KEY', '')
    SCOPUS_AUTHOR_ID = os.environ.get('SCOPUS_AUTHOR_ID', '')
    
    # PUBMED
    PUBMED_AUTHOR_QUERY = os.environ.get('PUBMED_AUTHOR_QUERY', '')
    
    # GROQ (Chatbot)
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')
