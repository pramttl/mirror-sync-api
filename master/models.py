from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

############################  MODELS  #############################
from werkzeug import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(100), unique=True)
    pwdhash = db.Column(db.String(54))
    role = db.Column(db.String(16))

    def __init__(self, username, password, role):
        self.username = username
        self.set_password(password)
        self.role = role

    def set_password(self, password):
        self.pwdhash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.pwdhash, password)

    def generate_auth_token(self, expiration=600):
        s = Serializer('REPLACE_BY_SECRET_KEY', expires_in=expiration)   #XXX
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer('REPLACE_BY_SECRET_KEY')  #XXX
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        user = User.query.get(data['id'])
        return user


class SlaveNode(db.Model):
    """
    Model that contains data related to FTP Host or slave that syncs
    from the master.
    """
    __tablename__ = 'slaves'
    id = db.Column('slave_id', db.Integer, primary_key=True)
    hostname = db.Column(db.String(60))
    port = db.Column(db.String)

    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port

    @property
    def to_dict(self):
       """Converts SlaveNode object to a dictionary"""
       return {
           'id': self.id,
           'hostname': self.hostname,
           'port': self.port,
       }

