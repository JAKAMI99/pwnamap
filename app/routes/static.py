from flask import render_template, send_from_directory, Blueprint
from .auth import login_required
import os

static_bp = Blueprint('static', __name__)

@static_bp.route('/')
@login_required
def index():
    return render_template('index.html')

@static_bp.route('/pwnamap')
@login_required
def pwnamap():
    return render_template('pwnamap.html')

@static_bp.route('/explore')
@login_required
def exploremap():
    return render_template('explore.html')

@static_bp.route('/tools')
@login_required
def tools():
    return render_template('tools.html')

@static_bp.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@static_bp.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(static_bp.root_path, 'images'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')