import sys, os
from datetime import datetime
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS, cross_origin

# Your API definition
app = Flask(__name__)
#CORS(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

# MongoDB configuration
mongo_uri = 'mongodb+srv://'+os.environ.get('DB_USER')+':'+os.environ.get('DB_PASSWORD')+'@'
mongo_uri += os.environ.get('DB_URL')+'/'+os.environ.get('DB_NAME')+'?retryWrites=true&w=majority'
app.config['MONGO_URI'] = mongo_uri
mongo = PyMongo(app)

# Function to format date in mm-dd-yyyy
def format_date_from_db(date_str):
    try:
        return date_str.strftime('%m-%d-%Y')
    except ValueError as e:
        # Handle the ValueError (incorrect date format)
        return f'Error: {e}'

# Function to format date in mm-dd-yyyy
def format_date_to_db(date_str):
    try:
        # Convert date string to datetime object
        return datetime.strptime(date_str, '%m-%d-%Y')
    except ValueError as e:
        # Handle the ValueError (incorrect date format)
        return f'Error: {e}'

@app.route("/")
def home():
    return "Hello, World!"

# Get all students
@app.route('/api/get_students', methods=['GET'])
def get_students():
    try:
        # Get all records from MongoDB filtering with status = ACTIVE
        students = mongo.db.students.find({'status': 'ACTIVE'})

        student_list = [
            {
                '_id': str(student['_id']),
                'firstName': student['firstName'],
                'familyName': student['familyName'],
                'fullName': student['firstName'] + " " + student['familyName'],
                'dateOfBirth': format_date_from_db(student['dateOfBirth']),
                'email': student['email'],
                'status': student['status']
            }
            for student in students
        ]
        return jsonify({'students': student_list})
    except Exception as e:
        # Handle any other exception
        return jsonify({'error': f'An error occurred: {e}'})

# Create a new student
@app.route('/api/create_student', methods=['POST'])
def create_student():
    try:
        data_student = request.get_json()

        if data_student and \
           'firstName' in data_student and 'familyName' in data_student and \
           'dateOfBirth' in data_student and 'email' in data_student and \
           data_student['firstName'] and data_student['firstName'] != "" and \
           data_student['familyName'] and data_student['familyName'] != "" and \
           data_student['dateOfBirth'] and data_student['dateOfBirth'] != "" and \
           data_student['email'] and data_student['email'] != "":
 

            student = {
                'firstName': data_student['firstName'],
                'familyName': data_student['familyName'],
                'dateOfBirth': format_date_to_db(data_student['dateOfBirth']),
                'email': data_student['email'],
                'status': 'ACTIVE'
            }

            result = mongo.db.students.insert_one(student)
            return jsonify({
                'message': 'A new student record was created successfully', 
                'id': str(result.inserted_id)
            })
        else:
            return jsonify({
                'error': 'All fields (firstName, familyName, dateOfBirth, email) are required'
            })
    except Exception as e:
        # Handle any other exception
        return jsonify({'error': f'An error occurred: {e}'})

# Get all courses
@app.route('/api/get_courses', methods=['GET'])
def get_courses():
    try:
        # Get all records from MongoDB filtering with status = ACTIVE
        courses = mongo.db.courses.find({'status': 'ACTIVE'})

        course_list = [
            {
                '_id': str(course['_id']),
                'courseName': course['courseName'],
                'status': course['status']
            }
            for course in courses
        ]
        return jsonify({'courses': course_list})
    except Exception as e:
        # Handle any other exception
        return jsonify({'error': f'An error occurred: {e}'})

# Get all results
@app.route('/api/get_results', methods=['GET'])
def get_results():
    try:
        # Get all results from MongoDB filtering courses and students with status = ACTIVE
        results = mongo.db.results.aggregate([
            {
                '$lookup': {
                    'from': 'courses',
                    'let': {'courseId': '$courseId'},
                    'pipeline': [
                        {'$match': {'$expr': {'$and': [{'$eq': ['$_id', '$$courseId']}, {'status': 'ACTIVE'}]}}}
                    ],
                    'as': 'course'
                }
            },
            {
                '$unwind': '$course'
            },
            {
                '$lookup': {
                    'from': 'students',
                    'let': {'studentId': '$studentId'},
                    'pipeline': [
                        {'$match': {'$expr': {'$and': [{'$eq': ['$_id', '$$studentId']}, {'status': 'ACTIVE'}]}}}
                    ],
                    'as': 'student'
                }
            },
            {
                '$unwind': '$student'
            },
            {
                '$project': {
                    '_id': {'$toString': '$_id'},
                    'courseName': '$course.courseName',
                    'studentName': {
                        '$concat': ['$student.firstName', ' ', '$student.familyName']
                    },
                    'score': '$score'
                }
            }
        ])

        result_list = list(results)
        return jsonify({'results': result_list})
    except Exception as e:
        # Handle any other exception
        return jsonify({'error': f'An error occurred: {e}'})

if __name__ == '__main__':
    app.run(debug=True)
