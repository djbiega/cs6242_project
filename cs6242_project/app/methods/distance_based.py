"""
distance based recommendation system
"""
from scipy.spatial.distance import cdist


def distance_based_recommendation(database=None, user_request=None):
    """
    :param database or clusters of database to get recommendations from
    :param user_request: scaled 2D array of requested feature
    :return: list of tuples with recommended track ids and their scores
    """
    TOP_K = 20
    X = database.values
    # use intersection of unweighted methods when neither method not weights are input
    l1_norm = database.copy()
    l2_norm = database.copy()
    mahalanobis = database.copy()
    cosine = database.copy()

    l1_norm.loc[:, "distance"] = cdist(X, user_request, 'minkowski', p=1)
    l2_norm.loc[:, "distance"] = cdist(X, user_request, 'minkowski', p=2)
    mahalanobis.loc[:, "distance"] = cdist(X, user_request, 'mahalanobis')
    cosine.loc[:, "distance"] = cdist(X, user_request, 'cosine')

    l1_norm_sorted_idx = l1_norm.sort_values("distance").index.to_list()
    l2_norm_sorted_idx = l2_norm.sort_values("distance").index.to_list()
    mahalanobis_sorted_idx = mahalanobis.sort_values("distance").index.to_list()
    cosine_sorted_idx = cosine.sort_values("distance").index.to_list()
    # select common recommendations based on "minkowski_p1" method
    KEY = l1_norm_sorted_idx.index
    # used as reference for similarity score
    l1_norm.loc[:, "score"] = 1 - (l1_norm.distance - l1_norm.distance.min()) / (l1_norm.distance.max() -
                                                                                 l1_norm.distance.min())
    idx = 0
    common_rec_track_id = []
    while len(common_rec_track_id) < TOP_K:
        idx += 1
        common_rec_track_id = sorted(set(l1_norm_sorted_idx[1:idx + TOP_K]) &
                                     set(l2_norm_sorted_idx[1:idx + TOP_K]) &
                                     set(mahalanobis_sorted_idx[1:idx + TOP_K]) &
                                     set(cosine_sorted_idx[1:idx + TOP_K]), key=KEY)
    return list(zip(common_rec_track_id, l1_norm.loc[common_rec_track_id]["score"]))
