from flask import abort
from flask_restful import Resource, reqparse
from data_manager import DataManager
import numpy as np
from typing import List

search_parser = reqparse.RequestParser()
search_parser.add_argument('positive_image_urls', type=list, location='json')
search_parser.add_argument('negative_image_urls', type=list, default=list(), location='json')
search_parser.add_argument('nb_results', type=int, default=30, location='json')


def _check_urls(urls: List[str]) -> bool:
    for url in urls:
        if not DataManager.get_current_data_manager().has_url(url):
            abort(400, "image_url not present in the database")


class SearchAPI(Resource):

    def post(self):
        args = search_parser.parse_args()
        positive_image_urls = args['positive_image_urls']
        negative_image_urls = args['negative_image_urls']
        nb_results = args['nb_results']
        _check_urls(negative_image_urls + positive_image_urls)
        # TODO perform search
        results = [DataManager.get_current_data_manager().get_metadata_from_url(image_url)
                   for image_url in positive_image_urls]
        return {'results': results}
