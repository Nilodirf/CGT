import numpy as np


def finderb(key, array):

    all_keys = np.array(key, ndmin=1)
    all_indices = np.zeros([len(all_keys)], dtype=int)

    for index_nest, key_nest in zip(all_indices, all_keys):
        index_nest = finderb_nest(key_nest, array)

    return all_indices

def finderb_nest(key_nest, array):

    distances = np.abs(array - key_nest)
    indices = np.where(distances == np.amin(distances))
    return indices[0]
