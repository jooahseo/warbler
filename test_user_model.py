"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py

from logging import error
import os
from unittest import TestCase

from models import db, User, Message, Follows, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Now we can import app

from app import app
from datetime import datetime
# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()
class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()
        Likes.query.delete()

        u1 = User.signup('test1', 'test1@email.com','password',None)
        u1.id = 1000

        u2 = User.signup('test2', 'test2@email.com','password2',None)
        u2.id = 2000
        db.session.commit()
        self.u1 = u1
        self.u2 = u2
        self.client = app.test_client()

    def test_user_model(self):
        """Does basic User model work?"""
        # User should have no messages & no followers
        self.assertEqual(len(self.u1.messages), 0)
        self.assertEqual(len(self.u1.followers), 0)

    def test_repr_method(self):
        """Does the repr method work as expected?"""
        u = self.u1
        self.assertTrue(repr(u) == f"<User #{u.id}: {u.username}, {u.email}>")

    def test_follows_model(self):
        """Does user follows/following model work?"""
        u1 = self.u1
        u2 = self.u2

        follow = Follows(user_being_followed_id = u1.id, user_following_id = u2.id)
        db.session.add(follow)
        db.session.commit()

        self.assertTrue(u2 in u1.followers)
        self.assertFalse(u1 in u2.followers)
        self.assertTrue(u1 in u2.following)
    
    def test_user_signup(self):
        """Does User.create fail to create a new user if any of the 
        validations (e.g. uniqueness, non-nullable fields) fail?"""
        missing_data = {
            "email":"user3@test.com",
            "username":"iam3"
            }   
        with self.assertRaises(TypeError):
            User.signup(**missing_data)
        
        complete_data = {
            "username":"testing",
            "email":"user3@test.com",
            "password":"123456",
            "image_url":"test.com/image_1"
        }

        u = User.signup(**complete_data)
        self.assertIsInstance(u, User)
    
    def test_user_authenticate(self):
        """Does User.authenticate successfully return a user 
        when given a valid username and password?        
        """
        u = self.u1

        res = User.authenticate(u.username,'password')
        self.assertTrue(u == res)

        res2 = User.authenticate(u.username,'wrongpw')
        self.assertFalse(res2)

        res3 = User.authenticate('hihihi','password')
        self.assertFalse(res3)

    def test_likes_model(self):
        u1 = self.u1
        u2 = self.u2

        m = Message(
            text = 'Hello',
            user_id = u1.id
        )        
        db.session.add(m)
        db.session.commit()

        likes = Likes(user_id = u2.id, message_id = m.id)
        db.session.add(likes)
        db.session.commit()

        self.assertTrue(m in u2.likes)
        self.assertFalse(m in u1.likes)
