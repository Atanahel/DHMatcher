from flask import abort
from flask_restful import Resource, reqparse
from data_manager import DataManager
import numpy as np
from typing import List
import search_algorithms

search_parser = reqparse.RequestParser()
search_parser.add_argument('positive_image_urls', type=list, location='json')
search_parser.add_argument('negative_image_urls', type=list, default=list(), location='json')
search_parser.add_argument('nb_results', type=int, default=30, location='json')


def _check_urls(urls: List[str]) -> bool:
    for url in urls:
        if not DataManager.has_url(url):
            abort(400, "{} not present in the database".format(url))


class SearchAPI(Resource):

    def post(self):
        args = search_parser.parse_args()
        positive_image_urls = args['positive_image_urls']
        negative_image_urls = args['negative_image_urls']
        nb_results = args['nb_results']
        # Check that urls are valid (should be in the database and in the search index)
        _check_urls(negative_image_urls + positive_image_urls)
        # Grab the indices in the signature array
        positive_indices = [DataManager.url_metadata_index[image_url] for image_url in positive_image_urls]
        negative_indices = [DataManager.url_metadata_index[image_url] for image_url in negative_image_urls]
        # Perform the search
        if len(negative_indices) == 0:
            scores = search_algorithms.search_one_class_svm(positive_indices, DataManager.signature_array)
            method = '1-class-svm'
        else:
            scores = search_algorithms.search_svm(positive_indices, negative_indices, DataManager.signature_array)
            method = '2-classes-svm'
        # Generate the ouput
        results_ind = np.argsort(scores)[-1:-nb_results:-1]
        results = list()
        for i in results_ind.ravel():
            url = DataManager.metadata_array[i]['image_url']
            ref = dict()
            ref['metadata'] = DataManager.get_metadata_from_url(url)
            ref['score'] = scores[i]
            results.append(ref)
        return {'results': results,
                'method': method,
                'query': {'positive_image_urls': positive_image_urls,
                          'negative_image_urls': negative_image_urls}
                }
