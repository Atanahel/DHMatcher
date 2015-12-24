from flask import abort
from flask_restful import Resource, reqparse
from data_manager import DatabaseElement
import numpy as np


metadata_parser = reqparse.RequestParser()
metadata_parser.add_argument('author', type=str, default='', location='json')
metadata_parser.add_argument('title', type=str, default='', location='json')
metadata_parser.add_argument('date', type=str, default='', location='json')
metadata_parser.add_argument('additional_metadata', type=dict, default=dict(), location='json')

image_url_metadata_parser = metadata_parser.copy()
image_url_metadata_parser.add_argument('image_url', type=str, location='json')

data_manager = None


def _get_image_url(args: dict) -> str:
        image_url = args['image_url']
        if not data_manager.has_url(image_url):
            abort(400)
        return image_url


class DatabaseAPI(Resource):

    def post(self):
        args = image_url_metadata_parser.parse_args()
        image_url = args['image_url']
        if data_manager.has_url(image_url):
            abort(400, "image_url already present in the database")
        data_manager.add_element(DatabaseElement(args, np.zeros((1024,), dtype=np.float32)))


def _check_has_image_url(image_url: str) -> str:
        if not data_manager.has_url(image_url):
            abort(400, "image_url not present in the database")


class DatabaseElementAPI(Resource):

    def get(self, image_url: str):
        _check_has_image_url(image_url)
        return data_manager.get_metadata_from_url(image_url)

    def put(self, image_url: str):
        _check_has_image_url(image_url)
        args = metadata_parser.parse_args()
        args['image_url'] = image_url
        data_manager.set_metadata_from_url(args)

    def delete(self, image_url: str):
        _check_has_image_url(image_url)
        data_manager.remove_url(image_url)

