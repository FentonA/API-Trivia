import os
from flask import Flask, request, abort, jsonify, json
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

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
	cors = CORS(app, resources={"r*/api/*": {"origins": "*"}})

	'''
	@TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
	'''

	'''
	@TODO: Use the after_request decorator to set Access-Control-Allow
	'''
	@app.after_request
	def after_request(response):
		response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type, Authorization')
		response.headers.add('Access-Control-Allow-Methods',
                         'GET, POST, PATCH, DELETE, OPTIONS')
		response.headers.add('Access-Control-Allow-Origin', '*')
		return response

	'''
	@TODO:
	Create an endpoint to handle GET requests
	for all available categories.
	'''
	@app.route('/categories', methods=['GET'])
	def get_categories():
		all_categories = {}
		for category in Category.query.all():
			all_categories[category.id] = category.type
		return jsonify({
      		'success': True,
			'categories': all_categories
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
		# pagination
		selection = Question.query.order_by(Question.id).all()
		current_questions = paginate_questions(request, selection)

		categories = {}
		for category in Category.query.all():
			categories[category.id] = category.type

		return jsonify({
    		'success': True,
			'questions': current_questions,
			'categories': categories,
			'total_questions': len(current_questions)
			})
	'''
	@TODO:
	Create an endpoint to DELETE question using a question ID.
	TEST: When you click the trash icon next to a question, the question will be removed.
	This removal will persist in the database and when you refresh the page.
	'''

	@app.route('/questions/<int:questions_id>', methods=['DELETE'])
	def delete_questions(questions_id):
		del_questions = Question.query.get(questions_id)
		if not del_questions:
				abort(404)
		try:
				del_questions.delete()
				del_questions.commit()
		except:
			del_questions.rollback()
			abort(422)

		return jsonify({
      		'success': True,
			'deleted': questions_id
		}), 200

	'''
	@TODO:
	Create an endpoint to POST a new question,
	which will require the question and answer text,
	category, and difficulty score.
	TEST: When you submit a question on the "Add" tab,
	the form will clear and the question will appear at the end of the last page
	of the questions list in the "List" tab.
	'''

	@app.route('/questions', methods=['POST'])
	def update_questions_list():
		try:
			body = request.get_json()

			new_questions = Question(
				answer=body.get('answer', None),
				category=body.get('category', None),
				difficulty=body.get('difficulty', None),
				question=body.get('question', None)
			)
			new_questions.insert()

			question = Question.query.all()
			current_questions = paginate_questions(request, question)

			return jsonify({
				'success': True,
				'created': new_questions.id,
				'questions': current_questions,
				'total_questions': len(question)
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
	@app.route('/search', methods=['POST', 'GET'])
	def search_questions():
		try:
			# paginate
			page = request.args.get('page', 1, type=int)
			start = (page - 1) * 10
			end = start + 10

			searched_question = Question.query.filter(
			    Question.question.ilike('%{}%'.format(data['searchTerm']))).all()
			formatted_questions = [question.format() for question in searched_question]

			return jsonify({
				'success': True,
				'question': formattd_questions[start:end],
				'total_questions': len(formatted_questions)
			})

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
		if not categories_id:
			abort(404)
		try:
			category_item = Category.query.get(categories_id)

			categories = list(map(Category.format, Category.query.all()))

			questions_item = Question.query.filter_by(category=categories_id).all()

			questions = list(map(Question.format, questions_item))

			return jsonify({
				'success': True,
				'questions': questions,
				'total_questions': len(questions_item),
				'current_category': Category.format(category_item),
				'categories': categories
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
	def get_question_for_quiz():
		if request.data:
			search_data = request.get_data('search_term')
			if ((b'quiz_category' in search_data
                and 'id' in search_data['quiz_category'])
                    and b'previous_questions' in search_data):
				questions_query = Question.query \
                    .filter_by(category=search_data['quiz_category']['id']) \
                    .filter(Question
                            .id.notin_(search_data["previous_questions"]))\
                    .all()
				length_of_available_question = len(questions_query)
				if length_of_available_question > 0:
					result = {
                        "success": True,
                        "question": Question.format(
                            questions_query[random.randrange(
                                0,
                                length_of_available_question
                            )]
                        )
                    }
				else:
					result = {
                        "success": True,
                        "question": None
                    }
				return jsonify(result)
			abort(404)
		abort(422)


	@app.errorhandler(422)
	def unproccessable(error):
		return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable"
        }), 422


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
