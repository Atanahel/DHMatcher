from flask import abort
from flask_restful import Resource, reqparse
import replica.util
from replica import Config
from index_manager import IndexManager

search_parser = reqparse.RequestParser()
search_parser.add_argument('positive_image_urls', type=list, location='json')
search_parser.add_argument('negative_image_urls', type=list, default=list(), location='json')
search_parser.add_argument('nb_results', type=int, default=30, location='json')


index_manager = IndexManager(period=3)


class SearchAPI(Resource):

    def post(self):
        args = search_parser.parse_args()
        positive_image_urls = args['positive_image_urls']
        negative_image_urls = args['negative_image_urls']
        nb_results = args['nb_results']

        # Transform urls to ids and check that the elements are in the database
        positive_ids, negative_ids = [], []
        for url in positive_image_urls:
            e = replica.util.get_element_from_image_url(url)
            if e is None:
                abort(404, "image_url not in database : {}".format(url))
            positive_ids.append(e['id'])
        for url in negative_image_urls:
            e = replica.util.get_element_from_image_url(url)
            if e is None:
                abort(404, "image_url not in database : {}".format(url))
            negative_ids.append(e['id'])

        # Perform the search
        try:
            search_results = index_manager.search(positive_ids, negative_ids, int(nb_results*1.2))
        except KeyError:
            index_manager.ask_for_index_rebuilding()
            # TODO Give more information about the index rebuilding? Start rebuilding the index now?
            abort(404, "One image is not present in the index, please wait for the index to be rebuilt")
            return

        # Generate the output
        results = []
        iter_results = iter(search_results)
        while len(results) < nb_results:
            try:
                r = next(iter_results)
            except StopIteration:
                break
            # Get the image information
            image_info = replica.util.get_element_from_id(r['id'], Config.IMAGES_COLLECTION)
            # Append the result if the image was found
            if image_info is not None:
                results.append({'image': image_info, 'score': r['score']})

        return {'results': results,
                'query': {'positive': [{'id': uuid, 'image_url': url}
                                       for uuid, url in zip(positive_ids, positive_image_urls)],
                          'negative': [{'id': uuid, 'image_url': url}
                                       for uuid, url in zip(negative_ids, negative_image_urls)]
                          }
                }
