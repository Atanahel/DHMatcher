from typing import Union, List, Callable, Tuple, Dict
import theano
import numpy as np


class SignatureExtractor:
    def __init__(self, preprocessing_function: Callable[np.ndarray],
                 computing_function: Callable,
                 signature_names: Union[str, List[str]]):
        self.preprocessing_function = preprocessing_function
        self.computing_function = computing_function
        if isinstance(signature_names, str):
            self.signature_names = [signature_names]
        else:
            self.signature_names = signature_names

    def compute_signatures(self, image: np.ndarray) -> List[Tuple[str, np.ndarray]]:
        image_preprocessed = self.preprocessing_function(image)
        outputs = self.computing_function(image_preprocessed)
        signatures_result = list()
        if len(self.signature_names) == 1:
            signatures_result.append((self.signature_names[0], outputs))
        else:
            for signature_name, output in zip(self.signature_names, outputs):
                signatures_result.append((signature_name, output))
        return signatures_result


class SignatureExtractorManager:
    _current_signature_extractor_manager = None

    def __init__(self):
        self.signature_extractor_list = list()  # type: List[SignatureExtractor]

    def compute_signatures(self, image: np.ndarray) -> Dict[str, np.ndarray]:
        signatures_result = dict()
        for signature_extractor in self.signature_extractor_list:
            signatures_tmp = signature_extractor.compute_signatures(image)
            for (signature_name, signature) in signatures_tmp:
                signatures_result[signature_name] = signature
        return signatures_result

    def get_all_signature_names(self) -> List[str]:
        return [name
                for signature_extractor in self.signature_extractor_list
                for name in signature_extractor.signature_names]

    def add_signature_extractor(self, signature_extractor: SignatureExtractor):
        # Check that the signature name does not already exists
        assert(len(set(self.get_all_signature_names()).intersection(signature_extractor.signature_names)) == 0)
        self.signature_extractor_list.append(signature_extractor)

    @classmethod
    def get_current(cls):
        return cls._current_signature_extractor_manager
