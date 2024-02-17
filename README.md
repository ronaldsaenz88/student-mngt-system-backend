# Student Result Management System - Backend

## Description
This is the backend for the Student Result Management System. It provides API endpoints to manage students, courses, and results.

## Technologies Used
- Flask
- MongoDB
- Flask-PyMongo

## Getting Started
1. Clone the repository.
2. Navigate to the project directory.
3. Install dependencies: `pip install -r requirements.txt`.
4. Set up the environment variables (if required).
5. Run the application: `python app.py`.

## Configuration
Ensure to set the appropriate environment variables in the `.env` file or elsewhere.

## Endpoints
- `GET /api/get_students`: Get all students.
- `POST /api/create_student`: Create a new student.
- `DELETE /api/delete_student/:id`: Delete a student.
- `GET /api/get_courses`: Get all courses.
- `POST /api/create_course`: Create a new course.
- `DELETE /api/delete_course/:id`: Delete a course.
- `GET /api/get_results`: Get all results.
- `POST /api/create_result`: Create a new result.

## MongoDB Configuration
- MongoDB connection URI is configured in `app.py`.
- Modify the `format_date_from_db` and `format_date_to_db` functions for date formatting.

## Contributing
If you'd like to contribute to this project, please follow the guidelines in the CONTRIBUTING.md file.

## License
This project is licensed under the [MIT License](LICENSE).

## Acknowledgments
- Any credits or acknowledgments you'd like to include.
