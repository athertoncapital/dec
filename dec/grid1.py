import numpy as np
import dec.helper
import dec.periodic
import dec.chebyshev
import dec.regular
import itertools
import dec.symbolic
import dec.spectral

Π = lambda *x: tuple(itertools.product(*x))

class Grid_1D(object):
    '''
    >>> g = Grid_1D.periodic(3)
    >>> g.n
    3
    >>> import dec.spectral as sp
    >>> sp.to_matrix(g.dec.D[0, True], g.N[0, True])
    array([[-1.,  1.,  0.],
           [ 0., -1.,  1.],
           [ 1.,  0., -1.]])
    >>> sp.to_matrix(g.dec.D[0, False], g.N[0, False])
    array([[ 1.,  0., -1.],
           [-1.,  1.,  0.],
           [ 0., -1.,  1.]])
    '''
    
    periodic = classmethod(dec.periodic.make)
    regular = classmethod(dec.regular.make)
    chebyshev = classmethod(dec.chebyshev.make)

    def __init__(self, n, xmin, xmax, delta, N, simp, dec, refine):
        self.dimension = 1
        self.n = n
        self.xmin = xmin
        self.xmax = xmax
        self.delta = delta
        self.N = N
        self.simp = simp
        self.dec = dec
        self.refine = refine
        
    def __repr__(self):
        return 'Grid_1D{}'.format((self.n, self.xmin, self.xmax))
    
    @property
    def verts(self):
        return self.simp[0, True]

    @property
    def edges(self):
        return self.simp[1, True]

    @property
    def verts_dual(self):
        return self.simp[0, False]
    
    @property
    def edges_dual(self):
        return self.simp[1, False]

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
        P = self.dec.P
        P0  = P[0, True]
        P1  = P[1, True]
        P0d = P[0, False]
        P1d = P[1, False]
        return P0, P1, P0d, P1d

    def basis_fn(self):
        B0  = [lambda x, i=i:  self.dec.B[0, True ](i, x) for i in range(self.N[0, True])]
        B1  = [lambda x, i=i:  self.dec.B[1, True ](i, x) for i in range(self.N[1, True])]
        B0d = [lambda x, i=i:  self.dec.B[0, False](i, x) for i in range(self.N[0, False])]
        B1d = [lambda x, i=i:  self.dec.B[1, False](i, x) for i in range(self.N[1, False])]
        return B0, B1, B0d, B1d

    def reconstruction(self):
        R0, R1, R0d, R1d = dec.spectral.reconstruction(self.basis_fn())
        return R0, R1, R0d, R1d

    def derivative(self):
        D = self.dec.D
        D0  = D[0, True]
        D0d = D[0, False]
        return D0, D0d
    
    def hodge_star(self):
        H = self.dec.H
        H0  = H[0, True]
        H1  = H[1, True]
        H0d = H[0, False]
        H1d = H[1, False]
        return H0, H1, H0d, H1d
    
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
      
    