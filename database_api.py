from flask import abort
from flask_restful import Resource, reqparse
from data_manager import DatabaseElement, DataManager
import numpy as np
import os.path
from matplotlib.pyplot import imread
import io
from urllib.request import urlopen
from signature_extractor import SignatureExtractorManager
from typing import Dict

metadata_parser = reqparse.RequestParser()
metadata_parser.add_argument('author', type=str, default='', location='json')
metadata_parser.add_argument('title', type=str, default='', location='json')
metadata_parser.add_argument('date', type=str, default='', location='json')
metadata_parser.add_argument('additional_metadata', type=dict, default=dict(), location='json')

image_url_metadata_parser = metadata_parser.copy()
image_url_metadata_parser.add_argument('image_url', type=str, location='json')


def _get_image_url(args: dict) -> str:
        image_url = args['image_url']
        if not DataManager.has_url(image_url):
            abort(400)
        return image_url


def _generate_signatures_from_url(image_url: str) -> Dict[str, np.ndarray]:
    ext = os.path.splitext(image_url)[1]
    im = imread(io.BytesIO(urlopen(image_url).read()), ext)
    if len(im.shape) == 2:
        im = np.repeat(im[:, :, np.newaxis], 3, axis=2)
    return SignatureExtractorManager.compute_signatures(im)


class DatabaseAPI(Resource):

    def post(self):
        args = image_url_metadata_parser.parse_args()
        image_url = args['image_url']
        if DataManager.has_url(image_url):
            abort(400, "image_url already present in the database")
        DataManager.add_element(DatabaseElement(args, _generate_signatures_from_url(image_url)))


def _check_has_image_url(image_url: str) -> str:
        if not DataManager.has_url(image_url):
            abort(404, "image_url not present in the database")


class DatabaseElementAPI(Resource):

    def get(self, image_url: str):
        _check_has_image_url(image_url)
        return DataManager.get_metadata_from_url(image_url)

    def put(self, image_url: str):
        _check_has_image_url(image_url)
        args = metadata_parser.parse_args()
        args['image_url'] = image_url
        DataManager.set_metadata_from_url(args)

    def delete(self, image_url: str):
        _check_has_image_url(image_url)
        DataManager.remove_url(image_url)
