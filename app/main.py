import sys, os
from datetime import datetime
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS, cross_origin
from bson import ObjectId


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


# Delete a student by ID
@app.route('/api/delete_student/<string:student_id>', methods=['DELETE'])
def delete_student(student_id):
    try:
        # Convert string ID to ObjectId
        student_object_id = ObjectId(student_id)

        # Delete the student by ID - Update Status to INACTIVE
        result = mongo.db.students.update_one(
            {'_id': student_object_id},
            {'$set': {'status': 'INACTIVE'}}
        )

        if result.modified_count  > 0:
            return jsonify({'message': 'Student deleted successfully'})
        else:
            return jsonify({'error': 'Student not found'})
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


# Create a new course
@app.route('/api/create_course', methods=['POST'])
def create_course():
    try:
        data_course = request.get_json()

        if data_course and \
            'courseName' in data_course and \
            data_course['courseName'] and data_course['courseName'] != "":
 
            course = {
                'courseName': data_course['courseName'],
                'status': 'ACTIVE'
            }

            result = mongo.db.courses.insert_one(course)
            return jsonify({
                'message': 'A new course record was created successfully', 
                'id': str(result.inserted_id)
            })
        else:
            return jsonify({
                'error': 'All fields (courseName) are required'
            })
    except Exception as e:
        # Handle any other exception
        return jsonify({'error': f'An error occurred: {e}'})


# Delete a course by ID
@app.route('/api/delete_course/<string:course_id>', methods=['DELETE'])
def delete_course(course_id):
    try:
        # Convert string ID to ObjectId
        course_object_id = ObjectId(course_id)

        # Delete the course by ID - Update Status to INACTIVE
        result = mongo.db.courses.update_one(
            {'_id': course_object_id},
            {'$set': {'status': 'INACTIVE'}}
        )

        if result.modified_count  > 0:
            return jsonify({'message': 'Course deleted successfully'})
        else:
            return jsonify({'error': 'Course not found'})
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
                    'localField': 'courseId',
                    'foreignField': '_id',
                    'as': 'course'
                }
            },
            {
                '$unwind': '$course'
            },
            {
                '$lookup': {
                    'from': 'students',
                    'localField': 'studentId',
                    'foreignField': '_id',
                    'as': 'student'
                }
            },
            {
                '$unwind': '$student'
            },
            {
                '$match': {
                    'course.status': 'ACTIVE',
                    'student.status': 'ACTIVE'
                }
            },
            {
                '$project': {
                    '_id': {'$toString': '$_id'},
                    'courseName': '$course.courseName',
                    'firstName': '$student.firstName',
                    'familyName': '$student.familyName',
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


# Create a new result
@app.route('/api/create_result', methods=['POST'])
def create_result():
    try:
        data_result = request.get_json()

        if data_result and \
            'courseId' in data_result and 'studentId' in data_result and \
            'score' in data_result and \
            data_result['courseId'] and data_result['courseId'] != "" and \
            data_result['studentId'] and data_result['studentId'] != "" and \
            data_result['score'] and data_result['score'] != "" and \
            data_result['score'] in ("A", "B", "C", "D", "E", "F"):

            # Convert string IDs to ObjectId
            course_id = ObjectId(data_result['courseId'])
            student_id = ObjectId(data_result['studentId'])

            new_result = {
                'courseId': course_id,
                'studentId': student_id,
                'score': data_result['score'],
                'status': 'ACTIVE'
            }

            result = mongo.db.results.insert_one(new_result)
            return jsonify({
                'message': 'A new result record was created successfully', 
                'id': str(result.inserted_id)
            })
        else:
            return jsonify({
                'error': 'All fields (courseName) are required'
            })
    except Exception as e:
        # Handle any other exception
        return jsonify({'error': f'An error occurred: {e}'})


if __name__ == '__main__':
    app.run(debug=True)
