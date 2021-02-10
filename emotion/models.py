# from flask_login import UserMixin
import jwt
import datetime
from flask_bcrypt import Bcrypt
from emotion import db
from flask import current_app, jsonify
from sqlalchemy.sql import func
import uuid
from sqlalchemy.dialects.postgresql import UUID



class Scope(db.Model):
    __tablename__ = 'scope'

    id_ = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())



class UserRole(db.Model):
    __tablename__ = 'user_role'

    id_ = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    scope_id = db.Column(db.Integer, db.ForeignKey('scope.id_'), nullable=False)
    scope = db.relationship("Scope")
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())



class Company(db.Model):
    __tablename__ = 'company'

    id_ = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    def __init__(self, name):
        self.name = name

    def as_dict(self):
        return {
            'id': self.id_,
            'name': self.name
        }



class FeelingFile(db.Model):
    __tablename__ = 'feeling_file'

    id_ = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uuid = db.Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True)
    name = db.Column(db.String(100), nullable=False)
    seen_count = db.Column(db.Integer, nullable=False, default=0)
    feeling_id = db.Column(UUID(as_uuid=True), db.ForeignKey('feeling.internal_uuid'), nullable=False)
    feeling = db.relationship("Feeling")

    def __init__(self, feeling, name):
        # self.uuid = str(uuid.uuid4())
        self.feeling = feeling
        self.name = name

    def as_dict(self):
        return {
            'uuid': self.uuid,
            'name': self.name
        }


class ContactChannel(db.Model):
    __tablename__ = 'contact_channel'

    id_ = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type_ = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    def __init__(self, type_):
        self.type_ = type_

    def as_dict(self):
        return {
            'id': self.id_,
            'type': self.type_
        }



class Receiver(db.Model):
    __tablename__ = 'receiver'

    id_ = db.Column(db.Integer, primary_key=True, autoincrement=True)
    contact_channel_id = db.Column(db.Integer, db.ForeignKey('contact_channel.id_'), nullable=False)
    contact_channel = db.relationship("ContactChannel")
    contact_channel_description = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    zipcode = db.Column(db.String(20), nullable=False)

    def __init__(self, contact_channel_id, contact_channel_description, address, zipcode):
        self.contact_channel_id = contact_channel_id
        self.contact_channel_description = contact_channel_description
        self.address = address
        self.zipcode = zipcode

    def as_dict(self):
        contact_channel_dict = self.contact_channel.as_dict()
        contact_channel_dict['description'] = self.contact_channel_description

        return {
            'id': self.id_,
            'contact_channel': contact_channel_dict,
            'address': self.address,
            'zipcode': self.zipcode
        }



class Feeling(db.Model):
    __tablename__ = 'feeling'

    id_ = db.Column(db.Integer, primary_key=True, autoincrement=True)
    internal_uuid = db.Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True)
    external_uuid = db.Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id_'), nullable=False)
    creator = db.relationship("User")
    receiver_id = db.Column(db.Integer, db.ForeignKey('receiver.id_'), nullable=False)
    receiver = db.relationship("Receiver")
    has_seen = db.Column(db.Boolean, nullable=False, default=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id_'), nullable=False)
    company = db.relationship("Company")
    order_id = db.Column(db.String(36), nullable=False)
    password = db.Column(db.String(255))
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())


    def __init__(self, creator, receiver, company_id, order_id, password=None):
        self.creator = creator
        self.receiver = receiver
        # self.internal_uuid = str(uuid.uuid4())
        # self.external_uuid = str(uuid.uuid4())
        self.company_id = company_id
        self.order_id = order_id
        if password == None:
            password = None
        else:
            print("asdasdasda")
            bcrypt = Bcrypt()
            self.password = bcrypt.generate_password_hash(
                password, current_app.config.get('BCRYPT_LOG_ROUNDS')
            ).decode()

    def as_dict(self):
        return {
            'id': self.id_,
            'internal_uuid': self.internal_uuid,
            'external_uuid': self.external_uuid,
            'receiver': self.receiver.as_dict(),
            'has_seen': self.has_seen,
            'order_id': self.order_id,
            'company': self.company.as_dict(),
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def as_dict_for_company(self):
        return {
            'external_uuid': self.external_uuid,
            'receiver': self.receiver.as_dict()
        }



class User(db.Model):
    __tablename__ = 'user'

    id_ = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    def __init__(self, email, name, password, admin=False):
        self.email = email
        self.name = name
        bcrypt = Bcrypt()
        self.password = bcrypt.generate_password_hash(
            password, current_app.config.get('BCRYPT_LOG_ROUNDS')
        ).decode()
        self.admin = admin


    def encode_auth_token(self, user_id):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1, seconds=5),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                current_app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e


    @staticmethod
    def decode_auth_token(auth_token):
        """
        Decodes the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, current_app.config.get('SECRET_KEY'))
            is_blacklisted_token = BlacklistToken.check_blacklist(auth_token)
            if is_blacklisted_token:
                return 'Token blacklisted. Please log in again.'
            else:
                return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'



class BlacklistToken(db.Model):
    """
    Token Model for storing JWT tokens
    """
    __tablename__ = 'blacklist_tokens'

    id_ = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.datetime.now()

    def __repr__(self):
        return '<id: token: {}'.format(self.token)

    @staticmethod
    def check_blacklist(auth_token):
        # check whether auth token has been blacklisted
        res = BlacklistToken.query.filter_by(token=str(auth_token)).first()
        if res:
            return True  
        else:
            return False



