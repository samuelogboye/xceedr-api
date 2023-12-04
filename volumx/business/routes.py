from flask import Blueprint, request, jsonify
from volumx.models.business import Business, Contact, Address, BusinessUserRights
from volumx import db
from volumx.business.business_schemas import IdSchema
from datetime import datetime, timedelta
from uuid import UUID


# Create a Blueprint for business routes
business_bp = Blueprint('business', __name__, url_prefix='/api/v1/business')


