import windowFT
import matlab
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

package = windowFT.initialize()

fs = 20

t = np.arange(0, 50, 1/fs)
sig = np.cos(2*np.pi*3*t + 0.75*np.sin(2*np.pi*t/5))
sigMat = sig.tolist()

A = matlab.double([sigMat])
fsMat = matlab.double([fs])
fmaxval = matlab.double([5]) 
fminval = matlab.double([0])

w, l = package.windowFT(A, fsMat, nargout=2)

# freq = np.asarray(frq)
# trans = np.asarray(trns)  

a = np.asarray(w)
gh = np.asarray(l)


pyA = np.asarray(A)

plt.pcolormesh(t, gh, np.abs(a))
plt.title('STFT Magnitude')
plt.ylabel('Frequency [Hz]')
plt.xlabel('Time [sec]')
plt.show()

# plt.plot(gh, np.square(np.abs(a)))
# plt.show()



# plt.plot(gh,abs(a))
# plt.show()
