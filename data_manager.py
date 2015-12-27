import numpy as np
from typing import Dict


class DatabaseElement:
    def __init__(self, metadata: dict, signature: np.ndarray):
        assert('image_url' in metadata)
        self.metadata = metadata
        self.signature = signature


class DataManager:
    signature_array = np.empty((0, 1024), dtype=np.float32)
    metadata_array = np.empty((0,), dtype=np.object)
    url_metadata_index = dict()  # type: Dict[str, np.ndarray]

    @classmethod
    def has_url(cls, image_url: str) -> bool:
        return image_url in cls.url_metadata_index

    @classmethod
    def get_metadata_from_url(cls, image_url: str) -> dict:
        assert(cls.has_url(image_url))
        return cls.metadata_array[cls.url_metadata_index[image_url]]

    @classmethod
    def set_metadata_from_url(cls, metadata: dict):
        image_url = metadata['image_url']
        assert(cls.has_url(image_url))
        cls.metadata_array[cls.url_metadata_index[image_url]] = metadata

    @classmethod
    def add_element(cls, element: DatabaseElement):
        cls.signature_array = np.append(cls.signature_array, element.signature.reshape((1, -1)), axis=0)
        cls.metadata_array = np.append(cls.metadata_array, np.array([element.metadata]), axis=0)
        cls.url_metadata_index[element.metadata['image_url']] = cls.metadata_array.shape[0] - 1

    @classmethod
    def remove_url(cls, image_url: str):
        idx = cls.url_metadata_index[image_url]
        del cls.url_metadata_index[image_url]
        cls.signature_array = np.delete(cls.signature_array, idx, axis=0)
        cls.metadata_array = np.delete(cls.metadata_array, idx, axis=0)
        for metadata in cls.metadata_array[idx:].ravel():
            cls.url_metadata_index[metadata['image_url']] -= 1
