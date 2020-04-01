import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
		page = request.args.get('page', 1, type=int)
		start = (page - 1) * QUESTIONS_PER_PAGE
		end = start + QUESTIONS_PER_PAGE

		questions = [question.format() for question in selection]
		current_questions = questions[start:end]


def create_app(test_config=None):
		# create and configure the app
		app = Flask(__name__, instance_relative_config=True)
		setup_db(app)
		CORS(app)

	'''
	@TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
	'''
		#cors = CORS(app, resources={"r*/api/*": {origins: "*"}})

	'''
	@TODO: Use the after_request decorator to set Access-Control-Allow
	'''
		@app.after_request
		def after_request(response):
				response.headers.add('Access-Control-Allow-Headers',
														 'Contnet-Type, Authorization')
				response.headers.add('Access-Control-Allow-Methods',
														 'GET, POST, PATCH, DELETE, OPTIONS')
				return response
	'''
	@TODO:
	Create an endpoint to handle GET requests
	for all available categories.
	'''
		@app.route('/categories', methods=['GET'])
		 #@cross_origin()
		def get_categories():
				selection = Category.query.order_by(Category.id).all()
				current_categories = paginate_questions(request, selection)

				return({
						'success': True,
						'Questions': current_categories,
						'Category': len(Category.query.all())
				})
	'''
	@TODO:
	Create an endpoint to handle GET requests for questions,
	including pagination (every 10 questions).
	This endpoint should return a list of questions,
	number of total questions, current category, categories.


	TEST: At this point, when you start the application
	you should see questions and categories generated,
	ten questions per page and pagination at the bottom of the screen for three pages.
	Clicking on the page numbers should update the questions.
	'''
		@app.route('/questions')
		def retreive_questions():
				selection = Question.query.order_by(Question.id).all()
				current_questions = paginate_questions(request, selection)

				if len(current_questions) == 0:
						abort(404)

				return({
						'success': True,
						'questions': current_questions,
						'total_questions': len(Question.query.all())
				})
	'''
	@TODO:
	Create an endpoint to DELETE question using a question ID.

	TEST: When you click the trash icon next to a question, the question will be removed.
	This removal will persist in the database and when you refresh the page.
	'''

		@app.route('questions/<int:questions_id>', methdods=['DELETE'])
		def delete_questions(questions_id):
				try:
						question = Question.query.order_by(Questions.id).one_or_none()

						if questions == None:
								abort(404)

						questions.delete()
						selection = Question.query.order_by(Question.id).all()
						current_questions = paginate_questions(request, selection)

						return jasonify({
								'success': True,
								'deleted': book_id,
								'questions': current_questions,
								'total_questions': len(Question.query.all())
						})
				except:
						abort(422)


	'''
	@TODO:
	Create an endpoint to POST a new question,
	which will require the question and answer text,
	category, and difficulty score.

	TEST: When you submit a question on the "Add" tab,
	the form will clear and the question will appear at the end of the last page
	of the questions list in the "List" tab.
	'''

	@app.route('/questions')
	def update_questions():
		body = request.get_json()

		new_questions = body.get('Questions', None)
		new_answers = body.get('answers', None)
		new_category = body.get('categoy', None)
		new_difficulty = body.get('difficulty', None)

		try:
			questions = Question(questions = new_questions, answers = new_answers, category = new_category, difficulty = new_difficulty)

			questions. insert()

			selection = Question.query.order_by(Question.id),all()
			current_questions = paginate_questions(request, selection)

			return jsonify({

				'success': True,
				'created': Question.id,
				'questions': current_questions,
				'total questions': len(Question.query.all())
			})
		except:
			abort(422)
	'''
	@TODO:
	Create a POST endpoint to get questions based on a search term.
	It should return any questions for whom the search term
	is a substring of the question.

	TEST: Search by any phrase. The questions list will update to include
	only question that include that string within their question.
	Try using the word "title" to start.
	'''
	@app.route('/questions/<int:questions_id>')
	def search_questions():
		try:
			question = Question.query.filter(Question.id == question_id).one_or_one()

			return jsonify({
				'success': True,
				'questions': Question.id,
				'total questions': len(Questions.query.all())
			})

			selcttion = Question.query.order_by(question.id).all()
			current_questions = paginate_questions(request, selcttion)

		except:
			abort(404)


	'''
	@TODO:
	Create a GET endpoint to get questions based on category.

	TEST: In the "List" tab / main screen, clicking on one of the
	categories in the left column will cause only questions of that
	category to be shown.
	'''
	@app.route()

	'''
	@TODO:
	Create a POST endpoint to get questions to play the quiz.
	This endpoint should take category and previous question parameters
	and return a random questions within the given category,
	if provided, and that is not one of the previous questions.

	TEST: In the "Play" tab, after a user selects "All" or a category,
	one question at a time is displayed, the user is allowed to answer
	and shown whether they were correct or not.
	'''

	'''
	@TODO:
	Create error handlers for all expected errors
	including 404 and 422.
	'''
	@app.errohandler(404)
	def not_found(error):
		return jsonify({
			"success": False,
			"error": 404,
			"message": "Resources not found"
		}), 404

	@app.errorhandler(422)
	def unprocessable(error):
		return jasonify({
			"success": False,
			"error": 422,
			"message": "Unprocessable"
		}), 422

	@app.errohandler(400)
	def bad_request(error):
		return jsonify({
			"success": False,
			"error": 400,
			"message": "Bad request"
		}), 400

	return app
