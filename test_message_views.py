"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

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

        self.u1 = u1
        self.u2 = u2
        db.session.commit()

    def test_add_message(self):
        """Can use add a message? 
        After add a message, is message's user_id is user that created?
        """

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})
            res = c.get('/messages/new')
            html = res.get_data(as_text=True)

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(res.status_code, 200)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")
            self.assertEqual(msg.user_id,self.u1.id)
            self.assertIn('Add my message!',html)

    def test_show_message(self):
        """show a message"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id

            res = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            self.assertEqual(res.status_code, 200)

            msg = Message.query.one()
            res2 = c.get(f"/messages/{msg.id}")
            html = res.get_data(as_text =True)

            self.assertEqual(res2.status_code, 200)
            self.assertIn('Hello',html)
            self.assertIn('Delete',html)

    def test_delete_mssages(self):
        """delete a message"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id

            c.post("/messages/new", data={"text": "Hello"})
            msg = Message.query.one()

            res = c.post(f"messages/{msg.id}/delete", follow_redirects=True)
            html = res.get_data(as_text = True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<button class="btn btn-outline-danger ml-2">Delete Profile</button>',html)

    def test_add_msg_without_login(self):
        """adding a message without logging in"""
        with self.client as c:

            res = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn("Access unauthorized",html)
        
    def test_add_msg_invalid_user(self):
        """adding a message as an invalid user"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY]=12345

            res = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn("Access unauthorized",str(res.data))

    def test_delete_msg_without_login(self):
        """deleting a message without logging in"""
        with self.client as c:
            
            res = c.post(f"messages/1/delete", follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn("Access unauthorized",str(res.data))


    def test_delete_msg_unauthorized_user(self):
        """deleting a message by unauthorized user"""
        m = Message(
            id = 100,
            text = "CANNOT DELET ME",
            user_id = self.u1.id
        )
        db.session.add(m)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u2.id
            
            res = c.post('/messages/100/delete', follow_redirects=True)
            self.assertEqual(res.status_code,200)
            self.assertIn("Unauthorized Action",str(res.data))
