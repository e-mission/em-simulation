import numpy as np
import logging
import pykov as pk

def generate_random_transition_prob(n_labels):
    logging.debug("generating a %dx%d probability matrix" % (n_labels, n_labels))
    transition_probabilities = []
    for ri in range(n_labels):
        rowprob = np.random.dirichlet(np.ones(n_labels-1), size=1)[0]
        final_rowprob = rowprob.tolist()
        final_rowprob.insert(ri, 0)
        transition_probabilities.append(final_rowprob)
    return transition_probabilities

def get_markov_chain(labels, prob_matrix):
    mc = pk.Chain()
    for rowindex, rowlabel in enumerate(labels):
        for colindex, collabel in enumerate(labels):
            logging.debug("Adding entry (%s, %s) -> %s" %
                (rowlabel, collabel, prob_matrix[rowindex][colindex]))
            mc[rowlabel, collabel] = prob_matrix[rowindex][colindex]
    logging.debug("chain = %s, converting to stochastic" % mc)
    mc.stochastic()
    logging.debug("final chain = %s" % mc)
    return mc

def generate_mode_probs(mode_weight_map):
    """
    The input is a map where the keys are the possible modes for the trip
    and the values are the weights for modes based on the user preferences
    from the tour config
    """
    logging.debug("Generating probabilities for weights %s" % mode_weight_map)
    rowprob = np.random.dirichlet(np.array(list(mode_weight_map.values())), size=1)[0]
    cdf = rowprob.cumsum()
    ret_val = dict(zip(mode_weight_map.keys(), cdf))
    logging.debug("About to return %s" % ret_val)
    return ret_val

def generate_random_mode_from_cdf(mode_cdf_map):
    cdf = list(mode_cdf_map.values())
    sel_index = _invert_cdf(cdf)
    assert sel_index is not None, "CDF inversion should always generate some value"
    return list(mode_cdf_map.keys())[sel_index]

def _invert_cdf(cdf):
    cdf = [0] + cdf
    cdf_ranges = zip(cdf, cdf[1:])
    uniform_rv = np.random.uniform()
    for i, r in enumerate(cdf_ranges):
        # print("About to compare %s with range (%s, %s)" %
        #     (uniform_rv, r[0], r[1]))
        if r[0] <= uniform_rv and uniform_rv <= r[1]:
            return i
