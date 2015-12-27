import numpy as np
import sklearn.svm as svm


def search_one_class_svm(search_inds, features: np.ndarray) -> np.ndarray:
    training_features = features[search_inds]
    model = svm.OneClassSVM()
    model.fit(training_features)
    scores = model.decision_function(features)
    scores = np.squeeze(scores)
    return scores


def search_svm(search_inds, negative_inds, features: np.ndarray) -> np.ndarray:
    y = np.zeros((len(search_inds)+len(negative_inds)))
    y[range(len(search_inds))] = 1
    training_features = np.vstack((features[search_inds], features[negative_inds]))
    model = svm.SVC(kernel='rbf', C=100)#, class_weight={0: 1*len(search_inds)/float(len(negative_inds)),1: 1})
    model.fit(training_features, y)
    knowledge_model = svm.OneClassSVM()
    knowledge_model.fit(training_features)

    scores = model.decision_function(features)# + knowledge_model.decision_function(features)
    scores = np.squeeze(scores)
    return scores
