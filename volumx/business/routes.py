from flask import Blueprint, request, jsonify
from volumx.models.business import Business, Contact, Address, BusinessUserRights
from volumx.models.user import User
from volumx import db
from volumx.business.business_schemas import IdSchema
from datetime import datetime, timedelta
from uuid import UUID


# Create a Blueprint for business routes
business_bp = Blueprint('business', __name__, url_prefix='/api/v1/business')


# Route to get a single business data by id
@business_bp.route('/<business_id>', methods=['GET'])
def get_business_data(business_id):
    business = Business.query.get(business_id)

    if not business:
        return jsonify({"error": "Business not found"}), 404

    try:
        business_data = {
            "businessId": business.id,
            "legalName": business.legalName,
            "displayName": business.displayName,
            "websiteLink": business.websiteLink,
            "currency": business.currency,
            "businessType": business.businessType,
            "businessGst": business.businessGst,
            "businessPan": business.businessPan,
            "businessLogo": business.businessLogo,
            "orderSystem": business.orderSystem
        }

        contact_data = {
            "contactId": business.contact.id,
            "email": business.contact.email,
            "phoneCode": business.contact.phoneCode,
            "phoneNumber": business.contact.phoneNumber
        }

        address_data = {
            "addressId": business.contact.address.id,
            "fullAddress": business.contact.address.fullAddress,
            "district": business.contact.address.district,
            "city": business.contact.address.city,
            "country": business.contact.address.country,
            "addressState": business.contact.address.addressState,
            "postalCode": business.contact.address.postalCode,
            "directions": business.contact.address.directions
        }

        business_data['contact'] = contact_data
        business_data['contact']['address'] = address_data

        return jsonify(business_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 404


# Route to get all businesses data
@business_bp.route('/', methods=['GET'])
def get_all_business_data():
    businesses = Business.query.all()

    if not businesses:
        return jsonify({"error": "Businesses not found", "businessesData": []}), 404

    try:
        businesses_data = []

        for business in businesses:
            business_data = {
                "businessId": business.id,
                "legalName": business.legalName,
                "displayName": business.displayName,
                "websiteLink": business.websiteLink,
                "currency": business.currency,
                "businessType": business.businessType,
                "businessGst": business.businessGst,
                "businessPan": business.businessPan,
                "businessLogo": business.businessLogo,
                "orderSystem": business.orderSystem
            }

            contact_data = {
                "contactId": business.contact.id,
                "email": business.contact.email,
                "phoneCode": business.contact.phoneCode,
                "phoneNumber": business.contact.phoneNumber
            }

            address_data = {
                "addressId": business.contact.address.id,
                "fullAddress": business.contact.address.fullAddress,
                "district": business.contact.address.district,
                "city": business.contact.address.city,
                "country": business.contact.address.country,
                "addressState": business.contact.address.addressState,
                "postalCode": business.contact.address.postalCode,
                "directions": business.contact.address.directions
            }

            business_data['contact'] = contact_data
            business_data['contact']['address'] = address_data

            businesses_data.append(business_data)

        return jsonify(businesses_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 404

# Route to create a new business
@business_bp.route('/', methods=['POST'])
def create_business():
    try:
        data = request.json

        # Validate the data
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Throw an error if any of the required fields are missing
        required_fields = ['legalName', 'displayName', 'websiteLink', 'currency', 'businessType', 'businessGst', 'businessPan', 'businessLogo', 'orderSystem', 'email', 'phoneCode', 'phoneNumber', 'fullAddress', 'district', 'city', 'country', 'addressState', 'postalCode', 'directions', 'userId', 'productRights', 'inventoryRights', 'salesRights', 'salesPosRights', 'suppliersRights', 'analyticsViewRights', 'ownerRights', 'userId']
        for field in required_fields:
                if field not in data:
                        return jsonify({"error": f"{field} is required"}), 400

        # Check if the user exists
        user = User.query.get(data['userId'])
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Check if the user exists by checking email and phone number in Contact Model
        email_exists = Contact.query.filter_by(email=data['email']).first()
        phone_exists = Contact.query.filter_by(phoneNumber=data['phoneNumber']).first()
        print(email_exists)
        print(phone_exists)

        if email_exists or phone_exists:
            return jsonify({"error": "Business already exists with the same email and phone number"}), 409


        # Check if the business already exists
        legal_name_exists = Business.query.filter_by(legalName=data['legalName']).first()
        display_name_exists = Business.query.filter_by(displayName=data['displayName']).first()
        if legal_name_exists or display_name_exists:
            return jsonify({"error": "Business already exists with the same Legal name and display name"}), 409

        # Create a new address
        address = Address(
            fullAddress=data['fullAddress'],
            district=data['district'],
            city=data['city'],
            country=data['country'],
            addressState=data['addressState'],
            postalCode=data['postalCode'],
            directions=data['directions']
        )
        address.insert()

        # Create a new contact
        contact = Contact(
            email=data['email'],
            phoneCode=data['phoneCode'],
            phoneNumber=data['phoneNumber'],
            addressId=address.id
        )
        contact.insert()

        # Create a new business
        business = Business(
            legalName=data['legalName'],
            displayName=data['displayName'],
            websiteLink=data['websiteLink'],
            currency=data['currency'],
            businessType=data['businessType'],
            businessGst=data['businessGst'],
            businessPan=data['businessPan'],
            businessLogo=data['businessLogo'],
            orderSystem=data['orderSystem'],
            contactId=contact.id
        )
        business.insert()

        # Create a new business user rights
        business_user_rights = BusinessUserRights(
            businessId=business.id,
            userId=data['userId'],
            productRights=data['productRights'],
            inventoryRights=data['inventoryRights'],
            salesRights=data['salesRights'],
            salesPosRights=data['salesPosRights'],
            suppliersRights=data['suppliersRights'],
            analyticsViewRights=data['analyticsViewRights'],
            ownerRights=data['ownerRights']
        )
        business_user_rights.insert()

        return jsonify({"message": "Business created successfully", "businessId": business.id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Route to update a business
@business_bp.route('/<business_id>', methods=['PUT'])
def update_business(business_id):
    try:
        data = request.json

        # Validate the data
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Throw an error if any of the required fields are missing
        required_fields = ['legalName', 'displayName', 'websiteLink', 'currency', 'businessType', 'businessGst', 'businessPan', 'businessLogo', 'orderSystem', 'email', 'phoneCode', 'phoneNumber', 'fullAddress', 'district', 'city', 'country', 'addressState', 'postalCode', 'directions', 'userId', 'productRights', 'inventoryRights', 'salesRights', 'salesPosRights', 'suppliersRights', 'analyticsViewRights', 'ownerRights', 'userId']
        for field in required_fields:
                if field not in data:
                        return jsonify({"error": f"{field} is required"}), 400

        # Check if the user exists
        user = User.query.get(data['userId'])
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Check if the business exists
        business = Business.query.get(business_id)
        if not business:
            return jsonify({"error": "Business not found"}), 404

        # Check if the user exists by checking email and phone number in Contact Model
        email_exists = Contact.query.filter_by(email=data['email']).first()
        phone_exists = Contact.query.filter_by(phoneNumber=data['phoneNumber']).first()
        print(email_exists)
        print(phone_exists)

        if email_exists or phone_exists:
            return jsonify({"error": "Business already exists with the same email and phone number"}), 409


        # Check if the business already exists
        legal_name_exists = Business.query.filter_by(legalName=data['legalName']).first()
        display_name_exists = Business.query.filter_by(displayName=data['displayName']).first()
        if legal_name_exists or display_name_exists:
            return jsonify({"error": "Business already exists with the same Legal name and display name"}), 409


        # Check if the business exists
        business = Business.query.get(business_id)
        if not business:
            return jsonify({"error": "Business not found"}), 404

        # Update the business
        business.legalName = data['legalName']
        business.displayName = data['displayName']
        business.websiteLink = data['websiteLink']
        business.currency = data['currency']
        business.businessType = data['businessType']
        business.businessGst = data['businessGst']
        business.businessPan = data['businessPan']
        business.businessLogo = data['businessLogo']
        business.orderSystem = data['orderSystem']
        business.update()

        # Update the address
        address = Address.query.get(business.contact.addressId)
        address.fullAddress = data['fullAddress']
        address.district = data['district']
        address.city = data['city']
        address.country = data['country']
        address.addressState = data['addressState']
        address.postalCode = data['postalCode']
        address.directions = data['directions']
        address.update()

        # Update the contact
        contact = Contact.query.get(business.contactId)
        contact.email = data['email']
        contact.phoneCode = data['phoneCode']
        contact.phoneNumber = data['phoneNumber']
        contact.update()

        # Update the business user rights
        business_user_rights = BusinessUserRights.query.filter_by(businessId=business.id, userId=data['userId']).first()
        if not business_user_rights:
            return jsonify({"error": "Business user rights not found"}), 404
        business_user_rights.productRights = data['productRights']
        business_user_rights.inventoryRights = data['inventoryRights']
        business_user_rights.salesRights = data['salesRights']
        business_user_rights.salesPosRights = data['salesPosRights']
        business_user_rights.suppliersRights = data['suppliersRights']
        business_user_rights.analyticsViewRights = data['analyticsViewRights']
        business_user_rights.ownerRights = data['ownerRights']
        business_user_rights.update()

        return jsonify({"message": "Business updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Route to update a business PATCH
@business_bp.route('/<business_id>', methods=['PATCH'])
def patch_business(business_id):
    try:
        data = request.json

        # Validate the data
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Check if the business exists
        business = Business.query.get(business_id)
        if not business:
            return jsonify({"error": "Business not found"}), 404

        # Update the business
        for field in ['legalName', 'displayName', 'websiteLink', 'currency', 'businessType', 'businessGst', 'businessPan', 'businessLogo', 'orderSystem']:
             if field in data:
                  setattr(business, field, data[field])

        business.update()

        # Update the address
        for field in ['fullAddress', 'district', 'city', 'country', 'addressState', 'postalCode', 'directions']:
             if field in data:
                  setattr(business.contact.address, field, data[field])

        business.contact.address.update()

        # Update the contact
        for field in ['email', 'phoneCode', 'phoneNumber']:
             if field in data:
                  setattr(business.contact, field, data[field])

        business.contact.update()

        return jsonify({"message": "Business patched successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Route to delete a business
@business_bp.route('/<business_id>', methods=['DELETE'])
def delete_business(business_id):
    try:
        # Check if the business exists
        business = Business.query.get(business_id)
        if not business:
            return jsonify({"error": "Business not found"}), 404

        # Delete the business user rights
        business_user_rights = BusinessUserRights.query.filter_by(businessId=business.id).first()
        business_user_rights.delete()

        # Delete the business
        business.delete()

        # Delete the contact
        contact = Contact.query.get(business.contactId)
        contact.delete()

        # Delete the address
        address = Address.query.get(contact.addressId)
        address.delete()

        return jsonify({"message": "Business deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Works
# Route to get the Business User Rights by User ID
@business_bp.route('/user_rights/<user_id>', methods=['GET'])
def get_business_user_rights(user_id):
    try:
        # Check if the user exists
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get the business user rights
        business_user_rights = BusinessUserRights.query.filter_by(userId=user.id).all()
        if not business_user_rights:
            return jsonify({"error": "Business user rights not found"}), 404

        business_user_rights_data = []

        for business_user_right in business_user_rights:
            business_user_right_data = {
                "businessId": business_user_right.businessId,
                "userId": business_user_right.userId,
                "productRights": business_user_right.productRights,
                "inventoryRights": business_user_right.inventoryRights,
                "salesRights": business_user_right.salesRights,
                "salesPosRights": business_user_right.salesPosRights,
                "suppliersRights": business_user_right.suppliersRights,
                "analyticsViewRights": business_user_right.analyticsViewRights,
                "ownerRights": business_user_right.ownerRights
            }

            business_user_rights_data.append(business_user_right_data)

        return jsonify(business_user_rights_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# WOrks
# Route to get all Business User Rights
@business_bp.route('/user_rights', methods=['GET'])
def get_all_business_user_rights():
    try:
        # Get the business user rights
        business_user_rights = BusinessUserRights.query.all()
        if not business_user_rights:
            return jsonify({"error": "Business user rights not found"}), 404

        business_user_rights_data = []

        for business_user_right in business_user_rights:
            business_user_right_data = {
                "id": business_user_right.id,
                "businessId": business_user_right.businessId,
                "userId": business_user_right.userId,
                "productRights": business_user_right.productRights,
                "inventoryRights": business_user_right.inventoryRights,
                "salesRights": business_user_right.salesRights,
                "salesPosRights": business_user_right.salesPosRights,
                "suppliersRights": business_user_right.suppliersRights,
                "analyticsViewRights": business_user_right.analyticsViewRights,
                "ownerRights": business_user_right.ownerRights
            }

            business_user_rights_data.append(business_user_right_data)

        return jsonify(business_user_rights_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Works
# Route to get the Business User Rights by Business ID
@business_bp.route('/<business_id>/user_rights', methods=['GET'])
def get_business_user_rights_by_business_id(business_id):
    try:
        # Check if the business exists
        business = Business.query.get(business_id)
        if not business:
            return jsonify({"error": "Business not found"}), 404

        # Get the business user rights
        business_user_rights = BusinessUserRights.query.filter_by(businessId=business.id).all()
        if not business_user_rights:
            return jsonify({"error": "Business user rights not found"}), 404

        business_user_rights_data = []

        for business_user_right in business_user_rights:
            business_user_right_data = {
                "id": business_user_right.id,
                "businessId": business_user_right.businessId,
                "userId": business_user_right.userId,
                "productRights": business_user_right.productRights,
                "inventoryRights": business_user_right.inventoryRights,
                "salesRights": business_user_right.salesRights,
                "salesPosRights": business_user_right.salesPosRights,
                "suppliersRights": business_user_right.suppliersRights,
                "analyticsViewRights": business_user_right.analyticsViewRights,
                "ownerRights": business_user_right.ownerRights
            }

            business_user_rights_data.append(business_user_right_data)

        return jsonify(business_user_rights_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Works
# Route to update a business user rights by business ID PATCH
@business_bp.route('/<business_id>/user_rights', methods=['PATCH'])
def patch_business_user_rights_by_business_id(business_id):
    try:
        data = request.json

        # Validate the data
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Check if the business exists
        business = Business.query.get(business_id)
        if not business:
            return jsonify({"error": "Business not found"}), 404

        # Update the business user rights
        business_user_rights = BusinessUserRights.query.filter_by(businessId=business_id).first()
        for field in ['productRights', 'inventoryRights', 'salesRights', 'salesPosRights', 'suppliersRights', 'analyticsViewRights', 'ownerRights', 'userId']:
             if field in data:
                  setattr(business_user_rights, field, data[field])

        business_user_rights.update()

        business_user_right_data = {
                "id": business_user_rights.id,
                "businessId": business_user_rights.businessId,
                "userId": business_user_rights.userId,
                "productRights": business_user_rights.productRights,
                "inventoryRights": business_user_rights.inventoryRights,
                "salesRights": business_user_rights.salesRights,
                "salesPosRights": business_user_rights.salesPosRights,
                "suppliersRights": business_user_rights.suppliersRights,
                "analyticsViewRights": business_user_rights.analyticsViewRights,
                "ownerRights": business_user_rights.ownerRights
            }

        return jsonify({"message": "Business user rights patched successfully", "business_user_right": business_user_right_data}), 200
    except Exception as e:
        return jsonify({"errors": str(e)}), 400
