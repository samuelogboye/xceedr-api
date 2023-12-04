#!/usr/bin/env python3
"""Template for the User Class"""
from volumx import db
from flask_login import UserMixin
from volumx.models.base import BaseModel


class User(UserMixin, BaseModel):
    __tablename__ = 'users'

    email = db.Column(db.String(255), unique=True, nullable=False)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(500), nullable=False)
    email_confirmed = db.Column(db.Boolean, default=False)
    otp = db.Column(db.String(6), default=None)
    otp_expiry = db.Column(db.DateTime, default=None)
    profile_picture = db.Column(db.String(255), default='http://res.cloudinary.com/dbn9ejpno/image/upload/v1700666059/iuqjx3u5ts4tpvofhdnn.png')
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)

    # Relationship with BusinessUserRights (One-to-One)
    business_user_rights = db.relationship('BusinessUserRights', backref='user', uselist=False)


    def __init__(self, email, first_name, last_name, password, email_confirmed=False, otp=None, otp_expiry=None, profile_picture='http://res.cloudinary.com/dbn9ejpno/image/upload/v1700666059/iuqjx3u5ts4tpvofhdnn.png', is_active=True, is_admin=False):
        super().__init__()
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.password = password
        self.email_confirmed = email_confirmed
        self.otp = otp
        self.otp_expiry = otp_expiry
        self.profile_picture = profile_picture
        self.is_active = is_active
        self.is_admin = is_admin


    def __repr__(self):
        return f'<User {self.username}>'

    def format(self):
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email_confirmed': self.email_confirmed,
            'profile_picture': self.profile_picture,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'createdAt': self.createdAt,
            'updatedAt': self.updatedAt,
        }