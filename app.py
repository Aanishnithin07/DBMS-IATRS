from flask import Flask, jsonify, request
from flask_cors import CORS
from db_connect import get_db_connection

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

@app.route('/')
def index():
    """
    Test route to verify the API is running.
    
    Returns:
        JSON response with success message
    """
    return jsonify({'message': 'ATS API is running successfully!'})

@app.route('/jobs', methods=['GET'])
def get_jobs():
    """
    Fetch all jobs from the Jobs table.
    
    Returns:
        JSON list of all jobs
    """
    connection = None
    cursor = None
    
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Jobs")
        jobs = cursor.fetchall()
        
        return jsonify(jobs), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
        
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

@app.route('/jobs/<int:id>', methods=['GET'])
def get_job(id):
    """
    Fetch a single job by its ID.
    
    Args:
        id: Job ID
        
    Returns:
        JSON object of the job or error message
    """
    connection = None
    cursor = None
    
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Jobs WHERE job_id = %s", (id,))
        job = cursor.fetchone()
        
        if job is None:
            return jsonify({'error': 'Job not found'}), 404
        
        return jsonify(job), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
        
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

@app.route('/jobs', methods=['POST'])
def create_job():
    """
    Create a new job posting.
    
    Expected JSON data:
        - title: Job title
        - department: Department name
        - location: Job location
        - recruiter_id: ID of the recruiter posting the job
        
    Returns:
        JSON success message or error
    """
    connection = None
    cursor = None
    
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'department', 'location', 'recruiter_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor()
        
        # Insert new job
        sql = """
            INSERT INTO Jobs (recruiter_id, title, department, location)
            VALUES (%s, %s, %s, %s)
        """
        values = (
            data['recruiter_id'],
            data['title'],
            data['department'],
            data['location']
        )
        
        cursor.execute(sql, values)
        connection.commit()
        
        return jsonify({
            'message': 'Job created successfully',
            'job_id': cursor.lastrowid
        }), 201
        
    except Exception as e:
        if connection:
            connection.rollback()
        return jsonify({'error': str(e)}), 500
        
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

@app.route('/apply', methods=['POST'])
def apply_for_job():
    """
    Allow a candidate to apply for a job.
    
    Expected JSON data:
        - candidate_id: ID of the candidate applying
        - job_id: ID of the job being applied to
        
    Returns:
        JSON success message or error
    """
    connection = None
    cursor = None
    
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'candidate_id' not in data or 'job_id' not in data:
            return jsonify({'error': 'Missing required fields: candidate_id and job_id'}), 400
        
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor()
        
        # Insert application
        sql = """
            INSERT INTO Applications (job_id, candidate_id, status)
            VALUES (%s, %s, 'Applied')
        """
        values = (data['job_id'], data['candidate_id'])
        
        cursor.execute(sql, values)
        connection.commit()
        
        return jsonify({
            'message': 'Application submitted successfully',
            'application_id': cursor.lastrowid
        }), 201
        
    except Exception as e:
        if connection:
            connection.rollback()
        return jsonify({'error': str(e)}), 500
        
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

@app.route('/applications', methods=['GET'])
def get_applications():
    """
    Fetch all applications with candidate and job details using SQL JOIN.
    
    Returns:
        JSON list of applications with joined data from Candidates and Jobs tables
    """
    connection = None
    cursor = None
    
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor(dictionary=True)
        
        # SQL JOIN query to fetch application details
        sql = """
            SELECT 
                a.application_id,
                c.full_name AS candidate_name,
                c.email AS candidate_email,
                j.title AS job_title,
                j.department,
                j.location,
                a.status,
                a.created_at
            FROM Applications a
            INNER JOIN Candidates c ON a.candidate_id = c.candidate_id
            INNER JOIN Jobs j ON a.job_id = j.job_id
            ORDER BY a.created_at DESC
        """
        
        cursor.execute(sql)
        applications = cursor.fetchall()
        
        return jsonify(applications), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
        
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
