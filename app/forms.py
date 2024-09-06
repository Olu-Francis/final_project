from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, IntegerField, TextAreaField, TelField, PasswordField
from wtforms.validators import DataRequired, EqualTo
from flask_wtf.file import FileField

TYPE_CHOICES = [(None, 'Select a type'), ('Income', 'Income'), ('Expense', 'Expenses')]
CATEGORY_CHOICES = [(None, 'Select a type'), ('Freelance Job', 'Freelance Job'), ('Salary', 'Salary'), ('Gift', 'Gift'),
                    ('Groceries', 'Groceries'), ('Utilities', 'Utilities'), ('Travel', 'Travel'),
                    ('Miscellaneous', 'Miscellaneous'), ('Mortgage', 'Mortgage'), ('Weekend Fun', 'Weekend Fun'),
                    ('Transportation', 'Transportation'), ('Dates', 'Dates'),
                    ('Vehicle Maintenance', 'Vehicle Maintenance'), ('Vehicle Repairs', 'Vehicle Repairs'),
                    ('School Fees', 'School Fees'), ('Take-outs', 'Take-outs'), ('Bills', 'Bills'),
                    ('Rent', 'Rent'), ('Coffee, Teas, etc', 'Morning Rituals (coffee, tea,...)')]
RECURRING_CHOICES = [(None, 'Select a type'), ('Annually', 'Annually'), ('Quarterly', 'Quarterly'),
                     ('Trimester', 'Trimester'), ('Semester', 'Semester'), ('Monthly', 'Monthly'),
                     ('Fortnightly', 'Fortnightly'), ('Weekly', 'Weekly'), ('Once', 'Once')]
DURATION_CHOICES = [(None, 'Select a type'), (0, 'Once'), (1, 'A Month'), (2, 'Two Months'), (3, 'Three Months'),
                    (4, 'Four Months'), (5, 'Five Months'), (6, 'Six Months'), (7, 'Seven Months'), (8, 'Eight Months'),
                    (9, 'Nine Months'), (10, '10 Months'), (11, '11 Months'), (12, '12 Months')]


class UserForm(FlaskForm):
    first_name = StringField(label="First Name", validators=[DataRequired()])
    last_name = StringField(label="Last Name", validators=[DataRequired()])
    username = StringField(label="Username", validators=[DataRequired()])
    email = StringField(label="Email", validators=[DataRequired()])
    phone = TelField(label="Phone")
    profile_pic = FileField(label="Profile Pic")
    password = PasswordField(label="Password",
                             validators=[DataRequired(), EqualTo("password1", message="Password Must Match")])
    password1 = PasswordField(label="Re-enter Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


class TransactionForm(FlaskForm):
    amount = IntegerField(label="Amount", validators=[DataRequired()])
    trans_type = SelectField(label="Transaction Type", choices=TYPE_CHOICES, validators=[DataRequired()])
    category = SelectField(label="Category", choices=CATEGORY_CHOICES, validators=[DataRequired()])
    transaction_frequency = SelectField(label="Frequency Of This Transaction", choices=RECURRING_CHOICES,
                                        validators=[DataRequired()])
    duration = SelectField(label="Duration Of This Transaction", choices=DURATION_CHOICES, validators=[DataRequired()])
    description = TextAreaField(label="Additional Details")
    submit = SubmitField("Submit")


class PasswordForm(FlaskForm):
    email = StringField("What's Your Email", validators=[DataRequired()])
    password = PasswordField("What's Your Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


class LoginForm(FlaskForm):
    username = StringField(label="Username", validators=[DataRequired()])
    password = PasswordField(label="Password", validators=[DataRequired()])
    submit = SubmitField("Submit")
