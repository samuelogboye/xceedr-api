#!/usr/bin/env python3
from volumx import db
from volumx.models.base import BaseModel
from volumx.models.user import User

class Address(BaseModel):
    """Template for the Address Class"""
    __tablename__ = 'address'

    fullAddress = db.Column(db.String(255), nullable=False, unique=False)
    district = db.Column(db.String(255), nullable=False, unique=False)
    city = db.Column(db.String(255), nullable=False, unique=False)
    country = db.Column(db.String(50), nullable=False, unique=False)
    addressState = db.Column(db.String(255), nullable=False, unique=False)
    postalCode = db.Column(db.String(10), nullable=False, unique=False)
    directions = db.Column(db.String(255), nullable=False, unique=False)

class Contact(BaseModel):
    """Template for the Contact Class"""
    __tablename__ = 'contact'

    email = db.Column(db.String(255), nullable=False, unique=True)
    phoneCode = db.Column(db.Integer, nullable=False, unique=False)
    phoneNumber = db.Column(db.Integer, nullable=False, unique=True)
    addressId = db.Column(db.String(50), db.ForeignKey('address.id'))
    address = db.relationship('Address', backref='contact', uselist=False)

class Business(BaseModel):
    """Template for the Business Class"""
    __tablename__ = 'business'

    legalName = db.Column(db.String(50), nullable=False, unique=True)
    displayName = db.Column(db.String(50), nullable=False, unique=True)
    websiteLink = db.Column(db.String(255), nullable=False, unique=False)
    currency = db.Column(db.String(10), nullable=False, unique=False)
    businessType = db.Column(db.String(50), nullable=False, unique=False)
    businessGst = db.Column(db.String(50), nullable=False, unique=False)
    businessPan = db.Column(db.String(50), nullable=False, unique=False)
    businessLogo = db.Column(db.String(255), nullable=False, unique=False)
    orderSystem = db.Column(db.Boolean, default=True)
    contactId = db.Column(db.String, db.ForeignKey('contact.id'))
    contact = db.relationship('Contact', backref='business', uselist=False)


class BusinessUserRights(BaseModel):
    """Template for the BusinessUserRights Class"""
    __tablename__ = 'business_user_rights'

    businessId = db.Column(db.String(50), db.ForeignKey('business.id'),primary_key=True)
    userId = db.Column(db.String(50), db.ForeignKey('user.id'),primary_key=True)
    productRights = db.Column(db.Boolean, default=True)
    inventoryRights = db.Column(db.Boolean, default=True)
    salesRights = db.Column(db.Boolean, default=True)
    salesPosRights = db.Column(db.Boolean, default=True)
    suppliersRights = db.Column(db.Boolean, default=True)
    analyticsViewRights = db.Column(db.Boolean, default=True)
    ownerRights = db.Column(db.Boolean, default=True)
