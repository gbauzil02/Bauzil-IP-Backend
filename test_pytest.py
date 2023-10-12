from index import app
import json

#[{'film_id': 103, 'title': 'BUCKET BROTHERHOOD', 'rentals': 34}, {'film_id': 738, 'title': 'ROCKETEER MOTHER', 'rentals': 33}, {'film_id': 331, 'title': 'FORWARD TEMPLE', 'rentals': 32}, {'film_id': 382, 'title': 'GRIT CLOCKWORK', 'rentals': 32}, {'film_id': 489, 'title': 'JUGGLER HARDLY', 'rentals': 32}]
def test_films():
    response = app.test_client().get('/films')

    res = json.loads(response.data.decode('utf-8'))
    assert type(res[0]) is dict

    assert res[0]['film_id'] == 103
    assert res[1]['film_id'] == 738
    assert res[2]['film_id'] == 331
    assert res[3]['film_id'] == 382
    assert res[4]['film_id'] == 489

    assert response.status_code == 200
    assert type(res) is list

#[{'actor_id': 107, 'first_name': 'GINA', 'last_name': 'DEGENERES', 'movies': 42}, {'actor_id': 102, 'first_name': 'WALTER', 'last_name': 'TORN', 'movies': 41}, {'actor_id': 198, 'first_name': 'MARY', 'last_name': 'KEITEL', 'movies': 40}, {'actor_id': 181, 'first_name': 'MATTHEW', 'last_name': 'CARREY', 'movies': 39}, {'actor_id': 23, 'first_name': 'SANDRA', 'last_name': 'KILMER', 'movies': 37}]
def test_actors():
    response = app.test_client().get('/actors')

    res = json.loads(response.data.decode('utf-8'))
    assert type(res[0]) is dict

    assert res[0]['actor_id'] == 107
    assert res[1]['actor_id'] == 102
    assert res[2]['actor_id'] == 198
    assert res[3]['actor_id'] == 181
    assert res[4]['actor_id'] == 23

    assert response.status_code == 200
    assert type(res) is list

#[{'customer_id': 1, 'first_name': 'MARY', 'last_name': 'SMITH'}, {'customer_id': 2, 'first_name': 'PATRICIA', 'last_name': 'JOHNSON'}, {'customer_id': 3, 'first_name': 'LINDA', 'last_name': 'WILLIAMS'}, {'customer_id': 4, 'first_name': 'BARBARA', 'last_name': 'JONES'}, {'customer_id': 5, 'first_name': 'ELIZABETH', 'last_name': 'BROWN'}, {'customer_id': 6, 'first_name': 'JENNIFER', 'last_name': 'DAVIS'}, {'customer_id': 7, 'first_name': 'MARIA', 'last_name': 'MILLER'}, {'customer_id': 8, 'first_name': 'SUSAN', 'last_name': 'WILSON'}, {'customer_id': 9, 'first_name': 'MARGARET', 'last_name': 'MOORE'}, {'customer_id': 10, 'first_name': 'DOROTHY', 'last_name': 'TAYLOR'}]
def test_cust():
    response = app.test_client().get('/getCust')

    res = json.loads(response.data.decode('utf-8'))
    assert type(res[0]) is dict

    assert res[0]['customer_id'] == 1
    assert res[1]['customer_id'] == 2
    assert res[2]['customer_id'] == 3
    assert res[3]['customer_id'] == 4
    assert res[4]['customer_id'] == 5
    assert res[5]['customer_id'] == 6
    assert res[6]['customer_id'] == 7
    assert res[7]['customer_id'] == 8
    assert res[8]['customer_id'] == 9
    assert res[9]['customer_id'] == 10

    assert response.status_code == 200
    assert type(res) is list

#[{'customer_id': 28, 'first_name': 'CYNTHIA', 'last_name': 'YOUNG'}]
def test_byId():
    data = {
        "data": 28
    }
    response = app.test_client().post('/custById', json=data)
    
    res = json.loads(response.data.decode('utf-8'))

    assert res[0]['customer_id'] == 28
    assert response.status_code == 201

# [{'film_id': 2, 'title': 'ACE GOLDFINGER', 'description': 'A Astounding Epistle of a Database Administrator And a Explorer who must Find a Car in Ancient China', 'release_year': 2006, 'rental_duration': 3, 'rental_rate': Decimal('4.99'), 'length': 48, 'rating': 'G', 'special_features': {'Trailers', 'Deleted Scenes'}, 'genre': 'Horror'}]
def test_getName():
    data = {
        "data": "ace goldfinger"
    }
    response = app.test_client().post('/getName', json=data)
    
    res = json.loads(response.data.decode('utf-8'))

    assert res[0]['film_id'] == 2
    assert response.status_code == 201

def test_genre():
    data = {
        "data": "horror"
    }
    response = app.test_client().post('/genre', json=data)
    
    res = json.loads(response.data.decode('utf-8'))

    for i in res:
        assert i['genre'] == 'Horror'
    assert response.status_code == 201

def test_actor():
    data = {
        "data": "walter torn"
    }
    response = app.test_client().post('/byActor', json=data)
    
    res = json.loads(response.data.decode('utf-8'))

    assert res[0]['title'] == 'AMELIE HELLFIGHTERS'


    assert response.status_code == 201

def test_getId():
    data = {
        "data": "10"
    }
    response = app.test_client().post('/getId', json=data)
    
    res = json.loads(response.data.decode('utf-8'))

    assert res[0]['customer_id'] == 10


    assert response.status_code == 201


def test_custByFirst():
    data = {
        "data": "Mary"
    }
    response = app.test_client().post('/custByFirst', json=data)
    
    res = json.loads(response.data.decode('utf-8'))

    assert res[0]['first_name'] == 'MARY'


    assert response.status_code == 201

def test_custByLast():
    data = {
        "data": "Johnson"
    }
    response = app.test_client().post('/custByLast', json=data)
    
    res = json.loads(response.data.decode('utf-8'))

    assert res[0]['last_name'] == 'JOHNSON'


    assert response.status_code == 201

def test_addCust():
    data = {
        "store": "1",
        "first": "Jane",
        "last": "Doe",
        "phone": "1234567890",
        "email": "newemail@gmail.com",
        "address": "1 New Street",
        "district": "New District",
        "city": "New City",
        "country": "New Country",
        "postal": "23456"
        
    }
    response = app.test_client().post('/addCust', json=data)


    assert response.status_code == 204

def test_editCust():
    data = {
        "customer_id": "600",
        "store": "",
        "first": "",
        "last": "C",
        "phone": "1234567891",
        "email": "newemail2@gmail.com",
        "address": "",
        "district": "",
        "city": "",
        "country": "",
        "postal": ""
        
    }
    response = app.test_client().post('/editCust', json=data)

    assert response.status_code == 204

def test_rentMovie():
    data = {
        "title": "ACE GOLDFINGER", # <-- film is not available at store 1
        # "title": "ACADEMY DINOSAUR", <-- film is available at store 1
        "customer_id": "600",
        
    }
    response = app.test_client().post('/rentMovie', json=data)

    assert response.status_code == 404 # <-- error code
    #assert response.status_code == 204

def test_deleteUser():
    data = {
        "customer_id": "600",
        
    }
    response = app.test_client().post('/deleteUser', json=data)

    assert response.status_code == 204

def test_rentPDF1():
    response = app.test_client().get('/rentPDF1')

    assert response.status_code == 200

