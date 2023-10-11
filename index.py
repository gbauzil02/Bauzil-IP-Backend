from flask import Flask, render_template, url_for, redirect, request, Response
import requests
import json
import flask
from flask_cors import CORS
import mysql.connector
import decimal
from fpdf import FPDF
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
import re
from flask import jsonify 

app = Flask(__name__)
CORS(app)
class APIError(Exception):
    """All custom API Exceptions"""
    pass

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        return super().default(o)
class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)

class MultipleJsonEncoders():
    """
    Combine multiple JSON encoders
    """
    def __init__(self, *encoders):
        self.encoders = encoders
        self.args = ()
        self.kwargs = {}

    def default(self, obj):
        for encoder in self.encoders:
            try:
                return encoder(*self.args, **self.kwargs).default(obj)
            except TypeError:
                pass
        raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')

    def __call__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        enc = json.JSONEncoder(*args, **kwargs)
        enc.default = self.default
        return enc



# Root address of the backend
@app.route('/')
def index():
    return render_template('index.html')

# Links to other html frontend pages
@app.route('/movies')
def movies():
    return render_template('movies.html')

@app.route('/customer')
def customer():
    return render_template('customer.html')


# Gets top 5 movies in descending order for home page
@app.route('/films', methods=["GET"])
def films():
    cnx = mysql.connector.connect(user='root', password='password',
                              host='127.0.0.1',
                              database='sakila')
    cursor = cnx.cursor()

    query = ("SELECT top.film_id, film.title,  top.rentals " 
    "FROM(SELECT DISTINCT film_id, COUNT(*) as rentals " 
    "FROM rental "
    "JOIN inventory "
    "ON rental.inventory_id = inventory.inventory_id "
    "GROUP BY film_id ORDER BY rentals DESC LIMIT 5) AS top "
    "JOIN film ON film.film_id = top.film_id;")
    cursor.execute(query)
    row_headers=[x[0] for x in cursor.description] #this will extract row headers
    myresult = cursor.fetchall()
    json_data=[]
    for result in myresult:
        json_data.append(dict(zip(row_headers,result)))
    return json.dumps(json_data)

# Gets top 5 actors in descending order for home page
@app.route('/actors', methods=["GET"])
def actors():
    cnx = mysql.connector.connect(user='root', password='password',
                              host='127.0.0.1',
                              database='sakila')
    cursor = cnx.cursor()

    query = ("SELECT actor_films.actor_id, actor_films.first_name, actor_films.last_name, COUNT(*) as movies "
    "FROM( "
    "SELECT actor.actor_id, actor.first_name, actor.last_name, film_actor.film_id "
    "FROM actor "
    "JOIN film_actor "
    "ON actor.actor_id = film_actor.actor_id) AS actor_films "
    "GROUP BY actor_films.actor_id, actor_films.first_name, actor_films.last_name "
    "ORDER BY movies DESC "
    "LIMIT 5;")
    cursor.execute(query)
    row_headers=[x[0] for x in cursor.description] #this will extract row headers
    myresult = cursor.fetchall()
    json_data=[]
    for result in myresult:
        json_data.append(dict(zip(row_headers,result)))
    return json.dumps(json_data)

# Gets movies by first name
@app.route('/getName', methods=["POST"])
def getName():
    received_data = request.get_json()
    cnx = mysql.connector.connect(user='root', password='password',
                              host='127.0.0.1',
                              database='sakila')
    cursor = cnx.cursor()
    query = ("SELECT f.film_id, f.title, f.description, f.release_year, f.rental_duration, f.rental_rate, f.length, f.rating, f.special_features, category.name as genre "
            "FROM ( "
                "SELECT film.film_id, film.title, film.description, film.release_year, film.rental_duration, film.rental_rate, film.length, film.rating, film.special_features, film_category.category_id "
                "FROM film "
                "JOIN film_category "
                "ON film.film_id = film_category.film_id) as f "
            "JOIN category "
            "ON category.category_id = f.category_id "
            "WHERE f.title = %s;")
    cursor.execute(query,(received_data["data"],))
    print(f"received data: {received_data}")
    row_headers=[x[0] for x in cursor.description] #this will extract row headers
    myresult = cursor.fetchall()
    json_data=[]
    for result in myresult:
        json_data.append(dict(zip(row_headers,result)))
    encoder = MultipleJsonEncoders(DecimalEncoder, SetEncoder)
    return flask.Response(response=json.dumps(json_data, cls=encoder), status=201)

# Gets movies by genre
@app.route('/genre', methods=["POST"])
def genre():
    received_data = request.get_json()
    cnx = mysql.connector.connect(user='root', password='password',
                              host='127.0.0.1',
                              database='sakila')
    cursor = cnx.cursor()
    query = ("SELECT f.film_id, f.title, f.description, f.release_year, f.rental_duration, f.rental_rate, f.length, f.rating, f.special_features, category.name as genre "
            "FROM ( "
                "SELECT film.film_id, film.title, film.description, film.release_year, film.rental_duration, film.rental_rate, film.length, film.rating, film.special_features, film_category.category_id "
                "FROM film "
                "JOIN film_category "
                "ON film.film_id = film_category.film_id) as f "
            "JOIN category "
            "ON category.category_id = f.category_id "
            "WHERE category.name = %s " 
            "LIMIT 1000;")
    cursor.execute(query,(received_data["data"],))
    print(f"received data: {received_data}")
    row_headers=[x[0] for x in cursor.description] #this will extract row headers
    myresult = cursor.fetchall()
    json_data=[]
    for result in myresult:
        json_data.append(dict(zip(row_headers,result)))
    encoder = MultipleJsonEncoders(DecimalEncoder, SetEncoder)
    return flask.Response(response=json.dumps(json_data, cls=encoder), status=201)

# Gets movies by actor's first and last name
@app.route('/byActor', methods=["POST"])
def byActor():
    received_data = request.get_json()
    cnx = mysql.connector.connect(user='root', password='password',
                              host='127.0.0.1',
                              database='sakila')
    cursor = cnx.cursor()
    query = ("SELECT faf3.title, faf3.description, faf3.release_year, faf3.rental_duration, faf3.rental_rate, faf3.length, faf3.rating, faf3.special_features, category.name as genre, faf3.first_name, faf3.last_name "
    "FROM "
        "(SELECT faf2.film_id, faf2.title, faf2.description, faf2.release_year, faf2.rental_duration, faf2.rental_rate, faf2.length, faf2.rating, faf2.special_features, faf2.first_name, faf2.last_name, film_category.category_id "
        "FROM "
            "(SELECT faf.film_id, faf.title, faf.description, faf.release_year, faf.rental_duration, faf.rental_rate, faf.length, faf.rating, faf.special_features, actor.first_name, actor.last_name "
            "FROM "
                "(SELECT film.film_id, film.title, film.description, film.release_year, film.rental_duration, film.rental_rate, film.length, film.rating, film.special_features, film_actor.actor_id "
                "FROM film_actor "
                "JOIN film "
                "ON film_actor.film_id = film.film_id) as faf "
            "JOIN actor "
            "ON actor.actor_id = faf.actor_id) as faf2 "
        "JOIN film_category "
        "ON film_category.film_id = faf2.film_id) as faf3 "
    "JOIN category "
    "ON category.category_id = faf3.category_id "
    "WHERE faf3.first_name = %s AND faf3.last_name = %s;")
    data = received_data["data"].split(' ')
    cursor.execute(query,(data[0],data[1]))
    print(f"received data: {received_data}")
    row_headers=[x[0] for x in cursor.description] #this will extract row headers
    myresult = cursor.fetchall()
    json_data=[]
    for result in myresult:
        json_data.append(dict(zip(row_headers,result)))
    encoder = MultipleJsonEncoders(DecimalEncoder, SetEncoder)
    return flask.Response(response=json.dumps(json_data, cls=encoder), status=201)

# Gets the first 10 customers in the customer table
@app.route('/getCust', methods=["GET"])
def getCust():
    received_data = request.get_json()
    cnx = mysql.connector.connect(user='root', password='password',
                              host='127.0.0.1',
                              database='sakila')
    cursor = cnx.cursor()
    query = ("SELECT customer_id, first_name, last_name "
            "FROM customer " 
            "LIMIT 10")
    cursor.execute(query)
    row_headers=[x[0] for x in cursor.description] #this will extract row headers
    myresult = cursor.fetchall()
    json_data=[]
    for result in myresult:
        json_data.append(dict(zip(row_headers,result)))
    return json.dumps(json_data)

# Gets customer information using id
@app.route('/getId', methods=["POST"])
def getId():
    received_data = request.get_json()
    cnx = mysql.connector.connect(user='root', password='password',
                              host='127.0.0.1',
                              database='sakila')
    cursor = cnx.cursor()
    query = ("SELECT c2.customer_id, c2.store_id, c2.first_name, c2.last_name, c2.email, c2.address, c2.district, c2.postal_code, c2.phone, c2.city, c2.country "
            "FROM( "
                "SELECT c.customer_id, c.store_id, c.first_name, c.last_name, c.email, addr.address, addr.district, addr.postal_code, addr.phone,addr.city, addr.country "
                "FROM Customer as c "
                "JOIN (SELECT a.address_id, a.address, a.district, a.postal_code, a.phone, c.city, c.country "
                    "FROM address as a "
                    "JOIN (SELECT city.city_id, city.city, country.country " 
                        "FROM city "
                        "JOIN country "
                        "ON city.country_id = country.country_id) as c "
                    "ON c.city_id = a.city_id) as addr "
                "ON c.address_id = addr.address_id) as c2 "
            "WHERE c2.customer_id = %s;") 
    cursor.execute(query, (int(received_data["data"]),))
    print(f"received data: {received_data}")
    row_headers=[x[0] for x in cursor.description] #this will extract row headers
    myresult = cursor.fetchall()
    json_data=[]
    for result in myresult:
        json_data.append(dict(zip(row_headers,result)))
    
    cursor = cnx.cursor()
    query = ("SELECT film.title as returned "
            "FROM film "
            "JOIN( "
                "SELECT rental.customer_id, inventory.film_id "
                "FROM rental "
                "JOIN inventory "
                "ON inventory.inventory_id = rental.inventory_id "
                "WHERE rental.customer_id = %s AND return_date IS NOT NULL) AS R2 "
            "WHERE film.film_id = R2.film_id") 
    cursor.execute(query, (int(received_data["data"]),))
    row_headers=[x[0] for x in cursor.description] #this will extract row headers
    myresult = cursor.fetchall()
    json_data2=[]
    for result in myresult:
        json_data2.append(dict(zip(row_headers,result)))
    print(json_data2)

    test = {}
    test['returned'] = json_data2
    json_data.append(test)
    print()

    cursor = cnx.cursor()
    query = ("SELECT film.title as not_returned "
            "FROM film "
            "JOIN( "
                "SELECT rental.customer_id, inventory.film_id "
                "FROM rental "
                "JOIN inventory "
                "ON inventory.inventory_id = rental.inventory_id "
                "WHERE rental.customer_id = %s AND return_date IS NULL) AS R2 "
            "WHERE film.film_id = R2.film_id") 
    cursor.execute(query, (int(received_data["data"]),))
    row_headers=[x[0] for x in cursor.description] #this will extract row headers
    myresult = cursor.fetchall()
    json_data3=[]
    for result in myresult:
        json_data3.append(dict(zip(row_headers,result)))
    print(json_data3)

    test = {}
    test['not_returned'] = json_data3
    json_data.append(test)

    print(json_data)


    encoder = MultipleJsonEncoders(DecimalEncoder, SetEncoder)
    return flask.Response(response=json.dumps(json_data, cls=encoder), status=201)

# Gets customer when using id
@app.route('/custById', methods=["POST"])
def custById():
    received_data = request.get_json()
    cnx = mysql.connector.connect(user='root', password='password',
                              host='127.0.0.1',
                              database='sakila')
    cursor = cnx.cursor()
    query = ("SELECT customer_id, first_name, last_name "
            "FROM customer " 
            "WHERE customer_id = %s")
    cursor.execute(query, (int(received_data["data"]),))
    print(f"received data: {received_data}")
    row_headers=[x[0] for x in cursor.description] #this will extract row headers
    myresult = cursor.fetchall()
    json_data=[]
    for result in myresult:
        json_data.append(dict(zip(row_headers,result)))
    print(json_data)
    encoder = MultipleJsonEncoders(DecimalEncoder, SetEncoder)
    return flask.Response(response=json.dumps(json_data, cls=encoder), status=201)

# Gets customer when using first name
@app.route('/custByFirst', methods=["POST"])
def custByFirst():
    received_data = request.get_json()
    cnx = mysql.connector.connect(user='root', password='password',
                              host='127.0.0.1',
                              database='sakila')
    cursor = cnx.cursor()
    query = ("SELECT customer_id, first_name, last_name "
            "FROM customer " 
            "WHERE first_name = %s")
    cursor.execute(query, (received_data["data"],))
    print(f"received data: {received_data}")
    row_headers=[x[0] for x in cursor.description] #this will extract row headers
    myresult = cursor.fetchall()
    json_data=[]
    for result in myresult:
        json_data.append(dict(zip(row_headers,result)))
    print(json_data)
    encoder = MultipleJsonEncoders(DecimalEncoder, SetEncoder)
    return flask.Response(response=json.dumps(json_data, cls=encoder), status=201)

#Gets customer when using last name
@app.route('/custByLast', methods=["POST"])
def custByLast():
    received_data = request.get_json()
    cnx = mysql.connector.connect(user='root', password='password',
                              host='127.0.0.1',
                              database='sakila')
    cursor = cnx.cursor()
    query = ("SELECT customer_id, first_name, last_name "
            "FROM customer " 
            "WHERE last_name = %s")
    cursor.execute(query, (received_data["data"],))
    print(f"received data: {received_data}")
    row_headers=[x[0] for x in cursor.description] #this will extract row headers
    myresult = cursor.fetchall()
    json_data=[]
    for result in myresult:
        json_data.append(dict(zip(row_headers,result)))
    print(json_data)
    encoder = MultipleJsonEncoders(DecimalEncoder, SetEncoder)
    return flask.Response(response=json.dumps(json_data, cls=encoder), status=201)

# Gets the top 5 actor films in descending order
@app.route('/topActFilms', methods=["POST"])
def topActFilms():
    received_data = request.get_json()
    cnx = mysql.connector.connect(user='root', password='password',
                              host='127.0.0.1',
                              database='sakila')
    cursor = cnx.cursor()
    query = ("SELECT fa2.actor_id, fa2.film_id, fa2.first_name, fa2.last_name, fa2.film_id, fa2.title, rent.rentals "
            "FROM "
            "(SELECT fa.actor_id, fa.film_id, fa.first_name, fa.last_name, film.title "
            "FROM "
            "(SELECT film_actor.actor_id, film_actor.film_id, actor.first_name, actor.last_name "
            "FROM film_actor "
            "JOIN actor "
            "ON actor.actor_id = film_actor.actor_id) as fa "
            "JOIN film "
            "ON film.film_id = fa.film_id) as fa2 "
            "JOIN "
            "(SELECT top.film_id, film.title, top.rentals "
            "FROM( "
                "SELECT DISTINCT film_id, COUNT(*) as rentals "
                "FROM rental "
                "JOIN inventory "
                "ON rental.inventory_id = inventory.inventory_id "
                "GROUP BY film_id) AS top "
            "JOIN film "
            "ON film.film_id = top.film_id "
            "ORDER BY top.rentals DESC) as rent "
            "ON fa2.film_id = rent.film_id "
            "WHERE fa2.first_name = %s AND fa2.last_name = %s " 
            "ORDER BY top.rentals DESC "
            "LIMIT 5;")
    data = received_data["data"].split(' ')
    cursor.execute(query,(data[0],data[1]))
    print(f"received data: {received_data}")
    row_headers=[x[0] for x in cursor.description] #this will extract row headers
    myresult = cursor.fetchall()
    json_data=[]
    for result in myresult:
        json_data.append(dict(zip(row_headers,result)))
    encoder = MultipleJsonEncoders(DecimalEncoder, SetEncoder)
    return flask.Response(response=json.dumps(json_data, cls=encoder), status=201)

class APIAuthError(Exception):
  code = 403
  description = "Authentication Error"

@app.errorhandler(APIError)
def handle_exception(err):
    """Return custom JSON when APIError or its children are raised"""
    response = {"error": err.description, "message": ""}
    if len(err.args) > 0:
        response["message"] = err.args[0]
    # Add some logging so that we can monitor different types of errors 
    app.logger.error(f'{err.description}: {response["message"]}')
    print(jsonify(response))
    return jsonify(response), err.code

# NOT COMPLETE - Adding customer after filling out form
@app.route('/addCust', methods=["GET","POST"])
def addCust():
    valid_stores = [1,2]
    received_data = request.get_json()
    print(f"received data: {received_data}")
    if not received_data["store"].isdigit():
        return ('', 600)

    print(int(received_data["store"]) == 2)
    if int(received_data["store"]) != 1:
        if int(received_data["store"]) != 2:
        # resp = ['{"message": "Please pick a valid store"}']
        # print(resp)
        # return flask.Response(response=json.dumps(resp), status=205)
            return ('', 600)
        # raise APIAuthError("Please pick a valid store")
    print(2)
    if not re.search(".*@.*\..*", received_data["email"]):
    # if "@" not in received_data["email"] and "." :
        # resp = [{'message': 'Please give a valid email'}]
        # encoder = MultipleJsonEncoders(DecimalEncoder, SetEncoder)
        # return flask.Response(response=json.dumps(resp, cls=encoder), status=205)
        return ('', 601)
    print(3)
    x = received_data["address"].split(' ')
    if not x[0].isdigit():
        # resp = [{'message': 'Please give a valid address'}]
        # encoder = MultipleJsonEncoders(DecimalEncoder, SetEncoder)
        # return flask.Response(response=json.dumps(resp, cls=encoder), status=205)
        return ('', 602)
    
    if not received_data["postal"].isdigit():
        # resp = [{'message': 'Please give a valid address'}]
        # encoder = MultipleJsonEncoders(DecimalEncoder, SetEncoder)
        # return flask.Response(response=json.dumps(resp, cls=encoder), status=205)
        return ('', 604)
    
    if not received_data["phone"].isdigit():
        # resp = [{'message': 'Please give a valid address'}]
        # encoder = MultipleJsonEncoders(DecimalEncoder, SetEncoder)
        # return flask.Response(response=json.dumps(resp, cls=encoder), status=205)
        return ('', 605)
    print(4)
    cnx = mysql.connector.connect(user='root', password='password',
                              host='127.0.0.1',
                              database='sakila')
    cursor = cnx.cursor()
    query = ("SELECT city_id  "
            "FROM city "
            "WHERE city = %s")
    cursor.execute(query, (received_data["city"],))
    row_headers=[x[0] for x in cursor.description] #this will extract row headers
    myresult = cursor.fetchall()
    if myresult == []:
        cursor = cnx.cursor()
        query = ("SELECT country_id  "
                "FROM country "
                "WHERE country = %s")
        cursor.execute(query, (received_data["country"],))
        row_headers=[x[0] for x in cursor.description] #this will extract row headers
        myresult = cursor.fetchall()
        if myresult == []:
            cursor = cnx.cursor()
            query = ("SELECT MAX(country_id) as country_id "
                    "FROM country;")
            cursor.execute(query)
            row_headers=[x[0] for x in cursor.description] #this will extract row headers
            myresult = cursor.fetchall()
            json_data=[]
            for result in myresult:
                json_data.append(dict(zip(row_headers,result)))
            new_id = str(int(json_data[0]["country_id"]) + 1)

            cursor = cnx.cursor()
            query = ("INSERT INTO country(country_id, country) VALUES (%s, %s);")
            cursor.execute(query, (new_id, received_data["country"].title(),))
            cnx.commit()
            country_id = new_id
        else:
            json_data=[]
            for result in myresult:
                json_data.append(dict(zip(row_headers,result)))
            country_id = json_data[0]["country_id"]

        cursor = cnx.cursor()
        query = ("SELECT MAX(city_id) as city_id "
                "FROM city;")
        cursor.execute(query)
        row_headers=[x[0] for x in cursor.description] #this will extract row headers
        myresult = cursor.fetchall()
        json_data=[]
        for result in myresult:
            json_data.append(dict(zip(row_headers,result)))
        city_id = str(int(json_data[0]["city_id"]) + 1)

        cursor = cnx.cursor()
        query = ("INSERT INTO city(city_id, city, country_id) VALUES (%s, %s, %s);")
        cursor.execute(query, (city_id, received_data["city"].title(), country_id,))
        cnx.commit()

        cursor = cnx.cursor()
        query = ("SELECT city_id  "
                "FROM city "
                "WHERE city = %s")
        cursor.execute(query, (received_data["city"],))
        row_headers=[x[0] for x in cursor.description] #this will extract row headers
        myresult = cursor.fetchall()
        json_data=[]
        for result in myresult:
            json_data.append(dict(zip(row_headers,result)))
        city_id = json_data[0]["city_id"]
    else:
        json_data=[]
        for result in myresult:
            json_data.append(dict(zip(row_headers,result)))
        city_id = json_data[0]["city_id"]
    print(5)
    cursor = cnx.cursor()
    query = ("SELECT MAX(address_id) as address_id "
            "FROM address;")
    cursor.execute(query)
    row_headers=[x[0] for x in cursor.description] #this will extract row headers
    myresult = cursor.fetchall()
    json_data=[]
    for result in myresult:
        json_data.append(dict(zip(row_headers,result)))
    address_id = str(int(json_data[0]["address_id"]) + 1)
    print(6)
    cursor = cnx.cursor()
    query = ("INSERT INTO address(address_id, address, district, city_id, postal_code, phone, location) "
            "VALUES (%s, %s, %s, %s, %s, %s, POINT(0,0));")
    cursor.execute(query, (address_id, received_data["address"].title(), received_data["district"].title(),city_id, received_data["postal"], received_data["phone"],))
    cnx.commit()
    print(8)
    cursor = cnx.cursor()
    query = ("SELECT MAX(customer_id) as customer_id "
            "FROM customer;")
    cursor.execute(query)
    row_headers=[x[0] for x in cursor.description] #this will extract row headers
    myresult = cursor.fetchall()
    json_data=[]
    for result in myresult:
        json_data.append(dict(zip(row_headers,result)))
    customer_id = str(int(json_data[0]["customer_id"]) + 1)
    print(9)
    cursor = cnx.cursor()
    query = ("INSERT INTO customer(customer_id, store_id, first_name, last_name, email, address_id, active) "
            "VALUES (%s, %s, %s, %s, %s, %s, 1);")
    cursor.execute(query, (customer_id, received_data["store"], received_data["first"].upper(), received_data["last"].upper(), received_data["email"], address_id,))
    cnx.commit()

    return ('', 204)


#testing adding a customer
@app.route('/test', methods=["GET"])
def test():
    print("1")
    cnx = mysql.connector.connect(user='root', password='password',
                              host='127.0.0.1',
                              database='sakila')
    cursor = cnx.cursor()
    query = ("SELECT MAX(customer_id) as customer_id "
            "FROM customer;")
    cursor.execute(query)
    row_headers=[x[0] for x in cursor.description] #this will extract row headers
    myresult = cursor.fetchall()
    json_data=[]
    for result in myresult:
        json_data.append(dict(zip(row_headers,result)))
    new_id = int(json_data[0]["customer_id"]) + 1
    print(new_id)
    print("2")

    cursor = cnx.cursor()
    query = ("SELECT MAX(address_id) as address_id "
            "FROM customer;")
    cursor.execute(query)
    row_headers=[x[0] for x in cursor.description] #this will extract row headers
    myresult = cursor.fetchall()
    json_data=[]
    for result in myresult:
        json_data.append(dict(zip(row_headers,result)))
    new_id = int(json_data[0]["address_id"]) + 1
    print(new_id)
    return json.dumps(json_data)

@app.route('/editCust', methods=["GET","POST"])
def editCust():
    received_data = request.get_json()
    print(f"received data: {received_data}")

    cnx = mysql.connector.connect(user='root', password='password',
                              host='127.0.0.1',
                              database='sakila')
    if not received_data["customer_id"].isdigit():
            return ('', 603)      

    cursor = cnx.cursor()
    query = ("SELECT MAX(customer_id) as customer_id "
            "FROM customer;")
    cursor.execute(query)
    row_headers=[x[0] for x in cursor.description] #this will extract row headers
    myresult = cursor.fetchall()
    json_data=[]
    for result in myresult:
        json_data.append(dict(zip(row_headers,result)))
    max_id = int(json_data[0]["customer_id"])

    if int(received_data["customer_id"]) > max_id:
        return ('', 603)
    

    if received_data["store"] != "":
        if not received_data["store"].isdigit():
            return ('', 600)

        print(int(received_data["store"]) == 2)
        if int(received_data["store"]) != 1:
            if int(received_data["store"]) != 2:
                return ('', 600)
        
        cursor = cnx.cursor()
        query = ("UPDATE Customer "
                "SET store_id = %s "
                "WHERE customer_id = %s")
        cursor.execute(query, (received_data["store"],received_data["customer_id"]))
        cnx.commit()

    if received_data["first"] != "":
        cursor = cnx.cursor()
        query = ("UPDATE Customer "
                "SET first_name = %s "
                "WHERE customer_id = %s")
        cursor.execute(query, (received_data["first"].upper(),received_data["customer_id"]))
        cnx.commit()

    if received_data["last"] != "":
        cursor = cnx.cursor()
        query = ("UPDATE Customer "
                "SET last_name = %s "
                "WHERE customer_id = %s")
        cursor.execute(query, (received_data["last"].upper(),received_data["customer_id"]))
        cnx.commit()
        
        
    print(2)
    if received_data["email"] != "":
        if not re.search(".*@.*\..*", received_data["email"]):
            return ('', 601)
        cursor = cnx.cursor()
        query = ("UPDATE Customer "
                "SET email = %s "
                "WHERE customer_id = %s")
        cursor.execute(query, (received_data["email"],received_data["customer_id"]))
        cnx.commit()

    print(3)

    if received_data["address"] != "":
        x = received_data["address"].split(' ')
        if not x[0].isdigit():
            # resp = [{'message': 'Please give a valid address'}]
            # encoder = MultipleJsonEncoders(DecimalEncoder, SetEncoder)
            # return flask.Response(response=json.dumps(resp, cls=encoder), status=205)
            return ('', 602)

        cursor = cnx.cursor()
        query = ("SELECT address_id "
                "FROM Customer "
                "WHERE customer_id = %s")
        cursor.execute(query, (int(received_data["customer_id"]),))
        row_headers=[x[0] for x in cursor.description] #this will extract row headers
        myresult = cursor.fetchall()
        json_data=[]
        for result in myresult:
            json_data.append(dict(zip(row_headers,result)))
        addr_id = str(json_data[0]["address_id"])

        cursor = cnx.cursor()
        query = ("UPDATE address "
                "SET address = %s "
                "WHERE address_id = %s ") 
        cursor.execute(query, (received_data["address"], addr_id))
        cnx.commit()

    if received_data["district"] != "":
        cursor = cnx.cursor()
        query = ("SELECT address_id "
                "FROM Customer "
                "WHERE customer_id = %s")
        cursor.execute(query, (int(received_data["customer_id"]),))
        row_headers=[x[0] for x in cursor.description] #this will extract row headers
        myresult = cursor.fetchall()
        json_data=[]
        for result in myresult:
            json_data.append(dict(zip(row_headers,result)))
        addr_id = str(json_data[0]["address_id"])

        cursor = cnx.cursor()
        query = ("UPDATE address "
                "SET district = %s "
                "WHERE address_id = %s ") 
        cursor.execute(query, (received_data["district"], addr_id))
        cnx.commit()

    if received_data["postal"] != "":
        if not received_data["postal"].isdigit():
            # resp = [{'message': 'Please give a valid address'}]
            # encoder = MultipleJsonEncoders(DecimalEncoder, SetEncoder)
            # return flask.Response(response=json.dumps(resp, cls=encoder), status=205)
            return ('', 604)

        cursor = cnx.cursor()
        query = ("SELECT address_id "
                "FROM Customer "
                "WHERE customer_id = %s")
        cursor.execute(query, (received_data["customer_id"]))
        row_headers=[x[0] for x in cursor.description] #this will extract row headers
        myresult = cursor.fetchall()
        json_data=[]
        for result in myresult:
            json_data.append(dict(zip(row_headers,result)))
        addr_id = str(json_data[0]["address_id"])

        cursor = cnx.cursor()
        query = ("UPDATE address "
                "SET postal_code = %s "
                "WHERE address_id = %s ") 
        cursor.execute(query, (received_data["postal"], addr_id))
        cnx.commit()
    
    if received_data["phone"] != "":
        if not received_data["phone"].isdigit():
            # resp = [{'message': 'Please give a valid address'}]
            # encoder = MultipleJsonEncoders(DecimalEncoder, SetEncoder)
            # return flask.Response(response=json.dumps(resp, cls=encoder), status=205)
            return ('', 605)

        cursor = cnx.cursor()
        query = ("SELECT address_id "
                "FROM Customer "
                "WHERE customer_id = %s")
        cursor.execute(query, (int(received_data["customer_id"]),))
        row_headers=[x[0] for x in cursor.description] #this will extract row headers
        myresult = cursor.fetchall()
        json_data=[]
        for result in myresult:
            json_data.append(dict(zip(row_headers,result)))
        addr_id = str(json_data[0]["address_id"])

        cursor = cnx.cursor()
        query = ("UPDATE address "
                "SET phone = %s "
                "WHERE address_id = %s ") 
        cursor.execute(query, (received_data["phone"], addr_id))
        cnx.commit()
    
    if received_data["city"] != "":
        cursor = cnx.cursor()
        query = ("SELECT address_id "
                "FROM Customer "
                "WHERE customer_id = %s")
        cursor.execute(query, (int(received_data["customer_id"]),))
        row_headers=[x[0] for x in cursor.description] #this will extract row headers
        myresult = cursor.fetchall()
        json_data=[]
        for result in myresult:
            json_data.append(dict(zip(row_headers,result)))
        addr_id = int(json_data[0]["address_id"])

        cursor = cnx.cursor()
        query = ("SELECT city_id "
                "FROM address "
                "WHERE address_id = %s ") 
        cursor.execute(query, (addr_id,))
        row_headers=[x[0] for x in cursor.description] #this will extract row headers
        myresult = cursor.fetchall()
        json_data=[]
        for result in myresult:
            json_data.append(dict(zip(row_headers,result)))
        city_id = str(json_data[0]["city_id"])

        cursor = cnx.cursor()
        query = ("SELECT country_id "
                "FROM city "
                "WHERE city_id = %s ") 
        cursor.execute(query, (city_id,))
        row_headers=[x[0] for x in cursor.description] #this will extract row headers
        myresult = cursor.fetchall()
        json_data=[]
        for result in myresult:
            json_data.append(dict(zip(row_headers,result)))
        country_id = str(json_data[0]["country_id"])


        cursor = cnx.cursor()
        query = ("SELECT city_id, country_id "
                "FROM city "
                "WHERE city = %s ") 
        cursor.execute(query, (received_data["city"],))
        row_headers=[x[0] for x in cursor.description] #this will extract row headers
        myresult = cursor.fetchall()
        
        #Check if city exists
        if myresult != []:
            json_data = []
            for result in myresult:
                json_data.append(dict(zip(row_headers,result)))
            city_id = str(json_data[0]["city_id"])
            old_country_id = str(json_data[0]["country_id"])
            #check if there is a new country
            if received_data["country"] != "":
                #insert the country
                cursor = cnx.cursor()
                query = ("SELECT MAX(country_id) as country_id "
                        "FROM country;")
                cursor.execute(query)
                row_headers=[x[0] for x in cursor.description] #this will extract row headers
                myresult = cursor.fetchall()
                json_data=[]
                for result in myresult:
                    json_data.append(dict(zip(row_headers,result)))
                new_id = str(int(json_data[0]["country_id"]) + 1)

                cursor = cnx.cursor()
                query = ("INSERT INTO country(country_id, country) VALUES (%s, %s);")
                cursor.execute(query, (new_id, received_data["country"].title(),))
                cnx.commit()
                country_id = new_id

                #insert city and new country id
                cursor = cnx.cursor()
                query = ("SELECT MAX(city_id) as city_id "
                        "FROM city;")
                cursor.execute(query)
                row_headers=[x[0] for x in cursor.description] #this will extract row headers
                myresult = cursor.fetchall()
                json_data=[]
                for result in myresult:
                    json_data.append(dict(zip(row_headers,result)))
                city_id = str(int(json_data[0]["city_id"]) + 1)

                cursor = cnx.cursor()
                query = ("INSERT INTO city(city_id, city, country_id) VALUES (%s, %s, %s);")
                cursor.execute(query, (city_id, received_data["city"].title(), country_id,))
                cnx.commit()

                #update address
                cursor = cnx.cursor()
                query = ("UPDATE address "
                        "SET city_id = %s "
                        "WHERE address_id = %s ") 
                cursor.execute(query, (city_id, addr_id))
                cnx.commit()

            #else
            else:
                good = False
                for i in json_data:
                    if country_id == i['country_id']:
                        #update address
                        cursor = cnx.cursor()
                        query = ("UPDATE address "
                                "SET city_id = %s "
                                "WHERE address_id = %s ") 
                        cursor.execute(query, (i[city_id], addr_id))
                        cnx.commit()
                        good = True
                if not good:


                    cursor = cnx.cursor()
                    query = ("SELECT MAX(city_id) as city_id "
                            "FROM city;")
                    cursor.execute(query)
                    row_headers=[x[0] for x in cursor.description] #this will extract row headers
                    myresult = cursor.fetchall()
                    json_data=[]
                    for result in myresult:
                        json_data.append(dict(zip(row_headers,result)))
                    city_id = str(int(json_data[0]["city_id"]) + 1)

                    cursor = cnx.cursor()
                    query = ("INSERT INTO city(city_id, city, country_id) VALUES (%s, %s, %s);")
                    cursor.execute(query, (city_id, received_data["city"].title(), country_id,))
                    cnx.commit()

                    cursor = cnx.cursor()
                    query = ("UPDATE address "
                            "SET city_id = %s "
                            "WHERE address_id = %s ") 
                    cursor.execute(query, (city_id, addr_id))
                    cnx.commit()


        #else
        else:
            #check if there is a new country
            if received_data["country"] != "":
                #insert country
                cursor = cnx.cursor()
                query = ("SELECT MAX(country_id) as country_id "
                        "FROM country;")
                cursor.execute(query)
                row_headers=[x[0] for x in cursor.description] #this will extract row headers
                myresult = cursor.fetchall()
                json_data=[]
                for result in myresult:
                    json_data.append(dict(zip(row_headers,result)))
                new_id = str(int(json_data[0]["country_id"]) + 1)

                cursor = cnx.cursor()
                query = ("INSERT INTO country(country_id, country) VALUES (%s, %s);")
                cursor.execute(query, (new_id, received_data["country"].title(),))
                cnx.commit()
                country_id = new_id

                #insert new city and country
                cursor = cnx.cursor()
                query = ("SELECT MAX(city_id) as city_id "
                        "FROM city;")
                cursor.execute(query)
                row_headers=[x[0] for x in cursor.description] #this will extract row headers
                myresult = cursor.fetchall()
                json_data=[]
                for result in myresult:
                    json_data.append(dict(zip(row_headers,result)))
                city_id = str(int(json_data[0]["city_id"]) + 1)

                cursor = cnx.cursor()
                query = ("INSERT INTO city(city_id, city, country_id) VALUES (%s, %s, %s);")
                cursor.execute(query, (city_id, received_data["city"].title(), country_id,))
                cnx.commit()

                #update address
                cursor = cnx.cursor()
                query = ("UPDATE address "
                        "SET city_id = %s "
                        "WHERE address_id = %s ") 
                cursor.execute(query, (city_id, addr_id))
                cnx.commit()
            #else
            else:
                cursor = cnx.cursor()
                query = ("SELECT MAX(city_id) as city_id "
                        "FROM city;")
                cursor.execute(query)
                row_headers=[x[0] for x in cursor.description] #this will extract row headers
                myresult = cursor.fetchall()
                json_data=[]
                for result in myresult:
                    json_data.append(dict(zip(row_headers,result)))
                city_id = str(int(json_data[0]["city_id"]) + 1)

                #insert new city with old country
                cursor = cnx.cursor()
                query = ("INSERT INTO city(city_id, city, country_id) VALUES (%s, %s, %s);")
                cursor.execute(query, (city_id, received_data["city"].title(), country_id,))
                cnx.commit()

                #update address
                cursor = cnx.cursor()
                query = ("UPDATE address "
                        "SET city_id = %s "
                        "WHERE address_id = %s ") 
                cursor.execute(query, (city_id, addr_id))
                cnx.commit()

    if received_data["country"] != "":
        cursor = cnx.cursor()
        query = ("SELECT address_id "
                "FROM Customer "
                "WHERE customer_id = %s")
        cursor.execute(query, (int(received_data["customer_id"]),))
        row_headers=[x[0] for x in cursor.description] #this will extract row headers
        myresult = cursor.fetchall()
        json_data=[]
        for result in myresult:
            json_data.append(dict(zip(row_headers,result)))
        addr_id = int(json_data[0]["address_id"])

        cursor = cnx.cursor()
        query = ("SELECT * "
                "FROM address "
                "WHERE address_id = %s ") 
        cursor.execute(query, (addr_id,))
        row_headers=[x[0] for x in cursor.description] #this will extract row headers
        myresult = cursor.fetchall()
        json_data=[]
        for result in myresult:
            json_data.append(dict(zip(row_headers,result)))
        city_id = str(json_data[0]["city_id"])
        
        


        cursor = cnx.cursor()
        query = ("SELECT * "
                "FROM city "
                "WHERE city_id = %s ") 
        cursor.execute(query, (city_id,))
        row_headers=[x[0] for x in cursor.description] #this will extract row headers
        myresult = cursor.fetchall()
        json_data=[]
        for result in myresult:
            json_data.append(dict(zip(row_headers,result)))
        old_country_id = str(json_data[0]["country_id"])
        city = str(json_data[0]["city"])


        cursor = cnx.cursor()
        query = ("SELECT country_id "
                "FROM country "
                "WHERE country = %s ") 
        cursor.execute(query, (received_data["country"],))
        row_headers=[x[0] for x in cursor.description] #this will extract row headers
        myresult = cursor.fetchall()
        
        if myresult == []:
            cursor = cnx.cursor()
            query = ("SELECT MAX(country_id) as country_id "
                    "FROM country;")
            cursor.execute(query)
            row_headers=[x[0] for x in cursor.description] #this will extract row headers
            myresult = cursor.fetchall()
            json_data=[]
            for result in myresult:
                json_data.append(dict(zip(row_headers,result)))
            new_id = str(int(json_data[0]["country_id"]) + 1)

            cursor = cnx.cursor()
            query = ("INSERT INTO country(country_id, country) VALUES (%s, %s);")
            cursor.execute(query, (new_id, received_data["country"].title(),))
            cnx.commit()
            country_id = new_id

            #insert old city with new country
            cursor = cnx.cursor()
            query = ("INSERT INTO city(city_id, city, country_id) VALUES (%s, %s, %s);")
            cursor.execute(query, (city_id, city,old_country_id,))
            cnx.commit()

            #update address
            cursor = cnx.cursor()
            query = ("UPDATE address "
                    "SET city_id = %s "
                    "WHERE address_id = %s ") 
            cursor.execute(query, (city_id, addr_id))
            cnx.commit()
        else:
            json_data=[]
            for result in myresult:
                json_data.append(dict(zip(row_headers,result)))
            country_id = str(json_data[0]["country_id"])

            if old_country_id == country_id:
                cursor = cnx.cursor()
                query = ("SELECT city_id "
                        "FROM city "
                        "WHERE country_id = %s ") 
                cursor.execute(query, (country_id,))
                row_headers=[x[0] for x in cursor.description] #this will extract row headers
                myresult = cursor.fetchall()
                json_data=[]
                for result in myresult:
                    json_data.append(dict(zip(row_headers,result)))
                
                for i in json_data:
                    if i["city"] == city:
                        #update address
                        cursor = cnx.cursor()
                        query = ("UPDATE address "
                                "SET city_id = %s "
                                "WHERE address_id = %s ") 
                        cursor.execute(query, (i['city_id'], addr_id))
            else:
                #insert old city with old country
                cursor = cnx.cursor()
                query = ("INSERT INTO city(city_id, city, country_id) VALUES (%s, %s, %s);")
                cursor.execute(query, (city_id, city, country_id,))
                cnx.commit()
    return ('', 204)
    

@app.route('/rentMovie', methods=["POST"])
def rentMovie():
    print("1")
    
    received_data = request.get_json()
    print(received_data)
    cnx = mysql.connector.connect(user='root', password='password',
                              host='127.0.0.1',
                              database='sakila')
    cursor = cnx.cursor()
    query = ("SELECT store_id "
            "FROM customer " 
            "WHERE customer_id = %s")
    cursor.execute(query, (received_data["customer_id"],))
    print(f"received data: {received_data}")
    row_headers=[x[0] for x in cursor.description] #this will extract row headers
    myresult = cursor.fetchall()
    json_data=[]
    for result in myresult:
        json_data.append(dict(zip(row_headers,result)))
    print(json_data[0]["store_id"])
    
    store_id = json_data[0]["store_id"]

    cursor = cnx.cursor()
    query = ("SELECT film_id "
            "FROM film " 
            "WHERE title = %s")
    cursor.execute(query, (received_data["title"],))
    row_headers=[x[0] for x in cursor.description] #this will extract row headers
    myresult = cursor.fetchall()
    json_data=[]
    for result in myresult:
        json_data.append(dict(zip(row_headers,result)))
    print(json_data[0]["film_id"])

    film_id = json_data[0]["film_id"]
    
    cursor = cnx.cursor()
    query = ("SELECT inventory_id "
            "FROM inventory " 
            "WHERE film_id = %s AND store_id = %s")
    cursor.execute(query, (film_id, store_id,))
    row_headers=[x[0] for x in cursor.description] #this will extract row headers
    myresult = cursor.fetchall()
    if myresult == ():
        return ('', 404)
    else:
        json_data=[]
        for result in myresult:
            json_data.append(dict(zip(row_headers,result)))
    
    cursor = cnx.cursor()
    query = ("SELECT inv.inventory_id "
            "FROM (SELECT inventory_id "
                "FROM inventory "
                "WHERE film_id = %s AND store_id = %s) as inv "
            "WHERE inv.inventory_id NOT IN (SELECT inventory_id "
                                        "FROM rental "
                                        "WHERE return_date IS NULL)")
    cursor.execute(query, (film_id, store_id,))
    row_headers=[x[0] for x in cursor.description] #this will extract row headers
    myresult = cursor.fetchall()
    if myresult == ():
        return ('', 404)
    else:
        json_data=[]
        for result in myresult:
            json_data.append(dict(zip(row_headers,result)))
    
    rentMov = json_data[0]["inventory_id"]

    cursor = cnx.cursor()
    query = ("SELECT MAX(rental_id) as rental_id "
            "FROM rental")
    cursor.execute(query)
    row_headers=[x[0] for x in cursor.description] #this will extract row headers
    myresult = cursor.fetchall()
    json_data=[]
    for result in myresult:
        json_data.append(dict(zip(row_headers,result)))

    new_id = str(int(json_data[0]["rental_id"]) + 1)

    cursor = cnx.cursor()
    query = ("INSERT INTO rental(rental_id, inventory_id, customer_id, return_date, staff_id) "
            "VALUES (%s, %s, %s, NULL, %s)")
    cursor.execute(query, (new_id, rentMov, received_data["customer_id"], store_id,))
    cnx.commit()

    return ('', 204)

@app.route('/deleteUser', methods=["POST"])
def deleteUser():
    print("1")
    
    received_data = request.get_json()
    print(received_data)
    cnx = mysql.connector.connect(user='root', password='password',
                              host='127.0.0.1',
                              database='sakila')
    cursor = cnx.cursor()
    query = ("SELECT address_id "
            "FROM customer " 
            "WHERE customer_id = %s")
    cursor.execute(query, (received_data["customer_id"],))
    print(f"received data: {received_data}")
    row_headers=[x[0] for x in cursor.description] #this will extract row headers
    myresult = cursor.fetchall()
    json_data=[]
    for result in myresult:
        json_data.append(dict(zip(row_headers,result)))
    print(json_data)
    addr_id = json_data[0]["address_id"]

    cursor = cnx.cursor()
    query = ("DELETE FROM payment "
             "WHERE customer_id = %s;")
    cursor.execute(query, (received_data["customer_id"],))
    cnx.commit()

    cursor = cnx.cursor()
    query = ("DELETE FROM rental "
             "WHERE customer_id = %s;")
    cursor.execute(query, (received_data["customer_id"],))
    cnx.commit()

    cursor = cnx.cursor()
    query = ("DELETE FROM customer "
             "WHERE customer_id = %s;")
    cursor.execute(query, (received_data["customer_id"],))
    cnx.commit()

    cursor = cnx.cursor()
    query = ("DELETE FROM address "
             "WHERE address_id = %s;")
    cursor.execute(query, (addr_id,))
    cnx.commit()

    return ('', 204)


class FPDF(FPDF):
    def header(self):
        if self.page_no() != 1:
            self.set_font('Courier', '', 12)
            page_width = self.w - 2 * self.l_margin
            col_width = page_width/4
            th = self.font_size
            self.cell(col_width/2+5, th, "Rental ID", border=1)
            self.cell(col_width+10, th, "Rental Date", border=1)
            self.cell(col_width, th, "Inventory ID", border=1)
            self.cell(col_width, th, "Customer ID", border=1)
            self.ln(th)
    
    def footer(self):
        self.set_y(-15)
        pageNum=self.page_no()
        self.set_font('Times','',12.0) 
        self.cell(0, 10, str(pageNum), align="C")
    
@app.route('/getMax', methods=["GET"])
def getMax():
    cnx = mysql.connector.connect(user='root', password='password',
                              host='127.0.0.1',
                              database='sakila')
    cursor = cnx.cursor()
    query = ("SELECT MAX(customer_id) as customer_id "
            "FROM customer;")
    cursor.execute(query)
    row_headers=[x[0] for x in cursor.description] #this will extract row headers
    myresult = cursor.fetchall()
    json_data=[]
    for result in myresult:
        json_data.append(dict(zip(row_headers,result)))
    customer_id = str(int(json_data[0]["customer_id"]))
    return customer_id


# Getting a pdf of all rentals
@app.route('/rentPDF1', methods=["GET"])
def rentPDF1():
    cnx = mysql.connector.connect(user='root', password='password',
                              host='127.0.0.1',
                              database='sakila')
    cursor = cnx.cursor()
    query = ("SELECT * "
            "FROM rental " 
            "WHERE staff_id = 1")
    cursor.execute(query)
    row_headers=[x[0] for x in cursor.description] #this will extract row headers
    myresult = cursor.fetchall()
    json_data=[]
    for result in myresult:
        json_data.append(dict(zip(row_headers,result)))

    pdf = FPDF()
    pdf.add_page()
    page_width = pdf.w - 2 * pdf.l_margin
         
    pdf.set_font('Times','B',14.0) 
    pdf.cell(page_width, 0.0, 'Store 1 Rentals', align='C')
    pdf.ln(10)

    pdf.set_font('Courier', '', 12)
    text_height = 0.17
        
    col_width = page_width/4
        
    pdf.ln(1)
        
    th = pdf.font_size
    
    pdf.cell(col_width/2+5, th, "Rental ID", border=1)
    pdf.cell(col_width+10, th, "Rental Date", border=1)
    pdf.cell(col_width, th, "Inventory ID", border=1)
    pdf.cell(col_width, th, "Customer ID", border=1)
    pdf.ln(th)

    pageNum=pdf.page_no()

    for row in json_data:
        pdf.cell(col_width/2+5, th, str(row['rental_id']), border=1)
        pdf.cell(col_width+10, th, str(row['rental_date']), border=1)
        pdf.cell(col_width, th, str(row['inventory_id']), border=1)
        pdf.cell(col_width, th, str(row['customer_id']), border=1)
        pdf.ln(th)
        
    pdf.ln(10)
        
    pdf.set_font('Times','',10.0) 
    pdf.cell(page_width, 0.0, '- end of report -', align='C')
        
    return Response(pdf.output(dest='S').encode('latin-1'), mimetype='application/pdf', headers={'Content-Disposition':'attachment;filename=store1_rentals.pdf'})

    
@app.route('/rentPDF2', methods=["GET"])
def rentPDF2():
    cnx = mysql.connector.connect(user='root', password='password',
                              host='127.0.0.1',
                              database='sakila')
    cursor = cnx.cursor()
    query = ("SELECT * "
            "FROM rental " 
            "WHERE staff_id = 2")
    cursor.execute(query)
    row_headers=[x[0] for x in cursor.description] #this will extract row headers
    myresult = cursor.fetchall()
    json_data=[]
    for result in myresult:
        json_data.append(dict(zip(row_headers,result)))

    pdf = FPDF()
    pdf.add_page()
    page_width = pdf.w - 2 * pdf.l_margin
         
    pdf.set_font('Times','B',14.0) 
    pdf.cell(page_width, 0.0, 'Store 2 Rentals', align='C')
    pdf.ln(10)

    pdf.set_font('Courier', '', 12)
    text_height = 0.17
        
    col_width = page_width/4
        
    pdf.ln(1)
        
    th = pdf.font_size
    
    pdf.cell(col_width/2+5, th, "Rental ID", border=1)
    pdf.cell(col_width+10, th, "Rental Date", border=1)
    pdf.cell(col_width, th, "Inventory ID", border=1)
    pdf.cell(col_width, th, "Customer ID", border=1)
    pdf.ln(th)

    pageNum=pdf.page_no()

    for row in json_data:
        pdf.cell(col_width/2+5, th, str(row['rental_id']), border=1)
        pdf.cell(col_width+10, th, str(row['rental_date']), border=1)
        pdf.cell(col_width, th, str(row['inventory_id']), border=1)
        pdf.cell(col_width, th, str(row['customer_id']), border=1)
        pdf.ln(th)
        
    pdf.ln(10)
        
    pdf.set_font('Times','',10.0) 
    pdf.cell(page_width, 0.0, '- end of report -', align='C')
        
    return Response(pdf.output(dest='S').encode('latin-1'), mimetype='application/pdf', headers={'Content-Disposition':'attachment;filename=store2_rentals.pdf'})

    





