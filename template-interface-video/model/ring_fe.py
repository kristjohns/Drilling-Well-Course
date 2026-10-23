"""In-plane analysis of a template slot ring: 2D frame of straight fibre beam elements around the ring, pinned at the
strut connections, loaded by the contact pressure of the conductor over an arc of the inner face.

Units: MN, m, MPa (= MN/m2). Materially non-linear, geometrically linear (MNA in EN 1993-1-5 Table C.1 terms):
the ring is stocky and not susceptible to buckling. Solved with displacement control at the loaded node.

Sign conventions: elements run counter-clockwise; local y points to the ring centre, so y = +w/2 is the inner edge.
Fibre strain eps = eps0 - y * kappa.
"""
import math
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

GP = np.array([0.5 - math.sqrt(0.6) / 2, 0.5, 0.5 + math.sqrt(0.6) / 2])
GW = np.array([5 / 18, 8 / 18, 5 / 18])


class Ring:
    def __init__(self, R, w, t, n_el, E, fy, Et, supports_deg=(0, 90, 180, 270), load_deg=45.0, spread_deg=20.0, nf=40):
        self.R, self.w, self.t, self.n, self.E, self.fy = R, w, t, n_el, E, fy
        self.Et = Et
        self.H = E * Et / (E - Et) if Et > 0 else 0.0          # hardening modulus on plastic strain
        self.th = 2 * math.pi * np.arange(n_el) / n_el           # node angles
        self.xy = np.c_[R * np.cos(self.th), R * np.sin(self.th)]
        self.L = 2 * R * math.sin(math.pi / n_el)
        # element direction cosines (node i -> i+1)
        d = np.roll(self.xy, -1, axis=0) - self.xy
        self.c, self.s = d[:, 0] / self.L, d[:, 1] / self.L
        # fibres through the depth (local y), area each
        self.y = (np.arange(nf) + 0.5) / nf * w - w / 2
        self.A = np.full(nf, w * t / nf)
        self.ndof = 3 * n_el
        # supports: pinned (ux, uy) at the nodes nearest the strut angles
        self.sup_nodes = [int(round(a / 360 * n_el)) % n_el for a in supports_deg]
        fixed = []
        for k in self.sup_nodes: fixed += [3 * k, 3 * k + 1]
        self.fixed = np.array(sorted(fixed))
        self.free = np.setdiff1d(np.arange(self.ndof), self.fixed)
        # reference load: radial contact pressure on an arc (cosine distribution), resultant 1 MN towards load_deg
        self.load_deg = load_deg
        P = np.zeros(self.ndof)
        tl = math.radians(load_deg); a0 = math.radians(spread_deg)
        wts = []
        for i, th in enumerate(self.th):
            dth = (th - tl + math.pi) % (2 * math.pi) - math.pi
            if abs(dth) < a0: wts.append((i, math.cos(math.pi * dth / (2 * a0)), dth))
        tot = sum(wv * math.cos(dth) for _, wv, dth in wts)
        for i, wv, dth in wts:
            P[3 * i] += wv / tot * math.cos(self.th[i]); P[3 * i + 1] += wv / tot * math.sin(self.th[i])
        self.P = P
        self.load_node = int(round(load_deg / 360 * n_el)) % n_el
        # material state per element / Gauss point / fibre (committed and trial)
        sh = (n_el, 3, nf)
        self.ep = np.zeros(sh); self.al = np.zeros(sh)
        self.u = np.zeros(self.ndof); self.lam = 0.0
        # B-matrix pieces per Gauss point (local), element-independent because all elements have length L
        L = self.L
        self.Be = np.array([-1 / L, 0, 0, 1 / L, 0, 0])
        self.Bk = np.array([[0, (-6 + 12 * x) / L**2, (-4 + 6 * x) / L, 0, (6 - 12 * x) / L**2, (-2 + 6 * x) / L] for x in GP])
        # element dof map
        n = n_el
        self.edof = np.array([[3 * i, 3 * i + 1, 3 * i + 2, 3 * ((i + 1) % n), 3 * ((i + 1) % n) + 1, 3 * ((i + 1) % n) + 2] for i in range(n)])

    def T(self, i):
        c, s = self.c[i], self.s[i]
        r = np.array([[c, s, 0], [-s, c, 0], [0, 0, 1]])
        T = np.zeros((6, 6)); T[:3, :3] = r; T[3:, 3:] = r
        return T

    def local_disp(self, u):
        ue = u[self.edof]                                   # (n, 6) global
        c, s = self.c[:, None], self.s[:, None]
        ul = np.empty_like(ue)
        for a in (0, 3):
            ul[:, a] = c[:, 0] * ue[:, a] + s[:, 0] * ue[:, a + 1]
            ul[:, a + 1] = -s[:, 0] * ue[:, a] + c[:, 0] * ue[:, a + 1]
            ul[:, a + 2] = ue[:, a + 2]
        return ul

    def section_strains(self, u):
        ul = self.local_disp(u)
        e0 = ul @ self.Be                                   # (n,)
        kap = ul @ self.Bk.T                                # (n, 3)
        return e0, kap

    def material(self, eps):
        """1D return mapping with linear isotropic hardening; returns stress, tangent, trial plastic state."""
        E, H = self.E, self.H
        sig_tr = E * (eps - self.ep)
        f = np.abs(sig_tr) - (self.fy + H * self.al)
        pl = f > 0
        dg = np.where(pl, f / (E + H), 0.0)
        sgn = np.sign(sig_tr)
        sig = sig_tr - sgn * E * dg
        Et = np.where(pl, E * H / (E + H), E)
        return sig, Et, self.ep + sgn * dg, self.al + dg

    def assemble(self, u, commit=False):
        e0, kap = self.section_strains(u)
        eps = e0[:, None, None] - self.y[None, None, :] * kap[:, :, None]          # (n, 3, nf)
        sig, Et, ep_new, al_new = self.material(eps)
        A, y = self.A, self.y
        N = (sig * A).sum(-1); M = -(sig * A * y).sum(-1)                           # (n, 3)
        D11 = (Et * A).sum(-1); D12 = -(Et * A * y).sum(-1); D22 = (Et * A * y * y).sum(-1)
        L = self.L
        fl = np.zeros((self.n, 6)); kl = np.zeros((self.n, 6, 6))
        for g in range(3):
            Bk = self.Bk[g]
            fl += GW[g] * L * (np.outer(N[:, g], self.Be) + np.outer(M[:, g], Bk))
            BeBe = np.outer(self.Be, self.Be); BeBk = np.outer(self.Be, Bk); BkBk = np.outer(Bk, Bk)
            kl += GW[g] * L * (D11[:, g, None, None] * BeBe + D12[:, g, None, None] * (BeBk + BeBk.T) + D22[:, g, None, None] * BkBk)
        F = np.zeros(self.ndof); rows, cols, vals = [], [], []
        for i in range(self.n):
            T = self.T(i)
            fe = T.T @ fl[i]; ke = T.T @ kl[i] @ T
            F[self.edof[i]] += fe
            rows.append(np.repeat(self.edof[i], 6)); cols.append(np.tile(self.edof[i], 6)); vals.append(ke.ravel())
        K = sp.csr_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(self.ndof, self.ndof))
        if commit:
            self.ep, self.al = ep_new, al_new
        return F, K, eps

    def linear(self):
        """elastic solution for the unit load (from the current, unloaded state)"""
        _, K, _ = self.assemble(np.zeros(self.ndof))
        f = self.free
        u = np.zeros(self.ndof)
        u[f] = spla.spsolve(K[f][:, f].tocsc(), self.P[f])
        e0, kap = self.section_strains(u)
        eps = e0[:, None, None] - self.y[None, None, :] * kap[:, :, None]
        return u, eps

    def control_dof(self):
        k = self.load_node; th = self.th[k]
        e = np.zeros(self.ndof); e[3 * k] = math.cos(th); e[3 * k + 1] = math.sin(th)    # radial displacement at the load node
        return e

    def _newton(self, du_target, tol=1e-8, maxit=25):
        f = self.free; e = self.control_dof()
        u = self.u.copy(); lam = self.lam
        target = e @ self.u + du_target
        for it in range(maxit):
            F, K, _ = self.assemble(u)
            r = F - lam * self.P
            lu = spla.splu(K[f][:, f].tocsc())
            dur = np.zeros(self.ndof); dup = np.zeros(self.ndof)
            dur[f] = lu.solve(-r[f]); dup[f] = lu.solve(self.P[f])
            dl = (target - e @ u - e @ dur) / (e @ dup)
            u += dur + dl * dup; lam += dl
            F, _, _ = self.assemble(u)
            res = np.linalg.norm((F - lam * self.P)[f])
            if res < tol * max(1.0, abs(lam)):
                return u, lam, it + 1
        return None

    def step(self, du_target):
        """one displacement-controlled increment of the radial displacement at the load node (sub-stepped if needed)"""
        todo, its = [du_target], 0
        while todo:
            d = todo.pop(0)
            sol = self._newton(d)
            if sol is None:
                if abs(d) < du_target * 1e-3: raise RuntimeError('no convergence')
                todo = [d / 2, d / 2] + todo
                continue
            u, lam, it = sol; its += it
            _, _, eps = self.assemble(u, commit=True)
            self.u, self.lam = u, lam
        return its, eps

    def fields(self, eps):
        """per element: membrane strain eps0 and curvature (mean over the Gauss points), and the edge strains"""
        e0, kap = self.section_strains(self.u)
        return e0, kap.mean(axis=1)
