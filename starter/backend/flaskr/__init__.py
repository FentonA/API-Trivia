import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


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
                         'Contnet-Type, Authorization')
		response.headers.add('Access-Control-Allow-Methods',
                         'GET, POST, PATCH, DELETE, OPTIONS')
		response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
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
			'categories' : all_categories
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
		#pagination
		page = request.args.get('page', 1, type=int)
		start = (page -1) * 10
		end = start + 10

		questions = Question.query.all()
		current_questions = [question.format() for question in questions]
		categories = {}
		for category in Category.query.all():
			categories[category.id] = category.type

		return jsonify({
    		'success': True,
			'questions': current_questions[start:end],
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
			#paginate
			page = request.args.get('page', 1, type=int)
			start = (page  -1 ) * 10
			end = start + 10

			body = request.json()
			
			new_questions = Question(
				answer = body.get('answer', None),
				category = body.get('category', None),
				difficulty = body.get('difficulty', None),
				question = body.get('question', None)
			)
			new_questions.insert()

			question = Question.query.all()
			created_questions = [question.format() for new_questions in question]


			return jsonify({
				'success': True,
				'created': new_questions.id,
				'questions': created_questions[start:end],
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
	@app.route('/questions/search', methods=['POST', 'GET'])
	def search_questions():
		try:
			#paginate
			page = request.args.get('page', 1, type=int)
			start = (page  -1 ) * 10
			end = start + 10

			searched_question = Question.query.filter(Question.question.ilike('%{}%'.format(data['searchTerm']))).all()
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