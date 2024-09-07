import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or "uyfhgfcnbfbgfdgfdhbdfgfdgf"
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:rootpass@localhost/final_test'
    SQLALCHEMY_DATABASE_URI = (os.environ.get('DATABASE_URL') or
                               'postgres://u8h5sba9et57jt'
                               ':pc0db8c36946c8a81591d18c1167f1a8f14906acabfc0970c09bc6fa76ac90cf4@c5p86clmevrg5s'
                               '.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/dcuke0qr6e4a0o')
