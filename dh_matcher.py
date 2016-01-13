from flask import Flask, abort
from flask_restful import Api
import database_api
import search_api

app = Flask(__name__)
api = Api(app)


api.add_resource(database_api.DatabaseAPI, '/database')
api.add_resource(database_api.DatabaseElementAPI, '/database/<path:image_url>')
api.add_resource(search_api.SearchAPI, '/search')

if __name__ == '__main__':
    app.run(debug=True)
