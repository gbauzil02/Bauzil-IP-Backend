# Bauzil-IP-Backend
This project consists of a Python backend using the Flask framework
In order to use this framework with the front end, you must use a virtual environment.

First install the virtual environment package using:

pip install virtualenv



To create virtual environment:
virtualenv venv



To activate virtual environment:

Windows: venv\Scripts\activate

Linux/MacOS: source venv/bin/activate
____________________________________________________________
To install Flask framework:

pip install Flask



Set the Flask app environment variable to index.py:

Windows: set FLASK_APP=index.py

Linux/MacOS: export FLASK_APP=index.py



To execute the Python file and launch the application run the command:

flask run 


Copy and paste the HTTP site that appears in the terminal into the search bar of your browser


____________________________________________________________

To run the pytest file:

Install pytest (command in installation section below)

On the command line, write:

python -m pytest 

____________________________________________________________

Installations (Good for Linux, MacOS, and Windows):

pip install fpdf

pip install Flask-Cors

pip install mysql-connector-python

pip install requests

pip install pytest




Sources and more information:

https://www.geeksforgeeks.org/flask-rendering-templates/
https://www.geeksforgeeks.org/how-to-install-flask-cors-in-python/
https://dev.mysql.com/doc/connector-python/en/connector-python-installation-binary.html
https://www.activestate.com/resources/quick-reads/how-to-pip-install-requests-python-package/

