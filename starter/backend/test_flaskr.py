import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://postgres:7Pillars@{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000', json={'rating': 1})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
    
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'], True)
        self.assertTrue(len(data['categories']))

    def test_get_categories_fail(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_cod, 422)
        self.assertFalse(data['success'])
        self.assertEqual(data['data'], 'Unprocessable')

    def test_delete_questions(self):
        res = self.client().delete('/questions/1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True )
        self.assertEqual(data['deleted'], 1)
    
    def test_delete_questions_fail(self):
        res = self.client().delete('/questions/1')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['suuccess'])
        self.assertEqual(data['message'], 'Resources not found')

    def test_update_questions(self):
        new_question = {
            'question': 'What is the Capitol of Japan',
            'answer': "Tokyo",
            'category': '2',
            'difficulty': '1'
        }

        res = self.client().post('/questions', json = new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['created questions'])
        self.assertTrue(len(data['questions']))

    def test_update_question_fail(self):

        new_questions = {
            'questions': 'Which Thai king was born in Cambridge Massachusets?',
            'answer': 'King Rama IX',
            'category': '3',
            'difficulty': '5'
        }
        res = self.client().post('/questions',json= new_questions)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Unprocessable')

    def test_search_questions(self):
        res = self.client().get('/search')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])

    def test_search_questions_fail(self):
        res = self.client().get('/search')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], 'Not Found')
        self.assertFalse(data['success'])
    
    def test_get_questions_by_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))

    def test_get_questions_by_category_fail(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(len(data['questopms']))
        self.assertFalse(len(data['categories']))

    def test_quiz(self):
        quiz_data ={
            'previosu_questions': [],
            'quiz_category':{
                'type': 'Geography',
                'id': 1
            }
        }

        res = self.client().post('/quiz', json-quiz_data)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
    
    def test_quiz_fail(self):
        quiz_data = {
            'previous_questions':[],
            'quiz_category':{
                'type': 'History',
                'id': 2
            }
        }

        res = self.client().post('/quiz', json = quiz_data)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()