"""
JEV PHYSICS LAB
================

LinkedIn-ready demo showing how TypeSafe AI's Jev can make typed
decisions that directly control a running physics simulation.

Flow:
    WORLD STATE -> JEV -> TYPED DECISION -> PHYSICS

Setup:
    pip install matplotlib numpy requests pillow

Windows PowerShell:
    $env:TYPESAFE_API_KEY="YOUR_NEW_KEY"

"""

import argparse
import os
import random
import time

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import FancyBboxPatch

try:
    import requests
except ImportError:
    requests = None


TYPESAFE_URL = "https://api.typesafe.ai/v1/systemone"
API_KEY = os.environ.get("TYPESAFE_API_KEY")

SCENARIOS = [
    ("a soap bubble", "an ice rink"),
    ("a brick", "a pillow"),
    ("a super ball", "a trampoline"),
    ("a water balloon", "a concrete floor"),
    ("a glass ornament", "a chalkboard"),
    ("a beach ball", "a trampoline"),
    ("a bowling ball", "a pillow"),
]

SOUND_OPTIONS = {
    "thud": "a heavy dull impact",
    "splat": "a wet messy impact",
    "ding": "a sharp metallic or glass sound",
    "boing": "a springy bouncy sound",
    "pop": "a light burst",
}

SOUND_KEYS = list(SOUND_OPTIONS)


def fallback_decision(material, surface):
    """Sensible fallback so the demo still works without Jev."""
    m = material.lower()
    s = surface.lower()

    if "soap bubble" in m:
        return random.uniform(0.80, 0.98), random.choice(["pop", "ding"]), "FALLBACK"
    if "brick" in m:
        return random.uniform(0.10, 0.30), "thud", "FALLBACK"
    if "super ball" in m:
        return random.uniform(0.85, 1.00), "boing", "FALLBACK"
    if "water balloon" in m:
        return random.uniform(0.15, 0.40), "splat", "FALLBACK"
    if "glass ornament" in m:
        return random.uniform(0.20, 0.45), "ding", "FALLBACK"
    if "trampoline" in s:
        return random.uniform(0.80, 1.00), "boing", "FALLBACK"

    return random.uniform(0.25, 0.75), random.choice(SOUND_KEYS), "FALLBACK"


def ask_jev(material, surface):
    """Ask Jev for a Score (bounciness) and Choice (sound)."""
    if not API_KEY or requests is None:
        return fallback_decision(material, surface)

    state = (
        f"{material.capitalize()} collides with {surface}. "
        "Decide how the collision should behave."
    )

    payload = {
        "state": state,
        "model": "jev-latest",
        "questions": {
            "bounciness": {
                "type": "score",
                "instructions": (
                    "How much of the impact energy should survive as bounce?"
                ),
                "criteria": [
                    "No bounce, absorbs completely",
                    "Partial bounce",
                    "Nearly perfectly elastic",
                ],
            },
            "sound": {
                "type": "choice",
                "instructions": "What sound would this collision make?",
                "criteria": SOUND_OPTIONS,
            },
        },
    }

    try:
        started = time.time()

        response = requests.post(
            TYPESAFE_URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=5,
        )
        response.raise_for_status()

        data = response.json()["answers"]
        bounciness = data["bounciness"]["score"] / 2.0
        sound = data["sound"]["choice"]

        bounciness = max(0.05, min(1.0, bounciness))

        print(
            f"[JEV] {material} × {surface} -> "
            f"score={bounciness:.2f}, sound={sound}, "
            f"{time.time() - started:.2f}s"
        )

        return bounciness, sound, "JEV"

    except Exception as exc:
        print(f"[JEV] API error: {exc}")
        return fallback_decision(material, surface)


class Ball:
    def __init__(self, box_size, color):
        self.r = 0.35
        self.pos = np.array([
            random.uniform(self.r, box_size - self.r),
            random.uniform(self.r, box_size - self.r),
        ])

        angle = random.uniform(0, 2 * np.pi)
        speed = random.uniform(4.0, 5.0)

        self.vel = speed * np.array([
            np.cos(angle),
            np.sin(angle),
        ])
        self.color = color

    def step(self, dt, box_size):
        self.pos += self.vel * dt

        if self.pos[0] - self.r <= 0:
            self.pos[0] = self.r
            return 0

        if self.pos[0] + self.r >= box_size:
            self.pos[0] = box_size - self.r
            return 0

        if self.pos[1] - self.r <= 0:
            self.pos[1] = self.r
            return 1

        if self.pos[1] + self.r >= box_size:
            self.pos[1] = box_size - self.r
            return 1

        return None


def rounded_box(ax, x, y, width, height,
                facecolor="#FFFFFF", edgecolor="#D6D3CC"):
    box = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.012,rounding_size=0.025",
        linewidth=1,
        edgecolor=edgecolor,
        facecolor=facecolor,
        transform=ax.transAxes,
    )
    ax.add_patch(box)
    return box


def draw_score_bar(ax, x, y, width, value):
    rounded_box(
        ax, x, y, width, 0.045,
        facecolor="#ECEAE4",
        edgecolor="#ECEAE4",
    )

    if value > 0:
        rounded_box(
            ax, x, y, width * value, 0.045,
            facecolor="#1D9E75",
            edgecolor="#1D9E75",
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seconds", type=float, default=15)
    parser.add_argument("--fps", type=int, default=20)
    parser.add_argument("--box-size", type=float, default=10)
    parser.add_argument("--out", default="jev_physics_lab.gif")
    args = parser.parse_args()

    print()
    print("=" * 65)
    print("JEV PHYSICS LAB")
    print("=" * 65)
    print("Mode:", "LIVE JEV" if API_KEY else "FALLBACK")
    if not API_KEY:
        print('Set API key with: $env:TYPESAFE_API_KEY="YOUR_KEY"')
    print("=" * 65)

    fig = plt.figure(figsize=(12, 7), facecolor="#FCFBF8")

    ax = fig.add_axes([0.055, 0.19, 0.56, 0.69])
    panel = fig.add_axes([0.655, 0.19, 0.30, 0.69])

    ax.set_xlim(0, args.box_size)
    ax.set_ylim(0, args.box_size)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_facecolor("#F7F5F0")
    panel.set_xticks([])
    panel.set_yticks([])
    panel.set_facecolor("#F7F5F0")

    for spine in ax.spines.values():
        spine.set_color("#C8C5BD")
        spine.set_linewidth(1.2)

    for spine in panel.spines.values():
        spine.set_color("#C8C5BD")
        spine.set_linewidth(1.2)

    fig.text(
        0.055, 0.945, "JEV PHYSICS LAB",
        fontsize=22, fontweight="bold", color="#20201E",
    )
    fig.text(
        0.055, 0.905,
        "Typed model decisions → real program behavior",
        fontsize=11, color="#6B6963",
    )
    fig.text(
        0.955, 0.945, "TypeSafe AI",
        fontsize=11, color="#6B6963", ha="right",
    )

    flow = [
        (0.055, "COLLISION", "#888780"),
        (0.275, "JEV", "#1D9E75"),
        (0.385, "TYPED DECISION", "#888780"),
        (0.570, "PHYSICS", "#D85A30"),
    ]
    for x, label, color in flow:
        fig.text(
            x, 0.115, label,
            fontsize=8, fontweight="bold", color=color,
        )

    fig.text(0.23, 0.115, "→", fontsize=12, color="#888780")
    fig.text(0.34, 0.115, "→", fontsize=12, color="#888780")
    fig.text(0.525, 0.115, "→", fontsize=12, color="#888780")

    ball = Ball(args.box_size, "#D85A30")
    circle = plt.Circle(ball.pos, ball.r, color=ball.color)
    ax.add_patch(circle)

    panel.text(
        0.07, 0.94, "JEV DECISION",
        fontsize=14, fontweight="bold", color="#20201E",
        transform=panel.transAxes,
    )

    panel.text(
        0.07, 0.885, "Waiting for collision...",
        fontsize=8, color="#888780",
        transform=panel.transAxes,
    )

    panel.text(
        0.07, 0.79, "WORLD STATE",
        fontsize=8, fontweight="bold", color="#888780",
        transform=panel.transAxes,
    )

    world_text = panel.text(
        0.07, 0.70, "",
        fontsize=11, color="#20201E",
        transform=panel.transAxes, va="top", wrap=True,
    )

    panel.text(
        0.07, 0.51, "BOUNCINESS  •  SCORE",
        fontsize=8, fontweight="bold", color="#888780",
        transform=panel.transAxes,
    )

    bounce_value = panel.text(
        0.93, 0.51, "—",
        fontsize=13, fontweight="bold", color="#1D9E75",
        transform=panel.transAxes, ha="right",
    )

    panel.text(
        0.07, 0.33, "SOUND  •  CHOICE",
        fontsize=8, fontweight="bold", color="#888780",
        transform=panel.transAxes,
    )

    sound_value = panel.text(
        0.07, 0.23, "—",
        fontsize=20, fontweight="bold", color="#D85A30",
        transform=panel.transAxes,
    )

    source_value = panel.text(
        0.07, 0.08, "",
        fontsize=8, color="#888780",
        transform=panel.transAxes,
    )

    current_scenario_index = 0
    current_bounciness = 0.0
    collision_flash = 0
    score_bar = None

    dt = 1.0 / args.fps
    frames = int(args.seconds * args.fps)

    def update(frame):
        nonlocal current_scenario_index
        nonlocal current_bounciness
        nonlocal collision_flash
        nonlocal score_bar

        axis = ball.step(dt, args.box_size)
        circle.center = ball.pos

        if axis is not None:
            material, surface = SCENARIOS[current_scenario_index]
            current_scenario_index = (
                current_scenario_index + 1
            ) % len(SCENARIOS)

            print(f"\nCollision: {material} × {surface}")

            bounciness, sound, source = ask_jev(
                material, surface
            )

            current_bounciness = bounciness

            # Jev's typed Score becomes actual physics.
            ball.vel[axis] *= -bounciness

            other_axis = 1 - axis
            if abs(ball.vel[other_axis]) < 1.2:
                direction = (
                    1 if ball.vel[other_axis] >= 0 else -1
                )
                ball.vel[other_axis] = direction * 1.2

            collision_flash = 5

            world_text.set_text(
                f"{material.capitalize()}\n"
                f"collides with\n"
                f"{surface}."
            )

            bounce_value.set_text(
                f"{bounciness:.2f}"
            )

            sound_value.set_text(
                sound.upper()
            )

            if source == "JEV":
                source_value.set_text(
                    "● LIVE TYPED RESPONSE FROM JEV"
                )
            else:
                source_value.set_text(
                    "○ FALLBACK — JEV NOT CONNECTED"
                )

            # Replace the score bar.
            if score_bar is not None:
                score_bar.remove()

            score_bar = draw_score_bar(
                panel, 0.07, 0.43, 0.86, current_bounciness
            )

        if collision_flash > 0:
            circle.set_alpha(
                min(1.0, 0.55 + collision_flash * 0.08)
            )
            collision_flash -= 1
        else:
            circle.set_alpha(0.95)

        return [
            circle,
            world_text,
            bounce_value,
            sound_value,
            source_value,
        ]

    print(f"Rendering {frames} frames...")

    anim = animation.FuncAnimation(
        fig,
        update,
        frames=frames,
        interval=1000 / args.fps,
        blit=False,
    )

    anim.save(
        args.out,
        writer=animation.PillowWriter(fps=args.fps),
    )

    plt.close(fig)

    print()
    print("=" * 65)
    print("GIF CREATED:")
    print(os.path.abspath(args.out))
    print("=" * 65)


if __name__ == "__main__":
    main()
