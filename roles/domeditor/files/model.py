from sqlalchemy import create_engine, Column, Text, Integer, VARCHAR, BLOB, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from configparser import ConfigParser
import os
import hashlib
import re
import string

db_name = "appname"

# ENGINE SETUP
this_directory = __file__.rsplit(os.path.sep, maxsplit=1)[0]
config_file_path = "{}{}config.ini".format(this_directory, os.path.sep)
cp = ConfigParser()
cp.read(config_file_path)
config_sec = cp["dbconfig"]
user = config_sec.get("username")
pw = config_sec.get("password")
db_name = config_sec.get("database")
db_url = "mysql+pymysql://{}:{}@localhost/{}".format(user, pw, db_name)
eng = create_engine(db_url)


Base = declarative_base()


class DomNumber(Base):
    __tablename__ = "domnumbers"
    id = Column(Integer, primary_key=True)
    number = Column(Integer)
    person = Column(Text)
    action = Column(Text)
    user = Column(ForeignKey("users.username"))


class User(Base):
    __tablename__ = "users"
    username = Column(VARCHAR(50), primary_key=True, nullable=False)
    is_active = Column(Boolean, default=False)
    is_authenticated = Column(Boolean, default=False)
    is_anonymous = Column(Boolean, default=False)
    dom_numbers = relationship("DomNumber")
    password = relationship("Password", uselist=False, lazy="joined")

    def get_id(self):
        return self.username


class Password(Base):
    __tablename__ = "passwords"
    username = Column(ForeignKey("users.username"), primary_key=True)
    password = Column(Text, nullable=False)
    salt = Column(BLOB)


Session = sessionmaker(bind=eng)
Base.metadata.create_all(eng)


def password_strong(pw):
    MIN_PW_LENGTH = 8
    if len(pw) < MIN_PW_LENGTH:
        return False
    if not re.search(r"\d+", pw):
        return False
    if not re.search(r"\w+", pw):
        return False
    if re.search(r"\s+", pw):
        return False
    if not set(string.punctuation).intersection(pw):
        return False
    return True


def create_user(uname, pw):
    if not password_strong(pw):
        msg = "Password requirements not met: Must be 8 characters or more with letters, numbers, punctuation, and no spaces"
        return msg

    sess = Session()
    hasher = hashlib.sha256()
    salt_data = os.urandom(16)
    hasher.update(salt_data + pw.encode())
    digest = hasher.hexdigest()

    user = User(username=uname)
    user.password = Password(password=digest, salt=salt_data)

    sess.add(user)
    sess.commit()
    sess.close()
    return "created user: {}".format(uname)


def get_user(uname):
    sess = Session()
    user = sess.query(User).filter_by(username=uname).one_or_none()
    sess.close()
    return user


def get_salt(uname):
    sess = Session()
    user = sess.query(User).filter_by(username=uname).one_or_none()
    salt = user.password.salt
    sess.close()
    return salt


def is_password_valid(uname, pw, prehashed=False):
    if prehashed:
        password_arg = pw
    else:
        salt_data = get_salt(uname)
        hasher = hashlib.sha256()
        hasher.update(salt_data + pw.encode())
        password_arg = hasher.hexdigest()

    user = get_user(uname)
    if user and user.password.password == password_arg:
        return True
    return False


def set_authenticate(uname, auth_status):
    sess = Session()
    user = get_user(uname)
    user.is_authenticated = auth_status
    sess.add(user)
    sess.commit()
    sess.close()


def initialize_dom_numbers(uname):
    sess = Session()
    user = sess.query(User).filter_by(username=uname).one_or_none()

    for num in range(100):
        dom_num = DomNumber(number=num, person="", action="")
        user.dom_numbers.append(dom_num)

    sess.commit()
    sess.close()

def update_dom_num(uname, num, person, action):
    sess = Session()
    dom_num = sess.query(DomNumber).filter_by(user=uname, number=num).one_or_none()
    dom_num.person = person
    dom_num.action = action
    sess.add(dom_num)
    sess.commit()
    return "SUCCESS"


def get_dom_num(uname, num):
    sess = Session()
    dom_num = sess.query(DomNumber).filter_by(user=uname, number=num).one_or_none()
    dom_dict = dict(number=num, person=dom_num.person, action=dom_num.action)
    sess.close()
    return dom_dict


def get_all_doms(uname):
    sess = Session()
    doms = sess.query(DomNumber).filter_by(user=uname).all()
    num_list = []
    from pdb import set_trace

    for dom in doms:
        dom_dict = dict(number=dom.number, person=dom.person, action=dom.action)
        num_list.append(dom_dict)
    sess.close()
    return num_list