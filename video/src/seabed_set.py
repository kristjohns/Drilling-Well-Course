"""Reusable seabed production set: wellhead, christmas tree, manifold, jumper, umbilical."""
import bl
import equipment as E
import models as MD


def production_set(M, x0=0.0, with_rov=False):
    seabed = bl.tex_mat('seabed', MD.tex('seabed'))
    bed = bl.box('bed', (400, 400, 0.4), loc=(x0, 0, -0.2), material=seabed)
    bl.uv_box(bed, 6.0)
    wh = E.wellhead(M, cut=False)
    for o in list(wh.values()):
        if hasattr(o, 'location'):
            o.location.x += x0
    xt = E.xmas_tree(M)
    xt.location = (x0, 0, 2.6)
    mf = E.manifold(M)
    mf.location = (x0 + 16, 3, 0)
    jumper_pts = [(x0 + 3.2, 0, 5.2), (x0 + 5, 0, 7.5), (x0 + 9.5, 1.5, 7.5), (x0 + 10.5, 3, 2.2)]
    jp = bl.curve_tube('jumper', jumper_pts, 0.16, M['yellow'])
    umb_pts = [(x0 - 60, 30, 0.15), (x0 - 20, 12, 0.15), (x0 - 6, 4, 0.15), (x0 - 2.5, 1.3, 3.0)]
    um = bl.curve_tube('umbilical', umb_pts, 0.14, bl.mat('umb', '#F59E1B', rough=0.5))
    out = {'xt': xt, 'mf': mf, 'jumper': jp, 'umb': um, 'wh': wh, 'jumper_pts': jumper_pts}
    if with_rov:
        out['rov'] = E.rov(M)
    return out
