from flask import abort
from flask_restful import Resource, reqparse
import replica
import replica.util
import replica.config
import replica.features.features
import requests
from search_api import index_manager

metadata_parser = reqparse.RequestParser()
metadata_parser.add_argument('metadata', type=dict, default=dict(), location='json')

image_url_metadata_parser = metadata_parser.copy()
image_url_metadata_parser.add_argument('image_url', type=str, location='json')


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

        # Creates the document to be inserted
        new_document = {'image_url': image_url,
                        'origin': replica.config.DEFAULT_ORIGIN_WEBAPP,
                        'metadata': args['metadata']}

        # Tries to insert, abort if key already present
        uuid = replica.util.insert_element_to_database(new_document,
                                                       replica.config.IMAGES_COLLECTION)
        if uuid is None:
            abort(400, "Image is already present in the database : {}".format(image_url))

        # Launch the task of the computation of features
        replica.features.features.compute_features_for_img_in_db.delay(uuid)
        index_manager.ask_for_index_rebuilding()
        return {'id': uuid}


class DatabaseElementAPI(Resource):

    def get(self, image_url: str):
        element = replica.util.get_element_from_image_url(image_url)
        if element is None:
            abort(404, "image_url not found : {}".format('image_url'))
        # TODO Return the info about computed features and indexes
        return element

    def put(self, image_url: str):
        args = metadata_parser.parse_args()
        modified = replica.util.update_metadata_from_image_url(image_url, args['metadata'])
        if not modified:
            abort(404, "image_url not found : {}".format('image_url'))

    def delete(self, image_url: str):
        deleted = replica.util.remove_element_from_image_url(image_url)
        if not deleted:
            abort(404, "image_url not found : {}".format('image_url'))
        index_manager.ask_for_index_rebuilding()
