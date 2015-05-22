from dec.symbolic import *
from dec.grid1 import Grid_1D
from dec.forms import decform
from sympy.core.numbers import One

c = Chart(x,)

def compare_comps(g, f, isprimal):
    #TODO: Why aren't the arrays equal to higher tolerance?
    df = f.decform(g, isprimal)
    assert np.allclose(f.lambdify(g.points),
                       g.refine.T[f.degree, df.isprimal](df.array),
                       atol=1e-7)

    assert np.allclose(df.array,
                       g.refine.U[f.degree, df.isprimal](f.lambdify(g.points)),
                       atol=1e-7)

def test_refine():

    g = Grid_1D.periodic(6)
    compare_comps(g, form(0, c, (sin(x),)), True)
    compare_comps(g, form(0, c, (sin(x),)), False)
    compare_comps(g, form(1, c, (sin(x),)), True)
    compare_comps(g, form(1, c, (sin(x),)), False)

    g = Grid_1D.periodic(7)
    for func in (sin(x), cos(x), sin(2*x), sin(x)*cos(x), 1 + sin(x)):
        compare_comps(g, form(0, c, (func,)), True)
        compare_comps(g, form(0, c, (func,)), False)
        compare_comps(g, form(1, c, (func,)), True)
        compare_comps(g, form(1, c, (func,)), False)

    g = Grid_1D.chebyshev(6)
    for func in (x, (1-x)**2, x**3, x+1):
        compare_comps(g, form(0, c, (func,)), True)
        compare_comps(g, form(0, c, (func,)), False)
        compare_comps(g, form(1, c, (func,)), True)
        compare_comps(g, form(1, c, (func,)), False)

    g = Grid_1D.chebyshev(7)
    for func in (x, (1-x)**2, x**3, x+1):
        compare_comps(g, form(0, c, (func,)), True)
        compare_comps(g, form(0, c, (func,)), False)
        compare_comps(g, form(1, c, (func,)), True)
        compare_comps(g, form(1, c, (func,)), False)

def test_P():

    g = Grid_1D.periodic(11)
    
    f = form(0, c, (sin(x),))
    assert f.decform(g, True) == g.P(f.degree, True, f.lambdify)
    assert f.decform(g, False) == g.P(f.degree, False, f.lambdify)
    
    f = form(1, c, (cos(x),))
    assert f.decform(g, True) == g.P(f.degree, True, f.lambdify)
    assert f.decform(g, False) == g.P(f.degree, False, f.lambdify)

    g = Grid_1D.regular(11)
    
    f = form(0, c, (x,))
    assert f.decform(g, True) == g.P(f.degree, True, f.lambdify)
    assert f.decform(g, False) == g.P(f.degree, False, f.lambdify)
    
    f = form(1, c, (x**3,))
    assert f.decform(g, True) == g.P(f.degree, True, f.lambdify)
    assert f.decform(g, False) == g.P(f.degree, False, f.lambdify)

    g = Grid_1D.chebyshev(11)
    
    f = form(0, c, (x,))
    assert f.decform(g, True) == g.P(f.degree, True, f.lambdify)
    assert f.decform(g, False) == g.P(f.degree, False, f.lambdify)
    
    f = form(1, c, (x**3,))
    assert f.decform(g, True) == g.P(f.degree, True, f.lambdify)
    assert f.decform(g, False) == g.P(f.degree, False, f.lambdify)

def test_R():

    g = Grid_1D.periodic(11)
    pnts = np.linspace(g.xmin, g.xmax, 50)
    
    f = form(0, c, (sin(x),))
    assert np.allclose(f.lambdify(pnts), f.decform(g, True).R(pnts))
    assert np.allclose(f.lambdify(pnts), f.decform(g, False).R(pnts))

    f = form(1, c, (sin(x),))
    assert np.allclose(f.lambdify(pnts), f.decform(g, True).R(pnts))
    assert np.allclose(f.lambdify(pnts), f.decform(g, False).R(pnts))

    g = Grid_1D.chebyshev(11)
    # do not include boundaries, because we get nan there
    pnts = np.linspace(g.xmin, g.xmax, 50)[1:-1] 
    
    f = form(0, c, (x**2,))
    assert np.allclose(f.lambdify(pnts), f.decform(g, True).R(pnts))
    assert np.allclose(f.lambdify(pnts), f.decform(g, False).R(pnts))

    f = form(1, c, (x**2,))
    assert np.allclose(f.lambdify(pnts), f.decform(g, True).R(pnts))
    assert np.allclose(f.lambdify(pnts), f.decform(g, False).R(pnts))

def test_D():
    
    g = Grid_1D.periodic(11)
    f = form(0, c, (cos(x),))    
    assert f.D.decform(g, True) == f.decform(g, True).D
    assert f.D.decform(g, False) == f.decform(g, False).D

    g = Grid_1D.regular(11)
    f = form(0, c, (x,))
    assert f.D.decform(g, True) == f.decform(g, True).D
    bc = g.boundary_condition(f.lambdify)
    assert f.D.decform(g, False) == f.decform(g, False).D + bc
    f = form(0, c, (x**3,))
    assert f.D.decform(g, True) == f.decform(g, True).D
    bc = g.boundary_condition(f.lambdify)
    assert f.D.decform(g, False) == f.decform(g, False).D + bc

    g = Grid_1D.chebyshev(11)
    f = form(0, c, (x,))
    assert f.D.decform(g, True) == f.decform(g, True).D
    bc = g.boundary_condition(f.lambdify)
    assert f.D.decform(g, False) == f.decform(g, False).D + bc
    f = form(0, c, (x**3,))
    assert f.D.decform(g, True) == f.decform(g, True).D
    bc = g.boundary_condition(f.lambdify)
    assert f.D.decform(g, False) == f.decform(g, False).D + bc
    
def test_H():

    g = Grid_1D.periodic(11)
    f = form(0, c, (cos(3*x),))    
    assert f.H.decform(g, False) == f.decform(g, True).H
    assert f.H.decform(g, True) == f.decform(g, False).H
    f = form(1, c, (sin(x)+cos(x),))    
    assert f.H.decform(g, False) == f.decform(g, True).H
    assert f.H.decform(g, True) == f.decform(g, False).H

    g = Grid_1D.chebyshev(11)
    f = form(0, c, (x**4,))    
    assert f.H.decform(g, False) == f.decform(g, True).H
    assert f.H.decform(g, True) == f.decform(g, False).H
    f = form(1, c, (x**2 + 1,))    
    assert f.H.decform(g, False) == f.decform(g, True).H
    assert f.H.decform(g, True) == f.decform(g, False).H

def test_W_C():

    g = Grid_1D.periodic(11)
    
    f0 = form(0, c, (cos(x),))
    f1 = form(1, c, (sin(x),))

    assert (f0^f0).decform(g, True) == f0.decform(g, True).W(f0.decform(g, True))
    assert (f0^f1).decform(g, True) == f0.decform(g, True).W(f1.decform(g, True))
    assert (f0^f1).decform(g, False) == f0.decform(g, True).W(f1.decform(g, True), toprimal=False)
    assert (f0^f1).decform(g, False) == f0.decform(g, False).W(f1.decform(g, False), toprimal=False)
    #assert (f0^f1).decform(g, False) == f0.decform(g, True).W(f1.decform(g, False), toprimal=False)
    
    assert (f1.C(f1)).decform(g, True) == f1.decform(g, True).C(f1.decform(g, True))
    assert (f1.C(f1)).decform(g, False) == f1.decform(g, False).C(f1.decform(g, False), toprimal=False)
    
    g = Grid_1D.chebyshev(11)
    
    f0 = form(0, c, (x,))
    f1 = form(1, c, (x**2,))

    assert (f0^f0).decform(g, True) == f0.decform(g, True) ^ f0.decform(g, True)
    assert (f0^f1).decform(g, True) == f0.decform(g, True) ^ f1.decform(g, True)
    assert (f0^f1).decform(g, False) == f0.decform(g, True).W(f1.decform(g, True), toprimal=False)
    assert (f0^f1).decform(g, False) == f0.decform(g, False).W(f1.decform(g, False), toprimal=False)
    
    assert (f1.C(f1)).decform(g, True) == f1.decform(g, True).C(f1.decform(g, True))
    assert (f1.C(f1)).decform(g, False) == f1.decform(g, False).C(f1.decform(g, False), toprimal=False)

if __name__ == '__main__':
    g = Grid_1D.periodic(11)
    
    f = form(0, c, (sin(x),))
    a = f.decform(g, True)
    b = g.P(f.degree, True, f.lambdify)
    assert a == b
