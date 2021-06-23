"""User model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py

import os
from unittest import TestCase

from models import db, User, Message, Follows, Likes

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Now we can import app

from app import app

db.create_all()

USER_DATA = {
    "email":"test@test.com",
    "username":"testuser",
    "password":"HASHED_PASSWORD"
}

USER_DATA2 = {
    "email":"test@gmail.com",
    "username":"hellotest",
    "password":"IT_WILL_WORK"
}

USER_DATA3 = {
    "email":"user3@test.com",
    "username":"iam3",
    "password":"EXTRA_TEST"
}
class MessageModelTestCase(TestCase):
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

    def test_message_model(self):
        """Does basic Message model work?"""

        u = self.u1

        m = Message(
            text = 'Hello',
            user_id = u.id
        )
        db.session.add(m)
        db.session.commit()

        self.assertEqual(m.user.id, u.id)
        self.assertTrue(m in u.messages)

    def test_message_likes_model(self):
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
