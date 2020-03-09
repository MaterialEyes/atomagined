import numpy as np
import numpy.matlib as nm
from itertools import product
from skimage.filters import gaussian

def addSTEMnoise(image,sigma_blur,counts_per_pixel,scanline_horizontal,background_value):
    """Add noise to a pristine simulation that emulates
    real noise from STEM imaging. Adapted from code written 
    by Colin Ophus in MATLAB
    """

    scanline_origin_sigma = [0.0,scanline_horizontal]
    dark_noise_sigma = 0.0

    image = image.astype(np.float64)

    # Normalize the image
    image_scale = image / np.mean(image)
    image_scale = image_scale + background_value
    image_scale = image_scale / np.mean(image_scale)

    # Apply Gaussian filter
    image_scale = gaussian(image_scale,sigma=sigma_blur)
    image_scale = image_scale / np.mean(image_scale)

    # Resample scanlines using bilinear interpolation, random shifts
    image_size = np.shape(image)
    xyOr = np.vstack([range(1,image_size[0]+1),np.ones(image_size[0])]).T

    xyOr[:,0] = xyOr[:,0] + (np.random.randn(image_size[0]) * scanline_origin_sigma[0])
    xyOr[:,1] = xyOr[:,1] + (np.random.randn(image_size[1]) * scanline_origin_sigma[1])

    xAdd, xa = np.meshgrid(np.zeros(image_size[0]), xyOr[:,0])
    x = (xa+xAdd).flatten('F')

    yAdd, ya = np.meshgrid(range(image_size[1]), xyOr[:,1])
    y = (ya+yAdd).flatten('F')

    xF = np.floor(x)
    yF = np.floor(y)

    dx = x - xF
    dy = y - yF

    xb = np.array([xF,xF+1,xF,xF+1]).flatten()
    yb = np.array([yF,yF,yF+1,yF+1]).flatten()

    xb = np.minimum(np.maximum(xb,1),image_size[0])
    yb = np.minimum(np.maximum(yb,1),image_size[1])

    xb = np.mod(xb-1,image_size[0])+1
    yb = np.mod(yb-1,image_size[0])+1

    weights = np.array([(1-dx)*(1-dy),dx*(1-dy),(1-dx)*dy,dx*dy]).flatten()

    subs = np.vstack([xb,yb]).T.astype(np.int)
    vals = nm.repmat(image_scale.flatten('F'),4,1).flatten()*weights

    image_resample = accum(subs, vals)[1::,1::]

    image_noise = np.random.poisson(np.maximum(image_resample,0)*counts_per_pixel)/float(counts_per_pixel) \
      + np.random.randn(image_size[0],image_size[1])*dark_noise_sigma

    image_noise = np.maximum(image_noise,0)

    return image_noise



#========================================================================#
# Helper functions:
#========================================================================#

def area(p):
    return p[0]*p[1]

def accum(accmap, a, func=None, size=None, fill_value=0, dtype=None):
    """
    An accumulation function similar to Matlab's `accumarray` function.

    From: https://scipy-cookbook.readthedocs.io/items/AccumarrayLike.html

    Parameters
    ----------
    accmap : ndarray
        This is the "accumulation map".  It maps input (i.e. indices into
        `a`) to their destination in the output array.  The first `a.ndim`
        dimensions of `accmap` must be the same as `a.shape`.  That is,
        `accmap.shape[:a.ndim]` must equal `a.shape`.  For example, if `a`
        has shape (15,4), then `accmap.shape[:2]` must equal (15,4).  In this
        case `accmap[i,j]` gives the index into the output array where
        element (i,j) of `a` is to be accumulated.  If the output is, say,
        a 2D, then `accmap` must have shape (15,4,2).  The value in the
        last dimension give indices into the output array. If the output is
        1D, then the shape of `accmap` can be either (15,4) or (15,4,1) 
    a : ndarray
        The input data to be accumulated.
    func : callable or None
        The accumulation function.  The function will be passed a list
        of values from `a` to be accumulated.
        If None, numpy.sum is assumed.
    size : ndarray or None
        The size of the output array.  If None, the size will be determined
        from `accmap`.
    fill_value : scalar
        The default value for elements of the output array. 
    dtype : numpy data type, or None
        The data type of the output array.  If None, the data type of
        `a` is used.

    Returns
    -------
    out : ndarray
        The accumulated results.

        The shape of `out` is `size` if `size` is given.  Otherwise the
        shape is determined by the (lexicographically) largest indices of
        the output found in `accmap`.


    Examples
    --------
    >>> from numpy import array, prod
    >>> a = array([[1,2,3],[4,-1,6],[-1,8,9]])
    >>> a
    array([[ 1,  2,  3],
           [ 4, -1,  6],
           [-1,  8,  9]])
    >>> # Sum the diagonals.
    >>> accmap = array([[0,1,2],[2,0,1],[1,2,0]])
    >>> s = accum(accmap, a)
    array([9, 7, 15])
    >>> # A 2D output, from sub-arrays with shapes and positions like this:
    >>> # [ (2,2) (2,1)]
    >>> # [ (1,2) (1,1)]
    >>> accmap = array([
            [[0,0],[0,0],[0,1]],
            [[0,0],[0,0],[0,1]],
            [[1,0],[1,0],[1,1]],
        ])
    >>> # Accumulate using a product.
    >>> accum(accmap, a, func=prod, dtype=float)
    array([[ -8.,  18.],
           [ -8.,   9.]])
    >>> # Same accmap, but create an array of lists of values.
    >>> accum(accmap, a, func=lambda x: x, dtype='O')
    array([[[1, 2, 4, -1], [3, 6]],
           [[-1, 8], [9]]], dtype=object)
    """

    # Check for bad arguments and handle the defaults.
    if accmap.shape[:a.ndim] != a.shape:
        raise ValueError("The initial dimensions of accmap must be the same as a.shape")
    if func is None:
        func = np.sum
    if dtype is None:
        dtype = a.dtype
    if accmap.shape == a.shape:
        accmap = np.expand_dims(accmap, -1)
    adims = tuple(range(a.ndim))
    if size is None:
        size = 1 + np.squeeze(np.apply_over_axes(np.max, accmap, axes=adims))
    size = np.atleast_1d(size)

    # Create an array of python lists of values.
    vals = np.empty(size, dtype='O')
    for s in product(*[range(k) for k in size]):
        vals[s] = []
    for s in product(*[range(k) for k in a.shape]):
        indx = tuple(accmap[s])
        val = a[s]
        vals[indx].append(val)

    # Create the output array.
    out = np.empty(size, dtype=dtype)
    for s in product(*[range(k) for k in size]):
        if vals[s] == []:
            out[s] = fill_value
        else:
            out[s] = func(vals[s])

    return out