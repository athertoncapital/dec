from dec.spectral import *
from dec.grid1 import *
import matplotlib.pyplot as plt

N = 5
g = Grid_1D.periodic(N)
R0, _, _, _ = g.reconstruction()

random.seed(seed=1)
y = random.rand(N)

x = linspace(0, 2*pi, 100)
plt.plot(x, R0(y)(x)  , color='k')
plt.scatter(g.verts, y, marker='o', color='k')


n = 2
En = method_in_fourier_space(lambda x: extend(x, n))
g2 = Grid_1D.periodic(N+2*n)
y2 = real( En(y) )
plt.plot(x, R0(y)(x)+1.0, color='k')
plt.scatter(g2.verts, y2+1.0, marker='o', color='k')

#n = 2
#g3 = Grid_1D.periodic(N-2*n)
#y3 = real( Finv(unextend(F(y), n)) )
#scatter(g3.verts, y3, marker='x', color='g')

frame = plt.gca()
frame.axes.get_xaxis().set_visible(False)
frame.axes.get_yaxis().set_visible(False)

plt.show()