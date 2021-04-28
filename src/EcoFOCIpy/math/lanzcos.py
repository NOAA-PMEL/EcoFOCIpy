"""
Lanczos Filter

121 point low pass lanczos filter.  Assumes hourly data

modiefied matlab code from https://gist.github.com/janeshdev/5847127

"""

__all__ = ["low_pass_weights", "spectral_window",
           "spectral_filtering", "lanzcos"]

import numpy as np


def low_pass_weights(window, cutoff):
    """Calculate weights for a low pass Lanczos filter.

    Args:

    window: int
        The length of the filter window.

    cutoff: float
        The cutoff frequency in inverse time steps.

    """
    order = ((window - 1) // 2 ) + 1
    nwts = 2 * order + 1
    w = np.zeros([int(nwts)])
    n = int(nwts) // 2
    w[n] = 2 * cutoff
    k = np.arange(1., n)
    sigma = np.sin(np.pi * k / n) * n / (np.pi * k)
    firstfactor = np.sin(2. * np.pi * cutoff * k) / (np.pi * k)
    w[n-1:0:-1] = firstfactor * sigma
    w[n+1:-1] = firstfactor * sigma
    return w[1:-1]
    

    
def spectral_window(weights, n):
    
    Ff = np.arange(0,1,2./n)
    if (not np.round(Ff[-1],8) == 1.0 ) and ( n % 2 == 0):
        Ff = np.append(Ff, 1.0) #matlab difference in array generation using floats

    window = np.zeros(len(Ff))
    for i in np.arange(1,len(Ff)):
       window[i] = weights[0] + 2. * np.sum(weights[1:-1] * np.cos(np.arange(1,len(weights) - 1. ) * np.pi * Ff[i]))
    
    return (window, Ff)

def spectral_filtering(x, window):
    Nx = len(x)
    Cx = np.fft.fft(x)
    
    Cx = Cx[0: int(np.floor(Nx / 2) +1) ]
        
    CxH = Cx * window
    filt = np.conj(CxH[Nx - len(CxH) :0:-1])
    CxH = np.append(CxH, filt)
    y = np.real(np.fft.ifft(CxH))
    
    
    return(y, Cx)

"""------------------------------------------------------------------------------------"""

def lanzcos(data, dt, Cf=35. ):
    """ Input - data (array-like) to be transformed   
                timestep   
                cuttoff frequency (35 or 2.86)
    
        Output - filtered data (array-like)
        
        Data shoud be hourly and every hour
    """

    


    window_size = 121. * 2.
    weights = low_pass_weights(window_size, 1. / Cf ) #filter coefs
    
    Nf = 1. / (2. * (dt * 24.)) #nyquist frequency
    Cf = Cf / Nf
        
    (window, Ff) = spectral_window(weights[len(weights) // 2:-1], len(data))
    Ff = Ff * Nf

    (y, Cx) = spectral_filtering(data, window)
    
    if len(y) > len(data):
        y = y[:-1]
    return (y)

