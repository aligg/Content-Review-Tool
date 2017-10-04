"""Tests for Flask App"""
import unittest
import server
from model import (connect_to_db, db)

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
        
        connect_to_db(server.app)

    # def tearDown(self):
    #     """Code to run after every test"""
        
    #     db.session.close()

    def test_homepage(self):
        """Can we reach the homepage?"""

        result = self.client.get("/")
        self.assertIn("welcomes you", result.data)
        self.assertIn("Images Queue", result.data)

    def test_queue(self):
        """Test queue loading"""

        result = self.client.get("queue")
        self.assertIn("Subreddit", result.data)



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


