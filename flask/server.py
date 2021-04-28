#!/usr/bin/env python
import os
import json

import flask
from bson import ObjectId
from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_cors import CORS, cross_origin
from urllib3 import HTTPResponse


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

app = Flask(__name__)

client = MongoClient("mongodb://admin:password@mongodb:27017")
personedb = client["persone"]
personecol = personedb["persone"]

@app.route('/see_all')
@cross_origin()
def see_all():
    lista_persone = []
    for x in personecol.find({}):
        lista_persone.append(x)
    return JSONEncoder().encode(lista_persone)


@app.route('/search/nome', methods=['GET'])
@cross_origin()
def cerca_pern_nome():
    Query = str(request.args['Query'])
    persons = personecol.find({"cognome": {"$regex": Query, "$options": 'i'}} )
    risposta = []
    for person in persons:
        risposta.append(person)

    return JSONEncoder().encode(risposta)

@app.route('/search/area', methods=['GET'])
@cross_origin()
def cerca_per_area():
    Query = str(request.args['Query'])
    persons = personecol.find({"area": {"$regex": Query, "$options": 'i'}} )
    risposta = []
    for person in persons:
        risposta.append(person)

    return JSONEncoder().encode(risposta)

@app.route('/', methods=['POST', 'GET'])
@cross_origin()
def pagina_iniziale_e_inserimento():
    if request.method == 'POST':
        nome = request.form['nome']
        cognome = request.form['cognome']
        area = request.form['area']
        try:
            personecol.insert_one({'nome' : nome, 'cognome' : cognome, 'area' : area})
            return json.dumps({'status': 'success'}), 200
        except:
            return json.dumps({'status': 'failure'}), 420
    elif request.method == 'GET':
        try:
            client.admin.command('ismaster')
        except:
                return "Server not available"
        return "Hello from the MongoDB client!\n"

@app.route('/search/id', methods=['GET'])
@cross_origin()
def cerca_per_id():
    Query = str(request.args['Query'])
    risposta = []
    try:
        persona = personecol.find_one({ '_id': ObjectId(Query)})
        risposta.append(persona)
    except:
        pass
    return JSONEncoder().encode(risposta)

@app.route('/update', methods=['POST'])
@cross_origin()
def update():
    nome = request.form['nome']
    cognome = request.form['cognome']
    area = request.form['area']
    _id = request.form['id']
    try:
        personecol.update_one({'_id' : _id}, {'nome' : nome, 'cognome' : cognome, 'area' : area})
        return json.dumps({'status': 'success'}), 200
    except:
        return json.dumps({'status': 'failure'}), 420



@app.route('/<string:id>', methods=['PUT', 'DELETE'])
@cross_origin()
def put_and_delete(id):
    if request.method == 'PUT':
        nome = request.form['nome']
        cognome = request.form['cognome']
        area = request.form['area']
        try:
            personecol.update_one({ '_id': ObjectId(id)}, {'$set': {'nome' : nome, 'cognome' : cognome, 'area' : area}})
            return json.dumps({'status': 'success'}), 200
        except:
            return json.dumps({'status': 'failure'}), 420
    elif request.method == 'DELETE':
        try:
            personecol.delete_one({ '_id': ObjectId(id)})
            return json.dumps({'status': 'success'}), 200
        except:
            return json.dumps({'status': 'failure'}), 420



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.environ.get("FLASK_SERVER_PORT", 80), debug=True)
