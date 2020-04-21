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

	return current_questions


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
	def get_categories():
		categories = Category.query.all()
		categories_dict = {}
		for category in categories:
			categories_dict[category.id] = category.type
		if (len(categories_dict) == 0):
			abort(404)

		return({
      		'success': True,
			'categories' : categories_dict
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
	@app.route('/questions/')
	def retreive_questions():
		selection = Question.query.order_by(Question.id).all()
		current_questions = paginate_questions(request, selection)

		if len(current_questions) == 0:
			abort(404)

		return({
    		'success': True,
			'questions': current_questions,
			'categories': None,
			'totalQuestions': len(Question.query.all()),
			'currentCateogry': None
				})
	'''
	@TODO:
	Create an endpoint to DELETE question using a question ID.

	TEST: When you click the trash icon next to a question, the question will be removed.
	This removal will persist in the database and when you refresh the page.
	'''

	@app.route('/questions/<int:questions_id>', methods=['DELETE'])
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

	@app.route('/questions/add', methods=['POST'])
	def update_questions():
		data = {
			'questions': request.get_json()['questions'],
			'answers': request.get_json()['answers'],
			'category':  request.get_json()['category'],
			'difficulty': request.get_json()['difficulty']
		}

		try:
			question = Question(**data)

			question.insert()

			selection = Question.query.order_by(Question.id), all()
			current_questions = paginate_questions(request, selection)

			return jsonify({
				'success': True,
				'created': questions.id,
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
	@app.route('/questions/search', methods=['POST', 'GET'])
	def search_questions():
		try:
			searched_question = Question.query.filter(
			    Question.question.ilike('%{}%'.format(data['searchTerm']))).all()
			formatted_questions = [question.format() for question in searched_question]

			return jsonify({
				'success': True,
				'total questions': len(formatted_questions)
			})

			selection = Question.query.order_by(question.id).all()
			current_questions = paginate_questions(request, selection)

		except:
			abort(404)

	'''
	@TODO:
	Create a GET endpoint to get questions based on category.

	TEST: In the "List" tab / main screen, clicking on one of the
	categories in the left column will cause only questions of that
	category to be shown.
	'''
	@app.route('/categories/<int:categories_id>/questions', methods=['GET'])
	def get_category_questions(categories_id):
		try:
			categories = Category.query.all()

			formatted_categories = [c.format() for c in categories]

			questions = Question.query.filter_by(category=str(categories_id)).all()

			formatted_questions = [q.format() for q in questions]
			print("LOG formatted questions", formatted_questions)
			current_questions = paginate_questions(request, questions)

			curr_categs = list(set([q['category'] for q in current_questions]))
			current_category = curr_categs

			return jsonify({
				'success': True,
				'questions': current_questions,
				'total_questions': len(questions),
				'current_category': current_category,
				'categories': formatted_categories
				})
		except:
			abort(422)

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

	@app.route('/quiz', methods=['POST'])
	def play_quiz():
		'''
		Returns a single question from the database
		Filters the questions already sent to the client
		'''
		try:
			data = request.get_json()
			# check given category
			category_id = int(data["quiz_category"]["id"])
			category = Category.query.get(category_id)
			previous_questions = data["previous_questions"]
			if not category == None:  
				if "previous_questions" in data and len(previous_questions) > 0:
					questions = Question.query.filter(
					Question.id.notin_(previous_questions),
					Question.category == category.id
					).all()  
				else:
					questions = Question.query.filter(Question.category == category.id).all()
			else:
				if "previous_questions" in data and len(previous_questions) > 0:
					questions = Question.query.filter(Question.id.notin_(previous_questions)).all()  
				else:
					questions = Question.query.all()
					max = len(questions) - 1
			if max > 0:
				question = questions[random.randint(0, max)].format()
			else:
				question = False
			return jsonify({
				"success": True,
				"question": question
			})
		except:
			abort(500, "An error occured while trying to load the next question")


	'''
	@TODO:
	Create error handlers for all expected errors
	including 404 and 422.
	'''
	@app.errorhandler(404)
	def not_found(error):
		return jsonify({
				"success": False,
				"error": 404,
				"message": "Resources not found"
			}), 404

	@app.errorhandler(422)
	def unprocessable(error):
		return jsonify({
				"success": False,
				"error": 422,
				"message": "Unprocessable"
			}), 422

	@app.errorhandler(400)
	def bad_request(error):
		return jsonify({
				"success": False,
				"error": 400,
				"message": "Bad request"
			}), 400

	
	return app
