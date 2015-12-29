import unittest
import dh_matcher
import requests
from signature_extractor import SignatureExtractorManager
import threading

server_address = 'http://127.0.0.1:5000'


def _block_until_server_on():
    server_on = False
    while not server_on:
        try:
            requests.get(server_address, timeout=1)
            server_on = True
        except requests.ConnectionError:
            print('Waiting for server to be online...')
    print('Server is online!')


class TestDHMatcher(unittest.TestCase):
    def setUp(self):
        SignatureExtractorManager.initialize_signature_extractors()
        self.server_thread = threading.Thread(target=lambda: dh_matcher.app.run())
        self.server_thread.start()
        _block_until_server_on()

    def tearDown(self):
        # Maybe stop the dh_matcher.app
        pass

    def test_scenario1(self):
        element1 = {
          "image_url": "http://www.wga.hu/art/l/leonardo/04/0monalis.jpg",
          "author": "LEONARDO da Vinci",
          "title": "Mona Lisa (La Gioconda)",
          "date": "1503-5",
          "additional_metadata": {
            "WGA_id": 153647,
            "added_by": "Benoit"
          }
        }
        # Adding element
        response = requests.post(server_address+'/database', json=element1)
        self.assertEqual(response.status_code, 200, "Adding an element failed")
        response = requests.post(server_address+'/database', json=element1)
        self.assertEqual(response.status_code, 400, "Trying to add an element that is already in the database")
        # Retrieving element
        response = requests.get(server_address+'/database/'+element1['image_url'])
        self.assertEqual(response.status_code, 200, "Accessing an already added element")
        response = requests.get(server_address+'/database/truc')
        self.assertEqual(response.status_code, 400, "Trying to access an element that is not in the database")

if __name__ == '__main__':
    unittest.main()
