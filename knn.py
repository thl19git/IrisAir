import numpy as np
from sql_app import crud, models, schemas
from typing import List, Tuple
from sklearn.neighbors import KNeighborsClassifier
from sklearn import datasets


def convert_for_knn(db_data: List[schemas.Session]) -> Tuple[np.ndarray, np.ndarray]:
    """
    Takes the extracted data from the database in the from of a list of
    schema.summary and converts it into a numpy array of the correct format for KNN

    :param db_data: data extracted from the database contaning summary information for each session related to a specific user/device (serial_number)

    :return: a tuple of two ndarray's containing features and labels for each session relating to a specific device.
    """
    features = []
    labels = []

    # removing open session:
    db_data.pop(len(db_data) - 1)

    for session in db_data:
        features.append([session.avg_temp, session.avg_humidity])
        if session.feeling == None:
            # If no feeling assuming neutral
            labels.append(5)
        else:
            labels.append(session.feeling)

    return features, labels


def get_label(
    current: List[List[float]],
    features: List[List[float]],
    labels: List[int],
    k: int = 3,
):
    """
    Predicts a label for the current data set given a set of data

    :param current: nested list containing latest temp and humidity values from a specific device

    :param features: list containing previous data samples of temp and humidity

    :param labels: list containing the multi-calass labels for each data sample
    """

    if current == [[]] or features == [[]] or labels == []:
        return 0

    if len(features) < k:
        k = len(features)

    neigh = KNeighborsClassifier(n_neighbors=k)

    neigh.fit(features, labels)
    # TODO: CHECK works with multi class
    prediction = neigh.predict(current)

    label = np.ndarray.tolist(prediction)
    return label[0]
