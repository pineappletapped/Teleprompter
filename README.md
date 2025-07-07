# Teleprompter

This project now includes a simple Flask based web app that provides user registration, login and the ability to save teleprompter scripts.

## Running locally

```
pip install -r requirements.txt
python app.py
```

After starting the server, open `http://localhost:5000` in your browser.

## Deploying on Asura shared hosting

1. Upload the project files to your Python application directory.
2. Install the dependencies using Asura's Python package manager:
   `pip install --user -r requirements.txt`.
3. Point Asura's WSGI configuration to the provided `wsgi.py` file.
4. Set environment variables `SECRET_KEY` and (optionally) `DATABASE_URL`
   through Asura's control panel.
5. Restart the application from the hosting dashboard.

The `wsgi.py` file exposes the Flask application as `application`, which works
with most shared hosting WSGI setups.
