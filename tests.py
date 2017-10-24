"""Tests for CRT"""

import unittest
import server
from model import (connect_to_db, db, example_data)
import datetime




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

        def _mock_picker_handler_api_helper():
            """creates mock picker handler helper to avoid doing real api calls during testing"""
    
            comments="[<Item item_id=3 link_id=345>]"
            return comments

        server.picker_handler_api_helper = _mock_picker_handler_api_helper


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


    def test_picker_handler(self):
        """Does the picker handler route work & redirect to the queue with proper contents displayed?"""

        picker_info = {"subreddit" : "news", "sort" : "top", "time" : "day"}

        result=self.client.post("/picker-handler", 
                                data=picker_info,
                                follow_redirects=True)

        self.assertIn("news", result.data)
        self.assertIn("POST ON REDDIT", result.data)

##### submit test returning integrity errors ####
    # def test_submit(self):
    #     """Does the queue submit work?"""

    #     submit_data = {"item_id": 5678, "reviewer_id" : 1, "time_created": datetime.datetime.utcnow(), "label_applied": "brand_safe", "notes": "TEST", "batchsize" : 1}

    #     result = self.client.post("/submit", data=submit_data, follow_redirects=True)

    #     self.assertIn("Review Item", result.data)


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

    def test_display_training(self):
        """Does the training page render?"""

        result=self.client.get("/training")
        self.assertIn("Hot Keys", result.data)

    def test_display_dash(self):
        """Does the operations dashboard page render?"""

        result=self.client.get("/dashboard")
        self.assertIn("Total Reviews", result.data)
        self.assertIn("crt-chart", result.data)

    def test_total_agreement_data(self):
        """Does the json passed to the agreement table on dashboard make it? """

        result=self.client.get("/dashboard-line-agreement.json")
        self.assertIn("datasets", result.data)
        self.assertIn("Daily Agreement Rate", result.data)


    def test_total_dailies_data(self):
        """Does the json passed to the daily reviews table on dashboard make it? """

        result=self.client.get("/dashboard-line-dailies.json")
        self.assertIn("datasets", result.data)
        self.assertIn("labels", result.data)


class LoggedOutServerTests(unittest.TestCase):
    """Tests for logged out CRT"""

    def setUp(self):
        """Code to run before every test"""

        server.app.config['TESTING'] = True
        server.app.config['SECRET_KEY'] = 'miau'
        self.client = server.app.test_client()

        connect_to_db(server.app, "postgresql:///testdb")
        db.create_all()
        example_data()

    
    def test_homepage(self):
        """Can we reach the homepage and does it load with correct info for logged ou user"""

        result = self.client.get("/")
        self.assertIn("welcomes you", result.data)
        self.assertNotIn("Comments Queue", result.data)


    def test_login_handler(self):
        """Does the login handler work properly for an existing user who enters proper credentials?"""

        login_data = {"handle": "alig", "password": "password"}
        result = self.client.post("/login-handler", data=login_data, follow_redirects=True)
        self.assertIn("You are logged in", result.data)
        self.assertIn("alig", result.data)
        self.assertNotIn("Incorrect credentials", result.data)


    def test_login_handler_bad_credentials(self):
        """Does the login handler work properly for an existing user who enters poor credentials?"""

        login_data = {"handle": "alig", "password": "wordpass"}
        result = self.client.post("/login-handler", data=login_data, follow_redirects=True)
        self.assertNotIn("You are logged in", result.data)
        self.assertNotIn("alig", result.data)
        self.assertIn("Incorrect credentials", result.data)


    def test_login_handler_no_reviewer(self):
        """Does the login handler work properly for a user who does not exist yet?"""

        login_data = {"handle": "purplerain", "password": "wordpass"}
        result = self.client.post("/login-handler", data=login_data, follow_redirects=True)
        self.assertNotIn("You are logged in", result.data)
        self.assertIn("Reviewer by that handle does not exist.", result.data)


if __name__ == "__main__":
    unittest.main()


