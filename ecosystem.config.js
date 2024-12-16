module.exports = {
    apps: [
      {
        name: 'flask-app',
        script: '/var/www/html/vital-projects/vital-python/venv/bin/gunicorn', // Full path to gunicorn
        args: 'run:app --workers 3 --bind 0.0.0.0:3579', // Adjust if needed for your app
        interpreter: '/usr/bin/python3', // Use Python to execute Gunicorn
        cwd: '/var/www/html/vital-projects/vital-python',  // Your app directory
        env: {
          FLASK_APP: 'run.py',  // or your entry file
          FLASK_ENV: 'production',
        },
      },
    ],
  };
  