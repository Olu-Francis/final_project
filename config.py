import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or "uyfhgfcnbfbgfdgfdhbdfgfdgf"
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:rootpass@localhost/final_test'
    # SQLALCHEMY_DATABASE_URI = (os.environ.get('DATABASE_URL') or 'postgres://u8h5sba9et57jt')
    UPLOAD_FOLDER = "app/static/images/"
