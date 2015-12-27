from flask import Flask, abort
from flask_restful import Api
from data_manager import DataManager
import database_api
import search_api

app = Flask(__name__)
api = Api(app)

# Initialize data manager
DataManager.set_current_data_manager(DataManager())

api.add_resource(database_api.DatabaseAPI, '/database')
api.add_resource(database_api.DatabaseElementAPI, '/database/<path:image_url>')
api.add_resource(search_api.SearchAPI, '/search')

if __name__ == '__main__':
    app.run(debug=True)
