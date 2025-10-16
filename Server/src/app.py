from flask import Flask
from flask_cors import CORS
from db import init_db
from routes import api_bp
from auth import auth_bp
import os

app = Flask(__name__)

# CORS Configuration
CORS(app)

# Initialize database
init_db()

# Register blueprints
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api')  # Register auth separately


# Error handling
@app.errorhandler(500)
def internal_error(error):
    return {'error': 'Something went wrong!'}, 500

@app.errorhandler(404)
def not_found(error):
    return {'error': 'Not found'}, 404

if __name__ == '__main__':
    PORT = int(os.getenv('PORT', 4000))
    print(f'🚀 Server running on http://localhost:{PORT}')
    print(f'📊 API available at http://localhost:{PORT}/api')
    app.run(debug=True, port=PORT, host='0.0.0.0')