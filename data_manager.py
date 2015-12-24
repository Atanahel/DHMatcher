import numpy as np


class DatabaseElement:
    def __init__(self, metadata: dict, signature: np.ndarray):
        assert('image_url' in metadata)
        self.metadata = metadata
        self.signature = signature


class DataManager:
    def __init__(self):
        self.signature_array = np.empty((0, 1024), dtype=np.float32)
        self.metadata_array = np.empty((0,), dtype=np.object)
        self.url_metadata_index = dict()

        # When necessary
        # self.new_elements = list()
        # self.to_be_removed_url = list()

    def has_url(self, image_url: str) -> bool:
        return image_url in self.url_metadata_index

    def get_metadata_from_url(self, image_url: str) -> dict:
        assert(self.has_url(image_url))
        return self.metadata_array[self.url_metadata_index[image_url]]

    def set_metadata_from_url(self, metadata: dict):
        image_url = metadata['image_url']
        assert(self.has_url(image_url))
        self.metadata_array[self.url_metadata_index[image_url]] = metadata

    def add_element(self, element: DatabaseElement):
        self.signature_array = np.append(self.signature_array, element.signature.reshape((1,-1)), axis=0)
        self.metadata_array = np.append(self.metadata_array, np.array([element.metadata]), axis=0)
        self.url_metadata_index[element.metadata['image_url']] = self.metadata_array.shape[0] - 1

    def remove_url(self, image_url: str):
        idx = self.url_metadata_index[image_url]
        del self.url_metadata_index[image_url]
        self.signature_array = np.delete(self.signature_array, idx, axis=0)
        self.metadata_array = np.delete(self.metadata_array, idx, axis=0)
        for metadata in self.metadata_array[idx:].ravel():
            self.url_metadata_index[metadata['image_url']] -= 1
