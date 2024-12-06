# from app import create_app
# from flask_cors import CORS
# import os
# from dotenv import load_dotenv

# # Load environment variables from .env file
# load_dotenv()

# app = create_app()
# CORS(app)

# if __name__ == '__main__':
#     # Get values from environment variables
#     host = os.getenv('FLASK_RUN_HOST', '127.0.0.1')  # Default is '127.0.0.1'
#     port = int(os.getenv('FLASK_RUN_PORT', 5000))  # Default is 5000
#     debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'  # Convert to boolean

#     app.run(host=host, port=port, debug=debug)



from app import create_app
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = create_app()

# Configure CORS
CORS(
    app,
    resources={r"/*": {"origins": "*"}},  # Allow all origins for all routes
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Allowed methods
    allow_headers=["Content-Type", "Authorization"],  # Allowed headers
)

if __name__ == '__main__':
    # Get values from environment variables
    host = os.getenv('FLASK_RUN_HOST', '0.0.0.0')  # Default is '127.0.0.1'
    port = int(os.getenv('FLASK_RUN_PORT', 3001))  # Default is 5000
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'  # Convert to boolean

    app.run(host=host, port=port, debug=debug)
