"""Bold, text-free illustrations for the publication thumbnails (720x480, dark card).

Shared visual vocabulary:
  stopwatch            fixed-time convergence
  blue / orange pawns  players in a game; a domino mask marks the deceiver
  sine wave            deterministic exploration (dither); jagged line = stochastic exploration
  hollow ring -> star  true Nash equilibrium -> deceptive equilibrium
  fast/slow arrows     two time scales (singular perturbation)
Usage (needs matplotlib and numpy):
  python tools/publication_thumbnails.py assets/img/publication_preview            # all of them
  python tools/publication_thumbnails.py assets/img/publication_preview KEY ...    # just these entries
The file name is the papers.bib key, which papers.bib references in its `preview` field.
"""

import math
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.patches as mp
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.path import Path

BG = "#15181d"
INK = "#e6edf3"
MUTED = "#6e7681"
BLUE = "#58a6ff"
ORANGE = "#f0883e"
GREEN = "#3fb950"
RED = "#ff7b72"
PURPLE = "#d2a8ff"
YELLOW = "#e3b341"
W, H = 300, 200  # drawing units; the image is 720x480 px
rng = np.random.default_rng(7)


def canvas():
    fig = plt.figure(figsize=(7.2, 4.8), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor(BG)
    return fig, ax


def save(fig, out):
    fig.savefig(out, facecolor=BG)
    plt.close(fig)


# ---------------------------------------------------------------- primitives
def arrow(ax, p, q, color=INK, lw=5, head=11, rad=0.0, ls="-", z=3):
    ax.add_patch(
        mp.FancyArrowPatch(
            p, q, arrowstyle=f"-|>,head_length={head / 10},head_width={head / 16}", mutation_scale=20,
            color=color, lw=lw, ls=ls, connectionstyle=f"arc3,rad={rad}", shrinkA=0, shrinkB=0, zorder=z,
            capstyle="round", joinstyle="round",
        )
    )


def stopwatch(ax, cx, cy, r, color=INK, frac=0.62, fill=GREEN):
    ax.add_patch(mp.Wedge((cx, cy), r * 0.78, 90 - 360 * frac, 90, color=fill, alpha=0.9, zorder=4))
    ax.add_patch(mp.Circle((cx, cy), r, fill=False, ec=color, lw=6, zorder=5))
    ax.add_patch(mp.FancyBboxPatch((cx - r * 0.18, cy + r * 1.08), r * 0.36, r * 0.22, boxstyle="round,pad=0,rounding_size=2", color=color, zorder=5))
    ax.plot([cx, cx], [cy + r, cy + r * 1.1], color=color, lw=5, zorder=5)
    a = math.radians(90 - 360 * frac)
    ax.plot([cx, cx + 0.72 * r * math.cos(a)], [cy, cy + 0.72 * r * math.sin(a)], color=color, lw=5, solid_capstyle="round", zorder=6)
    ax.add_patch(mp.Circle((cx, cy), r * 0.1, color=color, zorder=7))


def pawn(ax, cx, base_y, s, color, masked=False):
    """Game piece of height ~3.2*s standing on base_y."""
    ax.add_patch(mp.FancyBboxPatch((cx - 1.1 * s, base_y), 2.2 * s, 0.38 * s, boxstyle="round,pad=0,rounding_size=3", color=color, zorder=4))
    body = Path([(cx - 0.85 * s, base_y + 0.35 * s), (cx - 0.35 * s, base_y + 1.9 * s), (cx + 0.35 * s, base_y + 1.9 * s), (cx + 0.85 * s, base_y + 0.35 * s), (cx - 0.85 * s, base_y + 0.35 * s)])
    ax.add_patch(mp.PathPatch(body, color=color, zorder=4))
    hy = base_y + 2.45 * s
    ax.add_patch(mp.Circle((cx, hy), 0.72 * s, color=color, zorder=5))
    if masked:
        mask(ax, cx, hy + 0.05 * s, 1.75 * s)
    return hy


def mask(ax, cx, cy, w, color="#111318", eye=None):
    """Domino (eye) mask centred at (cx, cy), width w."""
    h = w * 0.42
    ax.add_patch(mp.Ellipse((cx - w * 0.25, cy), w * 0.55, h, color=color, zorder=8))
    ax.add_patch(mp.Ellipse((cx + w * 0.25, cy), w * 0.55, h, color=color, zorder=8))
    ax.add_patch(mp.Rectangle((cx - w * 0.2, cy - h * 0.12), w * 0.4, h * 0.42, color=color, zorder=8))
    e = eye or INK
    ax.add_patch(mp.Ellipse((cx - w * 0.24, cy + h * 0.02), w * 0.22, h * 0.36, color=e, zorder=9))
    ax.add_patch(mp.Ellipse((cx + w * 0.24, cy + h * 0.02), w * 0.22, h * 0.36, color=e, zorder=9))


def big_mask(ax, cx, cy, w, color=RED):
    """Large standalone mask with ties."""
    h = w * 0.42
    for sgn in (-1, 1):
        ax.plot([cx + sgn * w * 0.5, cx + sgn * w * 0.66], [cy + h * 0.1, cy + h * 0.32], color=color, lw=5, solid_capstyle="round", zorder=7)
        ax.plot([cx + sgn * w * 0.5, cx + sgn * w * 0.7], [cy + h * 0.05, cy - h * 0.12], color=color, lw=5, solid_capstyle="round", zorder=7)
    mask(ax, cx, cy, w, color=color, eye=BG)


def sine(ax, x0, x1, y, amp, cycles, color, lw=5, z=3):
    x = np.linspace(x0, x1, 300)
    ax.plot(x, y + amp * np.sin(2 * np.pi * cycles * (x - x0) / (x1 - x0)), color=color, lw=lw, solid_capstyle="round", zorder=z)


def noise(ax, x0, x1, y, amp, color, lw=4, n=60, z=3, seed=None):
    g = np.random.default_rng(seed)
    x = np.linspace(x0, x1, n)
    ax.plot(x, y + amp * g.uniform(-1, 1, n), color=color, lw=lw, solid_joinstyle="round", zorder=z)


def star(ax, cx, cy, r, color, z=8):
    pts = []
    for k in range(10):
        rr = r if k % 2 == 0 else r * 0.45
        a = math.pi / 2 + k * math.pi / 5
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    ax.add_patch(mp.Polygon(pts, color=color, zorder=z))


def ring(ax, cx, cy, r, color, lw=5, z=7):
    ax.add_patch(mp.Circle((cx, cy), r, fill=False, ec=color, lw=lw, zorder=z))


def gear(ax, cx, cy, r, color, teeth=8, z=5):
    pts = []
    for k in range(teeth * 4):
        a = 2 * math.pi * k / (teeth * 4)
        rr = r if (k % 4) in (0, 1) else r * 0.78
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    ax.add_patch(mp.Polygon(pts, color=color, zorder=z))
    ax.add_patch(mp.Circle((cx, cy), r * 0.3, color=BG, zorder=z + 1))


def node(ax, cx, cy, r, color, z=5):
    ax.add_patch(mp.Circle((cx, cy), r, color=color, zorder=z))


def rbox(ax, x, y, w, h, color, fill=None, lw=5, z=4, rs=10):
    ax.add_patch(mp.FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={rs}", fc=fill or "none", ec=color, lw=lw, zorder=z))


def fxt_curve(ax, x0, x1, ytop, ybot, color, lw=5, z=6, hit=0.78):
    """Fixed-time convergence icon: decays then drops to zero at a finite time and stays."""
    xh = x0 + hit * (x1 - x0)
    t = np.linspace(0, 1, 120)
    xs = x0 + t * (xh - x0)
    ys = ybot + (ytop - ybot) * (1 - t) ** 0.35 * (1 - 0.15 * t)
    xs = np.r_[xs, x1]
    ys = np.r_[ys, ybot]
    ax.plot(xs, ys, color=color, lw=lw, solid_capstyle="round", solid_joinstyle="round", zorder=z)


def dice(ax, cx, cy, s, color=INK, pip=BG, n=5, z=6):
    ax.add_patch(mp.FancyBboxPatch((cx - s / 2, cy - s / 2), s, s, boxstyle=f"round,pad=0,rounding_size={s * 0.18}", color=color, zorder=z))
    pos = {5: [(-1, 1), (1, 1), (0, 0), (-1, -1), (1, -1)], 3: [(-1, 1), (0, 0), (1, -1)]}[n]
    for px, py in pos:
        ax.add_patch(mp.Circle((cx + px * s * 0.27, cy + py * s * 0.27), s * 0.09, color=pip, zorder=z + 1))


def slow_manifold(ax, x0, x1, f, color=MUTED, lw=6):
    x = np.linspace(x0, x1, 200)
    ax.plot(x, f(x), color=color, lw=lw, solid_capstyle="round", zorder=2)


# ---------------------------------------------------------------- illustrations
def j4_smallgain_iss_games(out):
    """Small-gain FxT-ISS with optimization & games: plant + two players in a loop, disturbance in, stopwatch."""
    fig, ax = canvas()
    gear(ax, 150, 152, 32, INK)
    pawn(ax, 62, 18, 17, BLUE)
    pawn(ax, 238, 18, 17, ORANGE)
    arrow(ax, (114, 160), (66, 108), BLUE, rad=0.3)
    arrow(ax, (234, 108), (186, 160), ORANGE, rad=0.3)
    arrow(ax, (94, 52), (206, 52), INK)
    arrow(ax, (206, 30), (94, 30), INK)
    # bounded disturbance entering the plant (input-to-state stability)
    xs = np.linspace(196, 262, 120)
    ax.plot(xs, 186 + 6 * np.sin((xs - 196) / 5.5), color=PURPLE, lw=4.5, zorder=3)
    arrow(ax, (198, 186), (182, 178), PURPLE, lw=4.5, head=9)
    stopwatch(ax, 150, 88, 22)
    save(fig, out)


def c7_smallgain_fxts(out):
    """Small-gain FxTS: two subsystems in feedback, each converging in fixed time."""
    fig, ax = canvas()
    rbox(ax, 22, 112, 116, 66, BLUE, fill="#1c2a3d")
    rbox(ax, 132, 20, 116, 66, GREEN, fill="#1a2e22")
    fxt_curve(ax, 38, 122, 166, 124, BLUE)
    fxt_curve(ax, 148, 232, 74, 32, GREEN)
    ax.plot([138, 190], [145, 145], color=INK, lw=5, solid_capstyle="round", zorder=3)
    arrow(ax, (190, 145), (190, 94), INK)
    ax.plot([132, 80], [53, 53], color=INK, lw=5, solid_capstyle="round", zorder=3)
    arrow(ax, (80, 53), (80, 104), INK)
    stopwatch(ax, 252, 146, 26)
    save(fig, out)


def two_timescale(ax, disturbance=False):
    f = lambda x: 72 + 0.0042 * (x - 150) ** 2 - 0.08 * (x - 150)  # slow manifold
    slow_manifold(ax, 22, 278, f)
    eq = (150, f(150))
    # fast transients: double arrowheads snapping onto the manifold
    for x0, y0, c in [(40, 188, BLUE), (95, 182, BLUE), (210, 14, ORANGE), (262, 20, ORANGE), (262, 186, BLUE)]:
        y1 = f(x0)
        arrow(ax, (x0, y0), (x0, y1 + (8 if y0 > y1 else -8)), c, lw=5, head=10)
        mid = (y0 + y1) / 2
        arrow(ax, (x0, y0), (x0, mid), c, lw=5, head=10)
    # slow motion along the manifold to the equilibrium
    for xa, xb in [(52, 112), (248, 188)]:
        xs = np.linspace(xa, xb, 60)
        ax.plot(xs, f(xs) + 0, color=YELLOW, lw=7, solid_capstyle="round", zorder=4)
        arrow(ax, (xs[-6], f(xs[-6])), (xs[-1], f(xs[-1])), YELLOW, lw=7, head=12)
    if disturbance:
        ax.add_patch(mp.Circle(eq, 15, fc="#3fb95033", ec=GREEN, lw=3, ls=(0, (3, 2)), zorder=5))
        noise(ax, 168, 210, 128, 7, PURPLE, lw=4, n=14, seed=11)
        arrow(ax, (170, 128), (160, 92), PURPLE, lw=4, head=9)
    node(ax, *eq, 7, GREEN, z=8)
    return eq


def j2_fxt_iss_singular(out):
    """Two-time-scale system: fast snaps onto the slow manifold, then slides in fixed time; disturbance -> small ball."""
    fig, ax = canvas()
    two_timescale(ax, disturbance=True)
    stopwatch(ax, 40, 34, 20)
    save(fig, out)


def c1_fxts_singular(out):
    """Two-time-scale fixed-time stability: exact convergence (no disturbance)."""
    fig, ax = canvas()
    eq = two_timescale(ax, disturbance=False)
    ring(ax, *eq, 14, GREEN, lw=4)
    stopwatch(ax, 40, 34, 20)
    save(fig, out)


def c6_hybrid_fxts(out):
    """Hybrid system (bouncing ball): flows and jumps, all motion ends before a fixed-time wall."""
    fig, ax = canvas()
    ground = 34
    ax.plot([16, 284], [ground, ground], color=MUTED, lw=6, solid_capstyle="round")
    x, h, vx = 30.0, 128.0, 1.0
    segs, width = [], 62.0
    for k in range(6):
        xs = np.linspace(x, x + width, 80)
        if k == 0:
            ys = ground + h * (1 - ((xs - x) / width) ** 2)
        else:
            ys = ground + h * 4 * ((xs - x) / width) * (1 - (xs - x) / width)
        ax.plot(xs, ys, color=BLUE, lw=6, solid_capstyle="round", zorder=4)
        x += width
        segs.append(x)
        h *= 0.42
        width *= 0.55
        if width < 2:
            break
    for xj in segs[:-1]:
        ax.add_patch(mp.Circle((xj, ground), 5, color=ORANGE, zorder=6))  # jump instants
    ax.plot([x, 238], [ground, ground], color=GREEN, lw=8, solid_capstyle="round", zorder=5)
    ax.add_patch(mp.Circle((30, ground + 128 + 11), 11, color=INK, zorder=6))  # the ball
    wall = 238
    ax.plot([wall, wall], [ground, 182], color=INK, lw=4, ls=(0, (4, 3)))
    stopwatch(ax, 262, 154, 20)
    save(fig, out)


def c2_filterless_es(out):
    """Extremum seeking on an unknown bowl: dithered probe slides to the minimum in fixed time."""
    fig, ax = canvas()
    xs = np.linspace(20, 230, 200)
    f = lambda x: 40 + 0.0105 * (x - 140) ** 2
    ax.plot(xs, f(xs), color=MUTED, lw=7, solid_capstyle="round", zorder=2)
    t = np.linspace(0, 1, 600)
    cx = 40 + (140 - 40) * (1 - (1 - t) ** 1.8)
    wig = 11 * np.sin(2 * np.pi * 7 * t) * (1 - t) ** 0.8
    ax.plot(cx, f(cx) + 16 + wig, color=BLUE, lw=4.5, solid_joinstyle="round", zorder=4)
    node(ax, cx[0], f(cx[0]) + 16, 9, BLUE, z=6)
    star(ax, 140, f(140) + 3, 13, GREEN)
    stopwatch(ax, 258, 150, 22)
    save(fig, out)


def j3_separation(out):
    """Separation principle: noisy trajectories funnel to the optimum; feedback and optimizer designed separately."""
    fig, ax = canvas()
    # funnel
    xs = np.linspace(20, 236, 200)
    half = 8 + 70 * np.exp(-(xs - 20) / 55)
    yc = 92
    ax.fill_between(xs, yc - half, yc + half, color=BLUE, alpha=0.13, lw=0, zorder=1)
    ax.plot(xs, yc + half, color=BLUE, lw=3, alpha=0.6, zorder=2)
    ax.plot(xs, yc - half, color=BLUE, lw=3, alpha=0.6, zorder=2)
    g = np.random.default_rng(4)
    for k, c in enumerate([BLUE, PURPLE, ORANGE, YELLOW, BLUE, PURPLE]):
        y0 = yc + (k - 2.5) * 22
        steps = g.normal(0, 3.4, xs.size).cumsum() * 0.0
        y = yc + (y0 - yc) * np.exp(-(xs - 20) / 45) + g.normal(0, 2.6, xs.size)
        ax.plot(xs, y, color=c, lw=2.6, alpha=0.95, zorder=3)
    star(ax, 252, yc, 15, GREEN)
    # separation: two independent design blocks over a dashed divider
    ax.plot([150, 150], [160, 196], color=MUTED, lw=4, ls=(0, (3, 2)))
    rbox(ax, 86, 164, 54, 30, BLUE, fill="#1c2a3d", lw=4, rs=8)
    rbox(ax, 160, 164, 54, 30, GREEN, fill="#1a2e22", lw=4, rs=8)
    # feedback icon (loop) and optimizer icon (downhill)
    ax.add_patch(mp.Arc((113, 179), 26, 18, theta1=30, theta2=330, color=BLUE, lw=4, zorder=6))
    arrow(ax, (124, 184), (125, 181), BLUE, lw=4, head=7)
    xx = np.linspace(170, 204, 40)
    ax.plot(xx, 172 + 0.06 * (xx - 187) ** 2, color=GREEN, lw=4, zorder=6)
    node(ax, 177, 172 + 0.06 * 100, 4, GREEN, z=7)
    save(fig, out)


def nes_scene(ax, wave="sine"):
    """Victim (blue) and masked deceiver (orange) probing the game; deceiver taps the victim's signal."""
    pawn(ax, 48, 30, 18, BLUE)
    pawn(ax, 252, 30, 18, ORANGE, masked=True)
    rbox(ax, 102, 28, 96, 92, INK, fill="#20252c", lw=5, rs=12)
    # game board: payoff contours around the true equilibrium
    for r in (12, 24, 36):
        ax.add_patch(mp.Ellipse((136, 70), r * 1.7, r * 1.25, fill=False, ec=MUTED, lw=3, zorder=5))
    if wave == "sine":
        sine(ax, 30, 92, 150, 11, 2.5, BLUE, lw=5.5)
        sine(ax, 208, 270, 150, 11, 2.5, ORANGE, lw=5.5)
    else:
        noise(ax, 30, 92, 150, 11, BLUE, lw=4.5, n=24, seed=5)
        noise(ax, 208, 270, 150, 11, ORANGE, lw=4.5, n=24, seed=6)
    # eavesdropping: the deceiver copies the victim's exploration signal
    ax.add_patch(mp.FancyArrowPatch((70, 168), (230, 172), connectionstyle="arc3,rad=-0.3", arrowstyle="-|>,head_length=0.6,head_width=0.4", mutation_scale=20, color=RED, lw=4.5, ls=(0, (2, 2)), zorder=6))


def j1_deception_nes(out):
    fig, ax = canvas()
    nes_scene(ax, "sine")
    # equilibrium moves from the true NE (ring) to the deceptive NE (star)
    ring(ax, 136, 70, 8, INK, lw=4.5, z=8)
    arrow(ax, (146, 74), (166, 86), RED, lw=4.5, head=9, z=8)
    star(ax, 174, 92, 13, ORANGE, z=9)
    save(fig, out)


def c5_stochastic_deception(out):
    fig, ax = canvas()
    nes_scene(ax, "noise")
    ring(ax, 136, 70, 8, INK, lw=4.5, z=8)
    arrow(ax, (146, 74), (166, 86), RED, lw=4.5, head=9, z=8)
    star(ax, 174, 92, 13, ORANGE, z=9)
    save(fig, out)


def c9_deceptive_bandit(out):
    """Bandit learning: the victim's randomized exploration (dice) leaks to a masked deceiver."""
    fig, ax = canvas()
    # slot machine in the centre
    rbox(ax, 112, 40, 76, 96, INK, fill="#20252c", lw=5, rs=10)
    for k, c in enumerate([BLUE, YELLOW, ORANGE]):
        ax.add_patch(mp.FancyBboxPatch((122 + k * 20, 92), 16, 28, boxstyle="round,pad=0,rounding_size=3", color=c, zorder=6))
    ax.add_patch(mp.FancyBboxPatch((126, 52), 48, 12, boxstyle="round,pad=0,rounding_size=4", color=MUTED, zorder=6))
    ax.plot([188, 200, 200], [96, 96, 128], color=INK, lw=5, solid_capstyle="round", zorder=5)
    node(ax, 200, 134, 7, RED, z=6)
    pawn(ax, 44, 40, 15, BLUE)
    pawn(ax, 256, 40, 15, ORANGE, masked=True)
    dice(ax, 82, 156, 26, INK, n=5)
    arrow(ax, (82, 140), (110, 112), BLUE, lw=4, head=8)
    # leak
    ax.add_patch(mp.FancyArrowPatch((98, 168), (246, 120), connectionstyle="arc3,rad=-0.3", arrowstyle="-|>,head_length=0.6,head_width=0.4", mutation_scale=20, color=RED, lw=4, ls=(0, (2, 2)), zorder=7))
    save(fig, out)


def shop(ax, x, y, w, color, masked=False, bar=40):
    ax.add_patch(mp.Rectangle((x, y), w, w * 0.8, color="#20252c", ec=INK, lw=4, zorder=4))
    n = 4
    for k in range(n):
        ax.add_patch(mp.Polygon([(x - 4 + k * (w + 8) / n, y + w * 0.8), (x - 4 + (k + 1) * (w + 8) / n, y + w * 0.8), (x - 4 + (k + 1) * (w + 8) / n, y + w * 0.8 + 14), (x - 4 + k * (w + 8) / n, y + w * 0.8 + 14)], color=color if k % 2 == 0 else INK, zorder=5))
    ax.add_patch(mp.Rectangle((x + w * 0.38, y), w * 0.24, w * 0.42, color=color, zorder=5))
    if masked:
        mask(ax, x + w / 2, y + w * 0.62, w * 0.62)
    # price / profit bar above
    ax.add_patch(mp.FancyBboxPatch((x + w * 0.3, y + w * 0.8 + 22), w * 0.4, bar, boxstyle="round,pad=0,rounding_size=3", color=color, zorder=5))


def c3_oligopoly(out):
    fig, ax = canvas()
    ax.plot([14, 286], [30, 30], color=MUTED, lw=5)
    shop(ax, 26, 30, 62, BLUE, bar=34)
    shop(ax, 119, 30, 62, GREEN, bar=30)
    shop(ax, 212, 30, 62, ORANGE, masked=True, bar=64)
    arrow(ax, (262, 120), (262, 168), RED, lw=4, head=8)
    save(fig, out)


def shield(ax, cx, cy, s, color):
    p = Path([(cx, cy + s), (cx + 0.8 * s, cy + 0.72 * s), (cx + 0.72 * s, cy - 0.2 * s), (cx, cy - s), (cx - 0.72 * s, cy - 0.2 * s), (cx - 0.8 * s, cy + 0.72 * s), (cx, cy + s)], [Path.MOVETO, Path.LINETO, Path.CURVE3, Path.CURVE3, Path.CURVE3, Path.CURVE3, Path.CLOSEPOLY][:7])
    verts = [(cx, cy + s), (cx + 0.8 * s, cy + 0.7 * s), (cx + 0.75 * s, cy - 0.25 * s), (cx, cy - s), (cx - 0.75 * s, cy - 0.25 * s), (cx - 0.8 * s, cy + 0.7 * s)]
    ax.add_patch(mp.Polygon(verts, closed=True, fc="#1a2e22", ec=color, lw=5, joinstyle="round", zorder=5))
    ax.plot([cx - 0.3 * s, cx - 0.05 * s, cx + 0.38 * s], [cy + 0.05 * s, cy - 0.25 * s, cy + 0.35 * s], color=color, lw=5, solid_capstyle="round", zorder=6)


def network(ax, cx, cy, s, color):
    pts = [(cx, cy + s), (cx - s * 0.9, cy + s * 0.2), (cx + s * 0.9, cy + s * 0.2), (cx - s * 0.5, cy - s * 0.8), (cx + s * 0.5, cy - s * 0.8)]
    for i, j in [(0, 1), (0, 2), (1, 3), (2, 4), (3, 4), (1, 2), (0, 3)]:
        ax.plot([pts[i][0], pts[j][0]], [pts[i][1], pts[j][1]], color=MUTED, lw=3.5, zorder=4)
    for p in pts:
        node(ax, *p, s * 0.2, color, z=5)


def loop_icon(ax, cx, cy, s, color):
    gear(ax, cx, cy, s * 0.5, color)
    ax.add_patch(mp.Arc((cx, cy), s * 1.7, s * 1.7, theta1=20, theta2=340, color=color, lw=4.5, zorder=5))
    a = math.radians(20)
    arrow(ax, (cx + 0.85 * s * math.cos(a) - 2, cy + 0.85 * s * math.sin(a) - 6), (cx + 0.85 * s * math.cos(a), cy + 0.85 * s * math.sin(a) + 1), color, lw=4.5, head=9, z=6)


def c4_deception_tutorial(out):
    """Tutorial: deception across cyber security, games / learning, and control."""
    fig, ax = canvas()
    big_mask(ax, 150, 104, 96, RED)
    for (x, y) in [(52, 154), (248, 154), (52, 48), (248, 48)]:
        ax.plot([150 + (x - 150) * 0.35, x + (150 - x) * 0.22], [104 + (y - 104) * 0.35, y + (104 - y) * 0.22], color=MUTED, lw=3, ls=(0, (2, 2)), zorder=2)
    shield(ax, 52, 154, 26, GREEN)
    network(ax, 248, 154, 26, PURPLE)
    pawn(ax, 40, 24, 10, BLUE)
    pawn(ax, 66, 24, 10, ORANGE)
    loop_icon(ax, 248, 48, 30, BLUE)
    save(fig, out)


def hexgrid(ax, color):
    r = 17
    for i in range(-1, 12):
        for j in range(-1, 9):
            cx = i * 1.5 * r
            cy = j * math.sqrt(3) * r + (math.sqrt(3) * r / 2 if i % 2 else 0)
            ax.add_patch(mp.RegularPolygon((cx, cy), 6, radius=r, orientation=math.pi / 6, fill=False, ec=color, lw=1.6, zorder=1))


def neural(ax, cx, cy, s, color):
    layers = [3, 4, 2]
    pos = []
    for li, n in enumerate(layers):
        x = cx + (li - 1) * s
        ys = [cy + (k - (n - 1) / 2) * s * 0.62 for k in range(n)]
        pos.append([(x, y) for y in ys])
    for a, b in zip(pos[:-1], pos[1:]):
        for p in a:
            for q in b:
                ax.plot([p[0], q[0]], [p[1], q[1]], color=MUTED, lw=2.4, zorder=3)
    for layer in pos:
        for p in layer:
            node(ax, *p, s * 0.16, color, z=4)


def bloch(ax, cx, cy, r, color):
    ax.add_patch(mp.Circle((cx, cy), r, fc="#1e1a2b", ec=color, lw=5, zorder=4))
    ax.add_patch(mp.Arc((cx, cy), 2 * r, 0.6 * r, theta1=180, theta2=360, color=color, lw=4, zorder=5))
    ax.add_patch(mp.Arc((cx, cy), 2 * r, 0.6 * r, theta1=0, theta2=180, color=color, lw=3, ls=(0, (2, 2)), alpha=0.7, zorder=5))
    arrow(ax, (cx, cy), (cx + r * 0.55, cy + r * 0.68), YELLOW, lw=5, head=9, z=6)
    node(ax, cx, cy, r * 0.08, INK, z=7)


def c8_ai_quantum_tutorial(out):
    """Tutorial: AI (network), quantum (Bloch sphere) and deception (mask) on a wargame hex board."""
    fig, ax = canvas()
    hexgrid(ax, "#232a33")
    neural(ax, 70, 118, 30, BLUE)
    bloch(ax, 230, 118, 40, PURPLE)
    big_mask(ax, 150, 40, 62, RED)
    arrow(ax, (108, 92), (128, 62), MUTED, lw=4, head=8)
    arrow(ax, (196, 88), (172, 62), MUTED, lw=4, head=8)
    save(fig, out)


ALL = {
    "tang2027smallgain": j4_smallgain_iss_games,
    "tang2026separation": j3_separation,
    "tang2026fixedtimeiss": j2_fxt_iss_singular,
    "tang2025deception": j1_deception_nes,
    "tang2026bandit": c9_deceptive_bandit,
    "vamvoudakis2026tutorial": c8_ai_quantum_tutorial,
    "tang2026smallgainacc": c7_smallgain_fxts,
    "tang2025hybrid": c6_hybrid_fxts,
    "tang2025stochasticdeception": c5_stochastic_deception,
    "vamvoudakis2025tutorial": c4_deception_tutorial,
    "tang2025oligopoly": c3_oligopoly,
    "tang2024filterless": c2_filterless_es,
    "tang2024singular": c1_fxts_singular,
}

if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    only = sys.argv[2:] or list(ALL)
    for k in only:
        ALL[k](os.path.join(out, k + ".png"))
        print(k)
