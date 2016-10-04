from sqlalchemy import create_engine, Column, Text, Integer, VARCHAR, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from configparser import ConfigParser
import os
import hashlib

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
    password = Column(Text, nullable=False)
    is_active = Column(Boolean, default=False)
    is_authenticated = Column(Boolean, default=False)
    is_anonymous = Column(Boolean, default=False)
    dom_numbers = relationship("DomNumber")

    def get_id(self):
        return self.username


Session = sessionmaker(bind=eng)
Base.metadata.create_all(eng)


def create_user(uname, pw):
    sess = Session()
    hasher = hashlib.sha256()
    hasher.update(pw.encode())
    digest = hasher.hexdigest()
    user = User(username=uname, password=digest)
    sess.add(user)
    sess.commit()
    sess.close()
    return "created user: {}".format(uname)


def get_user(uname):
    sess = Session()
    user = sess.query(User).filter_by(username=uname).one_or_none()
    sess.close()
    return user



def is_password_valid(uname, pw, prehashed=False):
    if prehashed:
        password_arg = pw
    else:
        hasher = hashlib.sha256()
        hasher.update(pw.encode())
        password_arg = hasher.hexdigest()

    user = get_user(uname)
    if user and user.password == password_arg:
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
