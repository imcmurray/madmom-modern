# encoding: utf-8
# pylint: disable=no-member
# pylint: disable=invalid-name
"""
This module contains neural network activation functions for the ml.nn module.

"""

from __future__ import absolute_import, division, print_function

import numpy as np


def linear(x, out=None):
    """
    Linear function.

    Parameters
    ----------
    x : numpy array
        Input data.
    out : numpy array, optional
        Array to hold the output data.

    Returns
    -------
    numpy array
        Unaltered input data.

    """
    if out is None or x is out:
        return x
    out[:] = x
    return out


def tanh(x, out=None):
    """
    Hyperbolic tangent function.

    Parameters
    ----------
    x : numpy array
        Input data.
    out : numpy array, optional
        Array to hold the output data.

    Returns
    -------
    numpy array
        Hyperbolic tangent of input data.

    """
    # Note: define a wrapper around np.tanh so we just have the dependency on
    #       madmom when pickling objects
    return np.tanh(x, out)


# Use scipy's expit as the sigmoid function (the bug in scipy < 0.14 is
# no longer relevant since this project requires scipy >= 1.14)
# https://github.com/scipy/scipy/issues/3385
from scipy.special import expit as _sigmoid


def sigmoid(x, out=None):
    """
    Logistic sigmoid function.

    Parameters
    ----------
    x : numpy array
        Input data.
    out : numpy array, optional
        Array to hold the output data.

    Returns
    -------
    numpy array
        Logistic sigmoid of input data.

    """
    # Note: define a wrapper around _sigmoid so we just have the dependency on
    #       madmom when pickling objects, not on scipy.special which may
    #       contain the bug mentioned above
    return _sigmoid(x, out)


def relu(x, out=None):
    """
    Rectified linear (unit) transfer function.

    Parameters
    ----------
    x : numpy array
        Input data.
    out : numpy array, optional
        Array to hold the output data.

    Returns
    -------
    numpy array
        Rectified linear of input data.

    """
    return np.maximum(x, 0, out)


def elu(x, out=None):
    """
    Exponential linear (unit) transfer function.

    Parameters
    ----------
    x : numpy array
        Input data.
    out : numpy array, optional
        Array to hold the output data.

    Returns
    -------
    numpy array
        Exponential linear of input data

    References
    ----------
    .. [1] Djork-Arné Clevert, Thomas Unterthiner, Sepp Hochreiter (2015):
       Fast and Accurate Deep Network Learning by Exponential Linear Units
       (ELUs), http://arxiv.org/abs/1511.07289
    """
    if out is None:
        out = x.copy()
    elif out is not x:
        out[:] = x[:]
    m = x < 0
    out[m] = np.exp(x[m]) - 1
    return out


def softmax(x, out=None):
    """
    Softmax transfer function.

    Parameters
    ----------
    x : numpy array
        Input data.
    out : numpy array, optional
        Array to hold the output data.

    Returns
    -------
    numpy array
        Softmax of input data.

    """
    # determine maximum (over classes)
    tmp = np.amax(x, axis=1, keepdims=True)
    # exp of the input minus the max
    if out is None:
        out = np.exp(x - tmp)
    else:
        np.exp(x - tmp, out=out)
    # normalize by the sum (reusing the tmp variable)
    np.sum(out, axis=1, keepdims=True, out=tmp)
    out /= tmp
    return out
