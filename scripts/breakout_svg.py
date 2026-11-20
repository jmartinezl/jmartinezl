"""Genera assets/breakout.svg: una partida de brick breaker animada que se juega sola."""

import math
import random
from pathlib import Path

W, H = 800, 420
BAR = 34
COLS, BRICK_W, BRICK_H, GAP, TOP, ROW_STEP = 8, 90, 24, 6, 50, 30
MARGIN = (W - COLS * BRICK_W - (COLS - 1) * GAP) / 2
BALL_R, SPEED = 6, 420
PADDLE_W, PADDLE_H, PADDLE_Y = 110, 10, 395
MAX_ANGLE = math.radians(60)
DT = 1 / 600
MAX_T = 120
OUTRO = 3.5

ROWS = [
    (["Claude", "MCP", "Agents", "LLMs"], "#D97757", "#fff"),
    (["Python", "Node.js", "Bash"], "#3776AB", "#fff"),
    (["AWS", "EKS", "Docker", "Helm"], "#FF9900", "#111"),
    (["Actions", "GitLab CI", "Spinnaker"], "#2088FF", "#fff"),
    (["Datadog", "Prometheus", "Grafana"], "#632CA6", "#fff"),
    (["WAF", "Cloudflare"], "#DD344C", "#fff"),
]


def make_bricks():
    bricks = []
    for r, (labels, fill, text) in enumerate(ROWS):
        for c in range(COLS):
            bricks.append({
                "x": MARGIN + c * (BRICK_W + GAP),
                "y": TOP + r * ROW_STEP,
                "label": labels[(c + r) % len(labels)],
                "fill": fill,
                "text": text,
                "hit": None,
            })
    return bricks


def aim_angle(rng, bx, alive):
    """Ángulo de salida hacia un ladrillo de la fila viva más baja."""
    lowest = max(b["y"] for b in alive)
    target = rng.choice([b for b in alive if b["y"] == lowest])
    dx = target["x"] + BRICK_W / 2 - bx
    dy = PADDLE_Y - (target["y"] + BRICK_H / 2)
    angle = math.atan2(dx, dy) + rng.uniform(-0.08, 0.08)
    return max(-MAX_ANGLE, min(MAX_ANGLE, angle))


def paddle_hit(rng, bx, alive):
    """Devuelve (borde izquierdo de la paleta, vx, vy) para un golpe en bx."""
    angle = aim_angle(rng, bx, alive)
    left = bx - PADDLE_W / 2 - angle / MAX_ANGLE * PADDLE_W / 2
    left = max(0, min(W - PADDLE_W, left))
    angle = (bx - left - PADDLE_W / 2) / (PADDLE_W / 2) * MAX_ANGLE
    angle = max(-MAX_ANGLE, min(MAX_ANGLE, angle))
    return left, SPEED * math.sin(angle), -SPEED * math.cos(angle)


def simulate(seed):
    rng = random.Random(seed)
    bricks = make_bricks()
    t = 0.0
    x, y = W / 2, PADDLE_Y - BALL_R
    left, vx, vy = paddle_hit(rng, x, bricks)
    ball = [(t, x, y)]
    paddle = [(0.0, W / 2 - PADDLE_W / 2), (t, left)]

    while t < MAX_T:
        alive = [b for b in bricks if b["hit"] is None]
        if not alive:
            break
        px, py = x, y
        x, y, t = x + vx * DT, y + vy * DT, t + DT
        bounced = False
        if x < BALL_R or x > W - BALL_R:
            x = min(max(x, BALL_R), W - BALL_R)
            vx, bounced = -vx, True
        if y < BALL_R:
            y, vy, bounced = BALL_R, -vy, True
        for b in alive:
            x0, x1 = b["x"] - BALL_R, b["x"] + BRICK_W + BALL_R
            y0, y1 = b["y"] - BALL_R, b["y"] + BRICK_H + BALL_R
            if x0 <= x <= x1 and y0 <= y <= y1:
                b["hit"] = t
                if px < x0 or px > x1:
                    vx, x = -vx, px
                else:
                    vy, y = -vy, py
                bounced = True
                break
        if vy > 0 and y >= PADDLE_Y - BALL_R:
            y = PADDLE_Y - BALL_R
            left, vx, vy = paddle_hit(rng, x, alive)
            paddle.append((t, left))
            bounced = True
        if bounced:
            ball.append((t, x, y))
    return bricks, ball, paddle, t


def best_run():
    """Busca la semilla que limpia todos los ladrillos en menos tiempo."""
    best = None
    for seed in range(200):
        run = simulate(seed)
        if all(b["hit"] is not None for b in run[0]):
            if best is None or run[3] < best[3]:
                best = run
    return best


def key_times(times, dur):
    """keyTimes estrictamente crecientes entre 0 y 1."""
    out, last = [], -1.0
    for t in times:
        k = max(round(t / dur, 5), last + 0.00001)
        out.append(k)
        last = k
    out[0], out[-1] = 0, 1
    return ";".join(f"{k:.5f}".rstrip("0").rstrip(".") for k in out)


def track(points, end, dur):
    """Extiende una pista de keyframes hasta el final del ciclo."""
    pts = list(points)
    if pts[0][0] > 0:
        pts.insert(0, (0.0,) + pts[0][1:])
    pts.append((end,) + pts[-1][1:])
    pts.append((dur,) + pts[-1][1:])
    return pts


def render(bricks, ball, paddle, end):
    dur = end + OUTRO
    anim = f'dur="{dur:.2f}s" repeatCount="indefinite"'
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H + BAR}" width="{W}" height="{H + BAR}" '
        'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">',
        f'<rect width="{W}" height="{H + BAR}" rx="12" fill="#0d1117" stroke="#30363d"/>',
        f'<path d="M0 {BAR}H{W}" stroke="#30363d"/>',
        '<circle cx="20" cy="17" r="6" fill="#ff5f57"/><circle cx="40" cy="17" r="6" fill="#febc2e"/>'
        '<circle cx="60" cy="17" r="6" fill="#28c840"/>',
        '<text x="84" y="22" font-size="13" fill="#8b949e">jmartinezl@platform:~$ '
        '<tspan fill="#c9d1d9">./deploy --mode=breakout</tspan></text>',
        f'<text x="{W - 16}" y="22" font-size="12" fill="#3fb950" text-anchor="end">▶ click to play</text>',
        f'<g transform="translate(0 {BAR})">',
    ]
    for b in bricks:
        k = b["hit"] / dur
        out.append(
            f'<g><rect x="{b["x"]:.1f}" y="{b["y"]}" width="{BRICK_W}" height="{BRICK_H}" rx="4" fill="{b["fill"]}"/>'
            f'<text x="{b["x"] + BRICK_W / 2:.1f}" y="{b["y"] + 16}" font-size="11" font-weight="600" '
            f'fill="{b["text"]}" text-anchor="middle">{b["label"]}</text>'
            f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;{k:.5f};{min(k + 0.004, 0.999):.5f};1" {anim}/></g>'
        )

    bt = track(ball, end, dur)
    out.append(
        f'<circle r="{BALL_R}" fill="#f0f6fc">'
        f'<animate attributeName="cx" values="{";".join(f"{p[1]:.1f}" for p in bt)}" '
        f'keyTimes="{key_times([p[0] for p in bt], dur)}" {anim}/>'
        f'<animate attributeName="cy" values="{";".join(f"{p[2]:.1f}" for p in bt)}" '
        f'keyTimes="{key_times([p[0] for p in bt], dur)}" {anim}/>'
        f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;{end / dur:.5f};{(end + 0.3) / dur:.5f};1" {anim}/>'
        '</circle>'
    )

    pt = track(paddle, end, dur)
    out.append(
        f'<rect y="{PADDLE_Y}" width="{PADDLE_W}" height="{PADDLE_H}" rx="5" fill="#3fb950">'
        f'<animate attributeName="x" values="{";".join(f"{p[1]:.1f}" for p in pt)}" '
        f'keyTimes="{key_times([p[0] for p in pt], dur)}" {anim}/></rect>'
    )

    k0, k1 = (end + 0.3) / dur, (end + 0.8) / dur
    out.append(
        f'<text x="{W / 2}" y="{H / 2 + 20}" font-size="22" font-weight="700" fill="#3fb950" text-anchor="middle" opacity="0">'
        '✓ all systems operational'
        f'<animate attributeName="opacity" values="0;0;1;1" keyTimes="0;{k0:.5f};{k1:.5f};1" {anim}/></text>'
    )
    out.append("</g></svg>")
    return "\n".join(out)


def main():
    bricks, ball, paddle, end = best_run()
    path = Path(__file__).resolve().parent.parent / "assets" / "breakout.svg"
    path.parent.mkdir(exist_ok=True)
    path.write_text(render(bricks, ball, paddle, end), encoding="utf-8")
    print(f"{path.name}: {end:.1f}s, {len(ball)} rebotes, {len(paddle)} golpes de paleta")


if __name__ == "__main__":
    main()
