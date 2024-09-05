from flask import Flask, request, Response, jsonify
import os
from http import HTTPStatus
import psycopg2
from datetime import datetime

COUNTRIES_DB = "countries"
COUNTRY_NAME = "country_name"
LAT = "lat"
LON = "lon"
COORD_TYPES = ['float', 'int']
COUNTRY_ID = 'idTara'

app = Flask(__name__)

def init_db():
    conn = psycopg2.connect(
        host=os.environ.get("DB_HOST"),
        database = os.environ.get("DB_NAME"),
        user = os.environ.get("DB_USERNAME"),
        password = os.environ.get("DB_PASSWORD"),
        port = '5432'
    )
    cursor = conn.cursor()

    with open('init_db.sql', 'r') as init_script_db:
        db_create = init_script_db.read()
    
    cursor.execute(db_create)
    conn.commit()
    conn.close()

def getConnection():
    conn = psycopg2.connect(
        host=os.environ.get("DB_HOST"),
        database = os.environ.get("DB_NAME"),
        user = os.environ.get("DB_USERNAME"),
        password = os.environ.get("DB_PASSWORD"),
        port = '5432'
    )
    return conn


#   Countries API    

@app.route('/api/countries', methods=['GET'])
def get_countries():
    conn = getConnection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM COUNTRIES;")
    countries = cursor.fetchall()

    countries_list = []
    if countries:
        for country in countries:
            country_dict = {
                'id': country[0],
                'nume': country[1],
                'lat': country[2],
                'lon': country[3]
            }
            countries_list.append(country_dict)

    conn.close()
    return jsonify(countries_list), HTTPStatus.OK

@app.route('/api/countries', methods=['POST'])
def post_country():
    body = request.get_json()
 
    if not all(field in body for field in ['nume', 'lat', 'lon']) or \
            not (type(body["nume"]) == str and type(body["lat"]) == float and type(body["lon"]) == float):
        return Response(status=HTTPStatus.BAD_REQUEST)
    
    conn = getConnection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO countries (country_name, lat, lon) VALUES (%s, %s, %s);', (body['nume'], body[LAT], body[LON],))
        conn.commit()
    
    except:
        return Response(status=HTTPStatus.CONFLICT)
    
    cursor.execute("SELECT max(id) FROM COUNTRIES;")
    country_id = cursor.fetchone()[0]
    conn.close()
    return jsonify({"id":country_id}), HTTPStatus.CREATED

@app.route('/api/countries/<id>', methods=['PUT'])
def update_country(id):
    body = request.get_json()
    
    if not body or not all(field in body for field in ['id', 'nume', 'lat', 'lon']) or \
        not (type(body["id"]) == int and type(body["nume"]) == str and \
            (type(body['lat']) == int or type(body['lat']) == float) and \
            (type(body['lon']) == int or type(body['lon']) == float)) or \
            int(id) != body["id"]:
        return Response(status=HTTPStatus.BAD_REQUEST)
        
    conn = getConnection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM COUNTRIES WHERE id = %s;", (id, ))
    size = len(cursor.fetchall())

    if size == 0:
        return Response(status=HTTPStatus.NOT_FOUND)

    try:
        cursor.execute('UPDATE countries SET id = %s, country_name = %s, lat = %s, lon = %s WHERE id = %s;', \
            (body['id'], body['nume'], body['lat'], body['lon'], id))
        conn.commit()
        conn.close()
        return Response(status=HTTPStatus.OK)
    except:
        return Response(status=HTTPStatus.CONFLICT)

@app.route('/api/countries/<id>', methods=['DELETE'])
def remove_country(id):
    flag = True
    try:
        int(id)
    except ValueError:
        flag = False

    if not id or flag == False:
        return Response(status=HTTPStatus.BAD_REQUEST)

    conn = getConnection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM COUNTRIES WHERE id = %s;", (id, ))
    size = len(cursor.fetchall())
    
    if size == 0:
        return Response(status=HTTPStatus.NOT_FOUND)

    cursor.execute("DELETE FROM countries WHERE id = %s;", (id,))
    conn.commit()
    conn.close()
    return Response(status=HTTPStatus.OK)


#   Cities API

@app.route('/api/cities', methods=['POST'])
def add_city():
    body = request.get_json()
    
    if not body or \
        not all(field in body for field in ['idTara', 'nume', 'lat', 'lon']) or \
        not (type(body['idTara']) == int and type(body['nume']) == str and \
            (type(body['lat']) == int or type(body['lat']) == float) and \
            (type(body['lon']) == int or type(body['lon']) == float)):
        return Response(status=HTTPStatus.BAD_REQUEST)
    
    conn = getConnection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM COUNTRIES WHERE id = %s;', (body[COUNTRY_ID],))
    size = len(cursor.fetchall())

    if size == 0:
        return Response(status=HTTPStatus.NOT_FOUND)

    try:
        cursor.execute('INSERT INTO cities (country_id, city_name, lat, lon) VALUES (%s, %s, %s, %s)', \
            (body["idTara"], body["nume"], body["lat"], body["lon"], ))
        conn.commit()
    except:
        return Response(status=HTTPStatus.CONFLICT)

    cursor.execute('SELECT max(id) FROM CITIES;')
    city_id = cursor.fetchone()[0]

    return jsonify({"id":city_id}), HTTPStatus.CREATED

@app.route('/api/cities', methods=['GET'])
def get_all_cities():
    conn = getConnection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM cities;')
    cities = cursor.fetchall()

    cities_list = []
    if cities:
        for city in cities:
            city_dict = {
                'id': city[0],
                'idTara': city[1],
                'nume': city[2],
                'lat': city[3],
                'lon': city[4]
            }
            cities_list.append(city_dict)

    conn.close()
    return jsonify(cities_list), HTTPStatus.OK

@app.route('/api/cities/country/<idTara>', methods=['GET'])
def get_city_by_countryID(idTara):
    conn = getConnection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM cities WHERE country_id = %s;', (idTara))
    cities = cursor.fetchall()

    cities_list = []
    if cities:
        for city in cities:
            city_dict = {
                'id': city[0],
                'idTara': city[1],
                'nume': city[2],
                'lat': city[3],
                'lon': city[4]
            }
            cities_list.append(city_dict)

    conn.close()
    return jsonify(cities_list), HTTPStatus.OK

@app.route('/api/cities/<id>', methods=['PUT'])
def update_city(id):
    body = request.get_json()
    
    if not body or not all(field in body for field in ['id', 'idTara', 'nume', 'lat', 'lon']) or \
        not (type(body["id"]) == int and type(body['idTara']) == int and type(body["nume"]) == str and \
            (type(body['lat']) == int or type(body['lat']) == float) and \
            (type(body['lon']) == int or type(body['lon']) == float)) or \
            int(id) != body["id"]:
        return Response(status=HTTPStatus.BAD_REQUEST)
        
    conn = getConnection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM cities WHERE id = %s;", (id, ))
    size = len(cursor.fetchall())

    if size == 0:
        return Response(status=HTTPStatus.NOT_FOUND)

    cursor.execute("SELECT * FROM COUNTRIES WHERE id = %s;", (body["idTara"],))
    size = len(cursor.fetchall())

    if size == 0:
        return Response(status=HTTPStatus.NOT_FOUND)
    
    try:
        cursor.execute('UPDATE cities SET id = %s, country_id = %s, city_name = %s, lat = %s, lon = %s WHERE id = %s;', \
            (body['id'], body['idTara'], body['nume'], body['lat'], body['lon'], id))
        conn.commit()
        conn.close()
        return Response(status=HTTPStatus.OK)
    except:
        return Response(status=HTTPStatus.CONFLICT)

@app.route('/api/cities/<id>', methods=['DELETE'])
def remove_city(id):
    flag = True
    try:
        int(id)
    except ValueError:
        flag = False

    if not id or flag == False:
        return Response(status=HTTPStatus.BAD_REQUEST)

    conn = getConnection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM cities WHERE id = %s;", (id, ))
    size = len(cursor.fetchall())
    
    if size == 0:
        return Response(status=HTTPStatus.NOT_FOUND)

    cursor.execute("DELETE FROM cities WHERE id = %s;", (id,))
    conn.commit()
    conn.close()
    return Response(status=HTTPStatus.OK)

@app.route('/api/temperatures', methods=['POST'])
def add_temperature():
    body = request.get_json()

    if not body or not (all(field in body for field in ['idOras', 'valoare'])) \
        or not (type(body['idOras']) == int and (type(body['valoare']) == float or type(body['valoare']) == int)):
        return Response(status=HTTPStatus.BAD_REQUEST)

    conn = getConnection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM cities where id=%s', (body['idOras'],))
    size = len(cursor.fetchall())
    if size == 0:
        return Response(status=HTTPStatus.NOT_FOUND)

    try:
        cursor.execute('INSERT INTO temperatures (val, city_id) VALUES (%s, %s)', \
            (float(body["valoare"]), float(body["idOras"]), ))
        conn.commit()
    except:
        return Response(status=HTTPStatus.CONFLICT)
    
    cursor.execute('SELECT max(id) FROM temperatures;')
    temp_id = cursor.fetchone()[0]

    return jsonify({"id":temp_id}), HTTPStatus.CREATED

@app.route('/api/temperatures', methods=['GET'])
def get_filter_temperatures():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    start_date = request.args.get('from')
    end_date = request.args.get('until')

    query = "SELECT c.id, t.city_id, t.val, DATE(t.timesstamp), c.lat, c.lon FROM temperatures t join  cities c on c.id = t.city_id  WHERE TRUE"
    params = []

    if lat:
        query += " AND c.lat = %s"
        params.append(float(lat))
    
    if lon:
        query += " AND c.lon = %s"
        params.append(float(lon))

    if start_date:
        query += " AND DATE(t.timesstamp) > %s"
        params.append(datetime.strptime(start_date, '%Y-%m-%d').date())

    if end_date:
        query += " AND DATE(t.timesstamp) < %s"
        params.append(datetime.strptime(end_date, '%Y-%m-%d').date())

    query += ";"

    conn = getConnection()
    cursor = conn.cursor()

    cursor.execute(query, tuple(params))
    filtered_temperatures = cursor.fetchall()

    temperatures_list = []
    if filtered_temperatures:
        for temp in filtered_temperatures:
            temp_dict = {
                'id': temp[1],
                'valoare': temp[2],
                "timestamp": temp[3].strftime("%Y-%m-%d")
            }
            temperatures_list.append(temp_dict)
    conn.close()

    return jsonify(temperatures_list), HTTPStatus.OK

@app.route('/api/temperatures/cities/<city_id>', methods=['GET'])
def get_city_temperatures(city_id):
    flag = True
    try:
        int(city_id)
    except ValueError:
        flag = False

    if not city_id or flag == False:
        return Response(status=HTTPStatus.BAD_REQUEST)
    
    start_date = request.args.get('from')
    end_date = request.args.get('until')

    query = "SELECT t.id, t.val, DATE(t.timesstamp) FROM temperatures t JOIN cities c ON t.city_id = c.id WHERE city_id = %s"
    params = [city_id]

    if start_date:
        query += " AND DATE(t.timesstamp) > %s"
        params.append(datetime.strptime(start_date, '%Y-%m-%d').date())

    if end_date:
        query += " AND DATE(t.timesstamp) < %s"
        params.append(datetime.strptime(end_date, '%Y-%m-%d').date())

    query += ";"

    conn = getConnection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM temperatures t JOIN cities c ON t.city_id = c.id WHERE city_id = %s", (city_id,))
    size = cursor.fetchall()
    if size == 0:
        return Response(status=HTTPStatus.NOT_FOUND)

    cursor.execute(query, tuple(params))
    city_temperatures = cursor.fetchall()

    city_temp_list = []
    if city_temperatures:
        for temp in city_temperatures:
            temp_dict = {
                'id': temp[0],
                'valoare': temp[1],
                "timestamp": temp[2].strftime("%Y-%m-%d")
            }
            city_temp_list.append(temp_dict)

    conn.close()
    return jsonify(city_temp_list), HTTPStatus.OK

@app.route('/api/temperatures/countries/<country_id>', methods=['GET'])
def get_country_temperatures(country_id):
    flag = True
    try:
        int(country_id)
    except ValueError:
        flag = False

    if not country_id or flag == False:
        return Response(status=HTTPStatus.BAD_REQUEST)
    
    start_date = request.args.get('from')
    end_date = request.args.get('until')

    query = "SELECT t.id, t.val, DATE(t.timesstamp) FROM temperatures t JOIN cities c ON t.city_id = c.id WHERE country_id = %s"
    params = [country_id]

    if start_date:
        query += " AND DATE(t.timesstamp) > %s"
        params.append(datetime.strptime(start_date, '%Y-%m-%d').date())

    if end_date:
        query += " AND DATE(t.timesstamp) < %s"
        params.append(datetime.strptime(end_date, '%Y-%m-%d').date())

    query += ";"

    conn = getConnection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM temperatures t JOIN cities c ON t.city_id = c.id WHERE country_id = %s", (country_id,))
    size = cursor.fetchall()
    if size == 0:
        return Response(status=HTTPStatus.NOT_FOUND)
        
    cursor.execute(query, tuple(params))
    country_temperatures = cursor.fetchall()

    country_temp_list = []
    if country_temperatures:
        for temp in country_temperatures:
            temp_dict = {
                'id': temp[0],
                'valoare': temp[1],
                "timestamp": temp[2].strftime("%Y-%m-%d")
            }
            country_temp_list.append(temp_dict)

    conn.close()
    return jsonify(country_temp_list), HTTPStatus.OK

@app.route('/api/temperatures/<id>', methods=['PUT'])
def update_temperature(id):
    body = request.get_json()

    if not body or not all(field in body for field in ['id', 'idOras', 'valoare']) \
        or not (type(body['id']) == int and type(body['idOras']) == int \
            and (type(body['valoare']) == int or type(body['valoare']) == float)) or int(id) != body['id']:
            return Response(status=HTTPStatus.BAD_REQUEST)

    conn = getConnection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM temperatures WHERE id = %s", (id,))
    size = len(cursor.fetchall())

    if size == 0:
        return Response(status=HTTPStatus.NOT_FOUND)

    cursor.execute("SELECT * FROM cities WHERE id = %s", (body['idOras'],))
    size = len(cursor.fetchall())

    if size == 0:
        return Response(status=HTTPStatus.NOT_FOUND)

    try:
        cursor.execute('UPDATE temperatures SET city_id = %s, val = %s WHERE id = %s;', \
            (body['idOras'], float(body['valoare']), id))
        conn.commit()
        conn.close()
        return Response(status=HTTPStatus.OK)
    except:
        return Response(status=HTTPStatus.CONFLICT)

@app.route('/api/temperatures/<id>', methods=['DELETE'])
def remove_temperature(id):
    flag = True
    try:
        int(id)
    except ValueError:
        flag = False

    if not id or flag == False:
        return Response(status=HTTPStatus.BAD_REQUEST)
    
    conn = getConnection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM temperatures WHERE id = %s;", (id,))
    size = len(cursor.fetchall())

    if size == 0:
        return Response(status=HTTPStatus.NOT_FOUND)

    cursor.execute("DELETE FROM temperatures WHERE id = %s;", (id,))
    conn.commit()
    conn.close()

    return Response(status=HTTPStatus.OK)
    
if __name__ == "__main__":
    init_db()
    app.run(host='0.0.0.0', debug=True, port=6000)