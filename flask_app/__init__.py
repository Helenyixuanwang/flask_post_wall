import os
from flask import Flask
from flask_mail import Mail  # ADD THIS IMPORT

# Optional: Add dotenv support for local development
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables from .env file if it exists
except ImportError:
    # dotenv package not installed, that's fine for production
    pass

app = Flask(__name__)

# Use a more secure default key (though in production, always use an environment variable)
app.secret_key = os.environ.get('SECRET_KEY', 'b9584e1c6d9fd124aae40e5043f821a5e70e15b33fbd2c59')

# SENDGRID EMAIL CONFIGURATION
# Currently using Single Sender Verification (314piettjj@gmail.com)
# TODO: Switch to domain authentication before production deployment
app.config['MAIL_SERVER'] = 'smtp.sendgrid.net'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'apikey'  # Literally the word "apikey"
app.config['MAIL_PASSWORD'] = os.getenv('SENDGRID_API_KEY')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')# 314piettjj@gmail.com

mail = Mail(app)

# Your controller imports
from flask_app.controllers import user_controller  # or whatever your controller files are