from flask import render_template, flash, redirect, url_for, request, Blueprint, current_app
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from . import db
from .utils import process_phone_number
from .models import Users, Transactions
from .forms import UserForm, TransactionForm, LoginForm
from collections import defaultdict
from datetime import datetime
import os
import uuid

main = Blueprint('main', __name__)

DEFAULT_PIC = "profile/profile-user.png"


@main.route('/user/add', methods=['GET', 'POST'])
def add_user():
    form = UserForm()

    if form.validate_on_submit():
        existing_user = Users.query.filter_by(email=form.email.data).first()

        if existing_user is None:
            try:
                # Process and validate the phone number
                phone = process_phone_number(form.phone.data)

                # Handle profile picture upload
                image = request.files.get('profile_pic')
                if image and image.filename != '':
                    pic_filename = secure_filename(image.filename)
                    pic_name = f"profile/{uuid.uuid4()}_{pic_filename}"
                    image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], pic_name))
                else:
                    pic_name = DEFAULT_PIC  # Set to a default image

                # Create and add the new user
                new_user = Users(
                    id=str(uuid.uuid4()),
                    first_name=form.first_name.data.title(),
                    last_name=form.last_name.data.title(),
                    username=form.username.data,
                    email=form.email.data,
                    balance=0,
                    phone=phone,
                    password_hash=generate_password_hash(form.password.data),
                    profile_pic=pic_name,
                )
                db.session.add(new_user)
                db.session.commit()

                flash("User added successfully!", "success")
                return redirect(url_for('main.login'))
            except ValueError as e:
                flash(str(e), "danger")
        else:
            flash("Email already registered.", "danger")

    our_users = Users.query.order_by(Users.date_added).all()
    return render_template("add_user.html", form=form, our_users=our_users)


# Create login page
@main.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            # Check the hash
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                return redirect(url_for("main.index"))
            else:
                flash("Wrong Details - Try Again!")
        else:
            flash("Wrong Details - Try Again!")
    return render_template("login.html", form=form)


# Create logout page
@main.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("You just logged out!")
    return redirect(url_for("main.login"))


@main.route('/get_latest_data')
@login_required
def get_latest_data():
    user = Users.query.get(current_user.id)
    monthly_data = defaultdict(lambda: {'income': 0, 'expense': 0})

    for transaction in user.transactions:
        month = transaction.date_added.month - 1  # Adjusting month to be 0-indexed for use in charts
        if transaction.trans_type.lower() == 'income':
            monthly_data[month]['income'] += transaction.amount
        elif transaction.trans_type.lower() == 'expense':
            monthly_data[month]['expense'] += transaction.amount

    data = {
        'balance': user.balance,
        'income_data': [monthly_data[month]['income'] for month in range(12)],
        'expense_data': [monthly_data[month]['expense'] for month in range(12)],
        'income_sum': sum([monthly_data[month]['income'] for month in range(12)]),
        'expense_sum': sum([monthly_data[month]['expense'] for month in range(12)]),
    }
    return data


# Create route decorators
@main.route("/")
@login_required
def index():
    # user_transactions = Transactions.query.order_by(Transactions.date_added.desc()).limit(limit=4)
    user_transactions = Transactions.query.order_by(Transactions.date_added.desc()).where(
        Transactions.user_id == current_user.id).limit(limit=4)
    user = Users.query.get(current_user.id)

    # Group transactions by month and type
    monthly_data = defaultdict(lambda: {'income': 0, 'expense': 0, 'balance': user.balance})

    for transaction in user.transactions:
        month = transaction.date_added.month
        if transaction.trans_type.lower() == 'income':
            monthly_data[month]['income'] += transaction.amount
        elif transaction.trans_type.lower() == 'expense':
            monthly_data[month]['expense'] += transaction.amount

    # Prepare data for the chart
    income_data = [monthly_data.get(month, {}).get('income', 0) for month in range(1, 13)]
    expense_data = [monthly_data.get(month, {}).get('expense', 0) for month in range(1, 13)]
    balance_data = [monthly_data[month]['balance'] for month in range(1, 13)]

    # Detect overspending by comparing expenses and income
    overspending = any(monthly_data[month]['expense'] > monthly_data[month]['income'] for month in range(1, 13))
    date = datetime.now().year
    return render_template("index.html", user_transactions=user_transactions, date=date,
                           income_data=income_data, expense_data=expense_data, balance=balance_data, user=user,
                           overspending=overspending)


@main.route("/help-center")
def help_center():
    date = datetime.now().year
    return render_template("help-center.html", date=date)


@main.route("/profile")
@login_required
def profile():
    date = datetime.now().year
    return render_template("profile.html", date=date)


@main.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    form = UserForm()
    user_to_update = Users.query.get_or_404(current_user.id)

    if request.method == "POST":
        user_to_update.first_name = form.first_name.data
        user_to_update.last_name = form.last_name.data
        user_to_update.email = form.email.data
        user_to_update.phone = form.phone.data

        # Check if a new profile picture is uploaded
        if 'profile_pic' in request.files:
            profile_pic_file = request.files['profile_pic']

            if profile_pic_file and profile_pic_file.filename != '':
                # Handle new profile picture upload
                pic_filename = secure_filename(profile_pic_file.filename)
                pic_name = "profile/" + str(current_user.id) + '_' + pic_filename
                pic_path = os.path.join(current_app.config['UPLOAD_FOLDER'], pic_name)
                profile_pic_file.save(pic_path)
                user_to_update.profile_pic = pic_name

        try:
            db.session.commit()
            flash("Profile Updated Successfully", "success")
            return redirect(url_for('main.settings'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating profile: {str(e)}", "danger")
            return redirect(url_for('main.settings'))

    else:
        form.first_name.data = user_to_update.first_name
        form.last_name.data = user_to_update.last_name
        form.email.data = user_to_update.email
        form.phone.data = user_to_update.phone
        date = datetime.now().year
        return render_template("setting.html", date=date, form=form)


# Get the individual transaction details and update transaction record in the database
@main.route('/transaction/<string:transaction_id>', methods=["GET", "POST"])
@login_required
def transaction_detail(transaction_id):
    transaction = Transactions.query.get_or_404(transaction_id)
    form = TransactionForm()

    if request.method == "POST":
        if current_user.id == transaction.users.id:
            try:
                Transactions.update_transaction(transaction, form)
                flash("Transaction Updated Successfully")
                return redirect(url_for('main.wallet'))
            except Exception as e:
                db.session.rollback()
                flash(f"Error!!... There was a problem updating your record: {str(e)}")
        else:
            flash(f"You Are Not Authorized To Perform This Action")
            return redirect(url_for('main.wallet'))
    else:
        form.amount.data = transaction.amount
        form.trans_type.data = transaction.trans_type
        form.transaction_frequency.data = transaction.transaction_frequency
        form.duration.data = transaction.duration
        form.category.data = transaction.category
        form.description.data = transaction.description
        date = datetime.now().year
        return render_template('transaction_detail.html', transaction=transaction, form=form, date=date,
                               transaction_id=transaction.id)


@main.route("/wallet")
@login_required
def wallet():
    user = Users.query.get(current_user.id)
    user_transactions = Transactions.query.order_by(Transactions.date_added.desc()).where(
        Transactions.user_id == current_user.id)

    # Group transactions by month and type
    monthly_data = defaultdict(lambda: {'income': 0, 'expense': 0, 'balance': user.balance})

    for transaction in user.transactions:
        month = transaction.date_added.month
        if transaction.trans_type.lower() == 'income':
            monthly_data[month]['income'] += transaction.amount
        elif transaction.trans_type.lower() == 'expense':
            monthly_data[month]['expense'] += transaction.amount

    # Prepare data for the chart
    income_data = [monthly_data.get(month, {}).get('income', 0) for month in range(1, 13)]
    expense_data = [monthly_data.get(month, {}).get('expense', 0) for month in range(1, 13)]
    balance_data = [monthly_data[month]['balance'] for month in range(1, 13)]

    # Detect overspending by comparing expenses and income
    overspending = any(monthly_data[month]['expense'] > monthly_data[month]['income'] for month in range(1, 13))
    date = datetime.now().year
    month = datetime.now().month
    return render_template("wallet.html", user_transactions=user_transactions, date=date,
                           income_data=income_data, expense_data=expense_data, balance=balance_data, user=user,
                           overspending=overspending, month=month)


@main.route("/add-transaction", methods=['GET', 'POST'])
@login_required
def add_transaction_detail():
    form = TransactionForm()
    if form.validate_on_submit():
        try:
            Transactions.create_transaction(form, current_user)
            return redirect(url_for("main.wallet"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error!!... There was a problem adding your transaction: {str(e)}")
    date = datetime.now().year
    return render_template('transaction_form.html', form=form, date=date)


@main.route("/delete/<string:id>")
@login_required
def delete(id):
    transaction = Transactions.query.get_or_404(id)
    if current_user.id == transaction.users.id:
        try:
            Transactions.delete_transaction(transaction)
            return redirect(url_for('main.wallet'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error!!... There was a problem deleting your transaction: {str(e)}")
    else:
        flash(f"You Are Not Authorized To Perform This Action")
        return redirect(url_for('main.wallet'))


@main.route("/delete_user/<string:id>")
def delete_user(id):
    delete_users = Users.query.get_or_404(id)
    user_transactions = Transactions.query.where(Transactions.user_id == id)
    try:
        for tran in user_transactions:
            db.session.delete(tran)
        db.session.delete(delete_users)
        db.session.commit()
        return redirect(url_for('main.add_user'))
    except Exception as e:
        db.session.rollback()
        flash(f"Error!!... There was a problem deleting your record: {str(e)}")
        return redirect(url_for('main.add_user'))


# Create Custom Error Pages

# Invalid URL Page
@main.errorhandler(404)
def page_not_found(e):
    print(e)
    date = datetime.now().year
    return render_template("404.html", date=date), 404


# Internal Server Error Page
@main.errorhandler(500)
def page_not_found(e):
    print(e)
    date = datetime.now().year
    return render_template("500.html", date=date), 500
