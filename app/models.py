from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
import uuid


class Users(db.Model, UserMixin):
    id = db.Column(db.VARCHAR(60), primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    first_name = db.Column(db.String(200), nullable=False)
    last_name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(180), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=False)
    balance = db.Column(db.Integer, default=0, nullable=False)
    profile_pic = db.Column(db.String(100), nullable=True)
    date_added = db.Column(db.DateTime, default=datetime.now)
    password_hash = db.Column(db.String(180), nullable=False)
    transactions = db.relationship('Transactions', backref='users', lazy=True)

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute!!")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def update_balance(self):
        income = sum([txn.amount for txn in self.transactions if txn.trans_type == 'Income'])
        expense = sum([txn.amount for txn in self.transactions if txn.trans_type == 'Expense'])
        self.balance = income - expense
        db.session.commit()

    def __repr__(self):
        return '<Name %r>' % self.name


class Transactions(db.Model):
    id = db.Column(db.VARCHAR(60), primary_key=True)
    amount = db.Column(db.Integer, nullable=False)
    trans_type = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(150), nullable=False)
    transaction_frequency = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(25), nullable=True)
    duration = db.Column(db.Integer, nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.VARCHAR(60), db.ForeignKey('users.id'), nullable=False)

    @staticmethod
    def create_transaction(form, user):
        new_transaction = Transactions(
            id=str(uuid.uuid4()),
            amount=form.amount.data,
            trans_type=form.trans_type.data,
            category=form.category.data,
            transaction_frequency=form.transaction_frequency.data,
            duration=form.duration.data,
            description=form.description.data,
            user_id=user.id,
        )
        db.session.add(new_transaction)
        user.update_balance()

    @staticmethod
    def update_transaction(transaction, form):
        transaction.amount = form.amount.data
        transaction.trans_type = form.trans_type.data
        transaction.transaction_frequency = form.transaction_frequency.data
        transaction.duration = form.duration.data
        transaction.category = form.category.data
        transaction.description = form.description.data
        db.session.commit()
        transaction.users.update_balance()

    @staticmethod
    def delete_transaction(transaction):
        db.session.delete(transaction)
        transaction.users.update_balance()

    def __repr__(self):
        return '<Transaction %r>' % self.id
