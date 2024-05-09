from flask import Flask
import os, logging

#Logging config
from . import logging_config

log = logging.getLogger(__name__)


# Routes
from .routes.auth import auth_bp
from .routes.api import api_bp
from .routes.static import static_bp
from .routes.dynamic import dynamic_bp
from .routes.setup import setup_bp



required_directories = [ #Except logging, will be created trough logging_config
    'app/data',  # data dir
    'app/data/handshakes',  # Subdirectory for handshakes from pwnagotchi
    'app/data/wigle/raw_kml/', # Archive for old Downloads to now which are already downloaded
    'app/data/wigle/new_kml',  # for new Wigle Downloads
    'app/data/wardrive',       # for the wardrive map
]

def create_app():
    app = Flask(__name__)
    if not app.secret_key:
        
        app.secret_key = os.urandom(24) #generate secret key for signing cookies
    
    for dir_path in required_directories:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)  # Create the directory if it doesn't exist
            log.info(f"Setup: Created missing directory: {dir_path}")
    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(static_bp)
    app.register_blueprint(dynamic_bp)
    app.register_blueprint(setup_bp)

 

    return app