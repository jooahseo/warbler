"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py

import os
from unittest import TestCase

from models import db, connect_db, Message, User, Follows


os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False

class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.session.rollback()
        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        u1 = User.signup('test1','test@email.com','password',None)
        u1.id = 100
        u2 = User.signup('test2','test2@email.com','password',None)
        u2.id = 200
        u3 = User.signup('test3','test3@email.com','password',None)
        u3.id = 300

        db.session.commit()

        self.u1 = u1
        self.u2 = u2
        self.u3 = u3

    def test_users_view(self):
        """users view page"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id
            
            res = c.get('/users')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code,200)
            self.assertIn('<p class="card-bio text-secondary">This user has no bio.</p>',html)

    def test_specific_user_view(self):
        """a user view page"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id
            
            res = c.get(f'/users/{self.u1.id}')
            html = res.get_data(as_text = True)

            self.assertEqual(res.status_code,200)
            self.assertIn(f'@{self.u1.username}</a>',html)

    def set_up_following(self):
        f1 = Follows(user_being_followed_id=self.u1.id, user_following_id=self.u2.id)
        f2 = Follows(user_being_followed_id=self.u2.id, user_following_id=self.u1.id)
        db.session.add_all([f1,f2])
        db.session.commit()

    def test_following_view(self):
        """user can view thier following"""
        self.set_up_following()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id
            
            res = c.get(f'users/{self.u1.id}/following')
            self.assertEqual(res.status_code,200)
            self.assertIn("@test2", str(res.data))
            self.assertNotIn("@test3",str(res.data))

    def test_follower_view(self):
        """user can view thier follower"""
        self.set_up_following()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id
            
            res = c.get(f'users/{self.u1.id}/followers')
            self.assertEqual(res.status_code,200)
            self.assertIn("@test2", str(res.data))
            self.assertNotIn("@test3",str(res.data))
        
    def test_unauthorized_view(self):
        """unauthorize to access the pages without login"""
        self.set_up_following()
        with self.client as c:
            res = c.get(f'users/{self.u1.id}/following', follow_redirects=True)
            self.assertEqual(res.status_code,200)
            self.assertIn("Access unauthorized",str(res.data))

            res2 = c.get(f'users/{self.u1.id}/followers', follow_redirects=True)
            self.assertEqual(res2.status_code,200)
            self.assertIn("Access unauthorized",str(res2.data))
