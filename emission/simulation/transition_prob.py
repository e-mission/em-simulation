import numpy as np
import logging
import pykov as pk

def generate_random_transition_prob(n_labels):
    logging.debug("generating a %dx%d probability matrix" % (n_labels, n_labels))
    transition_probabilities = []
    for ri in range(n_labels):
        rowprob = np.random.dirichlet(np.ones(n_labels), size=1)[0]
        transition_probabilities.append(rowprob.tolist())
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
