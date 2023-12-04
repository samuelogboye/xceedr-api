from flask import Blueprint, jsonify, send_file, request, url_for, send_from_directory, current_app
from werkzeug.utils import secure_filename
from volumx.auth import login_required
import os
from volumx import db
from dotenv import load_dotenv
import cloudinary.uploader
from volumx.models.user import User


load_dotenv(".env")


util_bp = Blueprint('util', __name__)

@util_bp.route('/logs')
def get_logs():
    try:
        access_log_path = 'access_log.log'
        error_log_path = 'error_log.log'

        access_content = ''
        error_content = ''

        with open(access_log_path, 'r') as access_file:
            access_content = access_file.read()

        with open(error_log_path, 'r') as error_file:
            error_content = error_file.read()

        combined_content = f'Access Log:\n\n{access_content}\n\nError Log:\n\n{error_content}'

        return combined_content, 200, {'Content-Type': 'text/plain', 'Content-Disposition': 'attachment; filename=combined_logs.txt'}
    except FileNotFoundError:
        return "Log files not found", 404
    except Exception as e:
        return str(e), 500

# Route for cron job
@util_bp.route('/cron', methods=['GET'])
def cron_job():
    # Query the first user
    user = User.query.first()
    response = {'message': 'Everything is working fine', 'data': user.format()}
    return jsonify(response)

