"""Tests for Flask App"""
import unittest
import server
from model import (connect_to_db, db, example_data)

class LoggedInServerTests(unittest.TestCase):
    """Tests for logged in CRT """

    def setUp(self):
        """Code to run before every test"""

        server.app.config['TESTING'] = True
        server.app.config['SECRET_KEY'] = 'miau'
        self.client = server.app.test_client()

        with self.client as c:
            with c.session_transaction() as sess:
                sess['reviewer id'] = 1
                sess['handle'] = 'alig'
        
        connect_to_db(server.app, "postgresql:///testdb")

        db.create_all()
        example_data()

        def _mock_picker_handler():
            """creates mock picker handler to avoid doing real api calls during testing"""
        
            comments="[<Item item_id=556 link_id=72xep5>]"

            return comments

        server.picker_handler = _mock_picker_handler

    def tearDown(self):
        """Code to run after every test"""
        
        db.session.close()

    def test_homepage(self):
        """Can we reach the homepage?"""

        result = self.client.get("/")
        self.assertIn("welcomes you", result.data)
        self.assertIn("Images Queue", result.data)

    def test_queue(self):
        """Test queue loading"""

        result = self.client.get("/queue")
        self.assertIn("Subreddit", result.data)

    
    def test_imagequeue(self):
        """Does image queue route directs to image queue?"""

        result = self.client.get("/image-queue", 
                                follow_redirects=True)
        self.assertIn("Image", result.data)
        self.assertNotIn("Comment for Review", result.data)

    
    def test_picker(self):
        """Does the picker route work & display the form?"""

        result=self.client.get("/picker")
        self.assertIn("Subreddit", result.data)

##why does this still query the api live?!?!
    # def test_pickerhandler(self):
    #     """Does the picker handler route work & redirect to the queue with proper contents displayed?"""

    #     picker_info = {"subreddit" : "news", "sort" : "top", "time" : "day"}

    #     result=self.client.post("/picker-handler", 
    #                             data=picker_info,
    #                             follow_redirects=True)

    #     self.assertIn("news", result.data)

    def test_reg(self):
        """Does the registration page load properly?"""

        result=self.client.get("/add-reviewer")
        self.assertIn("Add a new reviewer", result.data)
        self.assertIn("Password", result.data)


    def test_reg_handler_dupe(self):
        """Does the registration handler work properly for reviewers already in db?"""

        reg_data = {"email" : "miau@gmail.com", "handle" :"miau", "password" : "miau", "is_manager" : False}
        result = self.client.post("/reg-handler", data=reg_data, follow_redirects=True)
        self.assertIn("This reviewer is already registered", result.data)
        self.assertNotIn("New reviewer registered", result.data)

    def test_reg_handler(self):
        """Does the registration handler work properly for new reviewers?"""

        reg_data = {"reviewer id": 1000, "email" : "woof@gmail.com", "handle" :"woof", "password" : "woof", "is_manager" : False}
        result = self.client.post("/reg-handler", data=reg_data, follow_redirects=True)
        self.assertNotIn("This reviewer is already registered", result.data)
        self.assertIn("New reviewer registered", result.data)


    def test_logout(self):
        """Does the logout route logout?"""

        result=self.client.get("/logout", follow_redirects=True) 
        self.assertIn("You are now logged out", result.data)


class LoggedOutServerTests(unittest.TestCase):
    """Tests for logged out CRT"""

    def setUp(self):
        """Code to run before every test"""

        server.app.config['TESTING'] = True
        server.app.config['SECRET_KEY'] = 'miau'
        self.client = server.app.test_client()

        connect_to_db(server.app)

    
    def test_homepage(self):
        """Can we reach the homepage and does it load with correct info for logged ou user"""

        result = self.client.get("/")
        self.assertIn("welcomes you", result.data)
        self.assertNotIn("Comments Queue", result.data)


if __name__ == "__main__":
    unittest.main()


