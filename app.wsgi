import sys
import os

# Add the project directory to the Python path
sys.path.insert(0, '/var/www/html/vital-projects/vital-python')

# Activate virtual environment
activate_this = '/var/www/html/vital-projects/vital-python/venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

from <your_app_module> import <your_app_instance> as application
