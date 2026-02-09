from flask import Flask, jsonify
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)
