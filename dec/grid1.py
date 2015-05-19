import numpy as np
import dec.helper
import dec.periodic
import dec.chebyshev
import dec.regular
import itertools
import dec.symbolic
import dec.spectral

Π = lambda *x: tuple(itertools.product(*x))

def projections(grid):

    def P0(f):
        return f(grid.simp[0])
    
    def P1(f):
        return dec.helper.slow_integration(grid.simp[1][0], grid.simp[1][1], f)
        #return dec.helper.split_args(sp.integrate_spectral)(grid.simp[1][0], grid.simp[1][1])
        
    return P0, P1

class Grid_1D(object):
    '''
    >>> g = Grid_1D.periodic(3)
    >>> g.n
    3
    >>> import dec.spectral as sp
    >>> sp.to_matrix(g.dec.D[0], g.N[0])
    array([[-1.,  1.,  0.],
           [ 0., -1.,  1.],
           [ 1.,  0., -1.]])
    >>> sp.to_matrix(g.dual.dec.D[0], g.dual.N[0])
    array([[ 1.,  0., -1.],
           [-1.,  1.,  0.],
           [ 0., -1.,  1.]])
    '''
    
    periodic = classmethod(lambda *args: dec.periodic.make(projections, *args))
    chebyshev = classmethod(lambda *args: dec.chebyshev.make(projections, *args))
    regular = classmethod(lambda *args: dec.regular.make(projections, *args))

    def __init__(self, n, xmin, xmax, delta, N, simp, dec, dual):
        self.dimension = 1
        self.n = n
        self.xmin = xmin
        self.xmax = xmax
        self.delta = delta
        self.N = N
        self.simp = simp
        self.dual = dual
        self.dec = dec
        
    def __repr__(self):
        return 'Grid_1D{}'.format((self.n, self.xmin, self.xmax))
    
    @property
    def verts(self):
        return self.simp[0]

    @property
    def edges(self):
        return self.simp[1]

    @property
    def verts_dual(self):
        return self.dual.simp[0]
    
    @property
    def edges_dual(self):
        return self.dual.simp[1]

    @property
    def points(self):
        vp = self.verts
        vd = self.verts_dual
        p = np.zeros(vp.shape[0]+vd.shape[0])
        p[0::2] = vp
        p[1::2] = vd
        return p

    def boundary_condition(self, f):
        bc = np.zeros((self.n, ))
        bc[ 0] = -f(self.xmin)
        bc[-1] = +f(self.xmax)
        return bc

    def projection(self):
        P0 = self.dec.P[0]
        P1 = self.dec.P[1]
        P0d = self.dual.dec.P[0]
        P1d = self.dual.dec.P[1]
        return P0, P1, P0d, P1d

    def basis_fn(self):
#         B0 = self.dec.B[0]
#         B1 = self.dec.B[1]
#         B0d = self.dual.dec.B[0]
#         B1d = self.dual.dec.B[1]
        B0  = [lambda x, i=i:  self.dec.B[0](i, x) for i in range(self.N[0])]
        B1  = [lambda x, i=i:  self.dec.B[1](i, x) for i in range(self.N[1])]
        B0d = [lambda x, i=i:  self.dual.dec.B[0](i, x) for i in range(self.dual.N[0])]
        B1d = [lambda x, i=i:  self.dual.dec.B[1](i, x) for i in range(self.dual.N[1])]
        return B0, B1, B0d, B1d

    def reconstruction(self):
#         R0 = self.dec.R[0]
#         R1 = self.dec.R[1]
#         R0d = self.dual.dec.R[0]
#         R1d = self.dual.dec.R[1]
        R0, R1, R0d, R1d = dec.spectral.reconstruction(self.basis_fn())
        return R0, R1, R0d, R1d

    def derivative(self):
        D, Dd = self.dec.D, self.dual.dec.D
        return D[0], Dd[0]
    
    def hodge_star(self):
        H, Hd = self.dec.H, self.dual.dec.H
        return H[0], H[1], Hd[0], Hd[1]
    
    def wedge(self):
        T, U = self.refine.T, self.refine.U
        p = Π((0, 1), (True, False))
        
        Ws = dec.symbolic.wedge_1d()
        W = {}    
        
        def get_w(d0, p0, d1, p1, p2):
            def w(a, b):
                a = T[d0, p0](a)
                b = T[d1, p1](b)
                (c,) = Ws[d0, d1]((a,), (b,))
                return U[d0+d1, p2](c)
            return w
    
        for ((d0, p0), (d1, p1), p2) in Π(p, p,(True, False)):
            if d0 + d1 > 1: continue
            if p0==p1==p2 and d0==d1==0:
                #no refinement necessary, just multiply directly
                W[(d0, p0), (d1, p1), p2] = lambda a, b: a*b
                continue
            W[(d0, p0), (d1, p1), p2] = get_w(d0, p0, d1, p1, p2)    
    
        return W
    
    def contraction(self):
        T, U = self.refine.T, self.refine.U        
        p = Π((0, 1), (True, False))
        
        Cs = dec.symbolic.contraction_1d()        
        C = {}
        
        def get_c(p0, d1, p1, p2):
            def c(a, b):
                a = T[1, p0](a)
                b = T[d1, p1](b)
                (c,) = Cs[d1]((a,), (b,))
                return U[d1-1, p2](c)
            return c
    
        for (p0, (d1, p1), p2) in Π((True, False), p, (True, False)):
            if d1-1 < 0: continue
            C[p0, (d1, p1), p2] = get_c(p0, d1, p1, p2)    
    
        return C
      
    