from flask import abort
from flask_restful import Resource, reqparse
from data_manager import DatabaseElement, DataManager
import numpy as np
import os.path
from matplotlib.pyplot import imread
import io
from urllib.request import urlopen
from urllib.error import URLError
from signature_extractor import SignatureExtractorManager
from typing import Dict
import replica
import replica.util
import replica.config
import replica.features.features
import requests

metadata_parser = reqparse.RequestParser()
metadata_parser.add_argument('metadata', type=dict, default=dict(), location='json')

image_url_metadata_parser = metadata_parser.copy()
image_url_metadata_parser.add_argument('image_url', type=str, location='json')


def _get_image_url(args: dict) -> str:
        image_url = args['image_url']
        if not DataManager.has_url(image_url):
            abort(400)
        return image_url


def _generate_signatures_from_url(image_url: str) -> Dict[str, np.ndarray]:
    ext = os.path.splitext(image_url)[1]
    try:
        http_response = urlopen(image_url)
    except URLError:
        raise ValueError('image_url unreachable : {} '.format(image_url))
    try:
        im = imread(io.BytesIO(http_response.read()), ext)
    except IOError:
        raise ValueError('Could not decode image : {}'.format(image_url))
    return SignatureExtractorManager.compute_signatures(im)


class DatabaseAPI(Resource):

    def post(self):
        args = image_url_metadata_parser.parse_args()
        image_url = args['image_url']

        # Check that there is actually a valid image there
        is_url_valid = False
        try:
            r = requests.get(image_url, stream=True,
                             headers={'User-agent': 'Mozilla/5.0'})
            is_url_valid = r.headers['Content-Type'].split('/')[0] == "image"
        except:
            pass

        if not is_url_valid:
            abort(400, 'Invalid or unreachable image_url: {}'.format(image_url))

        new_document = {'image_url': image_url,
                        'origin': 'image-matcher',
                        'metadata': args['metadata']}

        uuid = replica.util.insert_element_to_database(new_document,
                                                       replica.config.DEFAULT_IMAGES_COLLECTION,
                                                       replica.config.IMAGES_DB)
        if uuid is None:
            abort(400, "Image is already present in the database : {}".format(image_url))
        replica.features.features.compute_features_for_img_in_db.delay(uuid)


class DatabaseElementAPI(Resource):

    def get(self, image_url: str):
        element = replica.util.get_element_from_image_url(image_url)
        if element is None:
            abort(404, "image_url not found : {}".format('image_url'))
        # TODO Return the info about computed features and indexes
        return DataManager.get_metadata_from_url(image_url)

    def put(self, image_url: str):
        args = metadata_parser.parse_args()
        modified = replica.util.update_metadata_from_image_url(image_url, args['metadata'])
        if not modified:
            abort(404, "image_url not found : {}".format('image_url'))

    def delete(self, image_url: str):
        deleted = replica.util.remove_element_from_image_url(image_url)
        if not deleted:
            abort(404, "image_url not found : {}".format('image_url'))