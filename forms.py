# Import base form class from Flask-WTF
from flask_wtf import FlaskForm

# Import different types of form fields
from wtforms import StringField, PasswordField, SubmitField, BooleanField

# Import built-in validators for checking form input
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Optional, Length

# Import the User model to check for existing users during validation
from models import User


class RegisterForm(FlaskForm):
    # Email field (required + must be a valid email format)
    email = StringField("Email", validators=[DataRequired(), Email()])

    # Password field (required)
    password = PasswordField("Password", validators=[DataRequired()])

    # Confirm password must match the 'password' field
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match"),
        ],
    )

    # Submit button
    submit = SubmitField("Register")

    # Custom validator: check if the email is already in use
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("This email is already registered.")


class LoginForm(FlaskForm):
    # Email field (required + must be valid format)
    email = StringField("Email", validators=[DataRequired(), Email()])

    # Password field (required)
    password = PasswordField("Password", validators=[DataRequired()])

    # Submit button
    submit = SubmitField("Login")
            
class EditAccountForm(FlaskForm):
    # Email field for changing the user's email (required)
    email = StringField("Email", validators=[DataRequired(), Email()])

    # Current password field (optional, used for verifying before changing password)
    current_password = PasswordField("Current Password", validators=[Optional()])

    # New password field (optional, min length for security)
    new_password = PasswordField("New Password", validators=[Optional(), Length(min=6)])

    # Confirmation of new password (must match new_password)
    confirm_new_password = PasswordField("Confirm New Password", validators=[
        Optional(), EqualTo("new_password", message="Passwords must match")
    ])

    # Submit button
    submit = SubmitField("Update")

    def __init__(self, original_email, *args, **kwargs):
        # Store the original email for validation (so user can keep same email)
        super().__init__(*args, **kwargs)
        self.original_email = original_email

    def validate_email(self, email):
        # If the email was changed, make sure it's not taken by someone else
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError("This email is already registered.")
