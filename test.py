__author__ = 'mg'
from config import basedir
import random
from app import app, db_engine
from app.models import User
from sqlalchemy.orm import sessionmaker
import unittest

class TestCase(unittest.TestCase):

    def test_db_connection(self):
        try:
            random_number=random.randint(1111111, 999999999)
            u = User('id' + str(random_number), 'c49a532a71393b6b2a5584842cae37be', 'john@example.com')
            Session = sessionmaker(bind=db_engine)
            session_db = Session()
            session_db.add(u)
            user = session_db.query(User).filter(User.login == 'id' + str(random_number)).first()
            if not user:
                raise AssertionError
        except:
            assert False
        print('ok1')


    def test_unique_login(self):
        random_number=random.randint(1111111, 999999999)
        u = User('id' + str(random_number), 'c49a532a71393b6b2a5584842cae37be', 'john@example.com')
        Session = sessionmaker(bind=db_engine)
        session_db = Session()
        session_db.add(u)
        session_db.commit()
        # user = session_db.query(User).filter(User.login == 'john').first()
        try:
            session_db.add(u)
            session_db.commit()
            assert False
        except:
            assert True
        print('ok2')

if __name__ == '__main__':
    print('!!!')
    unittest.main()