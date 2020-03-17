import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import json

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  CORS(app)
  
  @app.after_request
  def handle_response(response):
      header = response.headers
      header['Access-Control-Allow-Origin'] = '*'
      return response

  
  @app.route("/categories", methods=['GET'])
  def get_categories():
      categories = list(map(Category.format, Category.query.all()))

      if len(categories) == 0:
        abort(404)

      return jsonify({
        "success": True,
        "categories": categories,
        "total_categoreies": len(Category.query.all())
      })

  @app.route("/questions")
  def get_question():
      page = int(request.args.get('page'))
      categories = list(map(Category.format, Category.query.all()))
      questions_query = Question.query.paginate(page, QUESTIONS_PER_PAGE)
      questions = list(map(Question.format, questions_query.items))
      if len(questions) > 0:
        return jsonify({
          "success": True,
          "questions": questions,
          "total_questions": questions_query.total,
          "categories": categories,
          "current_category": None,
        })
      abort(404)

  

  @app.route("/questions/<question_id>", methods=['DELETE'])
  def delete_question(question_id):
    question_data = Question.query.get(question_id)
    if question_data:
      Question.delete(question_data)
      result ={
        "success": True
      }
      return jsonify(result)
    abort(404)

  

  @app.route("/questions", methods=['POST'])
  def add_question():
    if request.data:
      new_question_data = json.loads(request.data.decode('utf-8'))
      if (('question' in new_question_data and 'answer' in new_question_data) and ('difficulty' in new_question_data and 'category' in new_question_data)):
        new_question = Question(
          question=new_question_data['question'],
          answer=new_question_data['answer'],
          difficulty=new_question_data['difficulty'],
          category=new_question_data['category']
        )
        Question.insert(new_question)
        return jsonify({
          "success": True,
        })
      abort(404)
    abort(422)

  
  @app.route("/searchQuestions", methods=['POST'])
  def search_questions():
    if request.data:
      page = 1
      if request.args.get('page'):
        page = int(request.args.get('page'))
      search_data = json.loads(request.data.decode('utf-8'))
      if 'searchTerm' in search_data:
        questions_query = Question.query.filter(Question.question.ilike(
          '%' + search_data['searchTerm'] + '%'
        )).paginate(
          page,
          QUESTIONS_PER_PAGE,
          False
        )
        questions = list(map(Question.format, questions_query.items))
        if len(questions) > 0:
          return jsonify({
            "success": True,
            "questions": questions,
            "total_questions": questions_query.total,
            "current_category": None
          })
      abort(404)
    abort(422)
  
  @app.route("/categories/<int:category_id>/questions")
  def question_by_category(category_id):
    category_data = Category.query.get(category_id)
    page = int(request.args.get('page'))
    categories = list(map(Category.format, Category.query.all()))
    questions_query = Question.query.filter_by(category=category_id).paginate(page, QUESTIONS_PER_PAGE)
    questions = list(map(Question.format, questions_query.items))
    if len(questions) > 0:
      return jsonify({
        "success": True,
        "questions": questions,
        "total_questions": questions_query.total,
        "categories": categories,
        "current_category": Category.format(category_data)
      })
    abort(404)

  @app.route("/quizzes", methods=['POST'])
  def get_question_for_quiz():
        if request.data:
            search_data = json.loads(request.data.decode('utf-8'))
            if (('quiz_category' in search_data
                 and 'id' in search_data['quiz_category'])
                    and 'previous_questions' in search_data):
                questions_query = Question.query.filter_by(
                    category=search_data['quiz_category']['id']
                ).filter(
                    Question.id.notin_(search_data["previous_questions"])
                ).all()
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
  
  @app.errorhandler(404)
  def not_found(error):
        error_data = {
            "success": False,
            "error": 404,
            "message": "Resource not found"
        }
        return jsonify(error_data), 404

  @app.errorhandler(422)
  def unprocessable(error):
        error_data = {
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }
        return jsonify(error_data), 422

  return app

    