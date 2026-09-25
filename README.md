# JEV Physics Lab

A small physics experiment where **TypeSafe AI's Jev** makes typed decisions that directly control a running physics simulation.

Instead of using a hardcoded restitution value for every collision, the simulation sends the current collision state to Jev and uses its structured response to determine what happens next.

## Demo
---
![Jev Physics Lab Demo](demo/jev_physics_lab.gif)

---

## The Idea

What happens if an AI model doesn't just generate text, but makes a structured decision that directly affects a running program?

In this experiment, every time the ball collides with a surface, the simulation describes the collision to Jev.

For example:

```text
A soap bubble collides with an ice rink.
````

Jev then answers two typed questions:

```text
Bounciness → Score
Sound      → Choice
```

The `bounciness` score becomes the actual restitution value used by the physics simulation.

The `sound` choice becomes part of the collision state displayed in the simulation.

The flow is:

```text
              WORLD STATE
                   │
                   ▼
                  JEV
                   │
          ┌────────┴────────┐
          ▼                 ▼
       SCORE              CHOICE
    Bounciness             Sound
          │                 │
          └────────┬────────┘
                   ▼
                PHYSICS
```

---

## Example

A collision might look like:

```text
Soap bubble × ice rink

Jev decides:

Bounciness → 0.91
Sound      → DING
```

The `0.91` score is then applied directly to the ball's velocity.

A different collision could produce:

```text
Brick × pillow

Bounciness → 0.18
Sound      → THUD
```

The resulting bounce is therefore much weaker.

The important part is that the model's output is not simply displayed as text.

**The output changes the behavior of the program.**

---

## Why Jev?

The experiment explores a simple pattern:

```text
World state
     ↓
Typed model decision
     ↓
Program behavior
```

Instead of asking a model an open-ended question and trying to interpret a block of text, the application defines the decisions it needs and receives structured outputs.

In this demo:

* `Score` controls **how much energy survives the collision**
* `Choice` controls **what sound the collision represents**

This makes the model output directly usable by the application.

---

## What Jev Decides

### 1. Bounciness — Score

Jev evaluates how much of the impact energy should survive as a bounce.

The criteria are:

```text
0 → No bounce, absorbs completely
1 → Partial bounce
2 → Nearly perfectly elastic
```

The returned score is normalized to:

```text
0.0 → 1.0
```

and used as the restitution value in the physics simulation.

### 2. Sound — Choice

Jev chooses from a predefined set of sounds:

```text
thud
splat
ding
boing
pop
```

Each choice has a description that gives Jev context about the intended meaning.

---

## Collision Scenarios

The demo uses different material/surface combinations such as:

```text
Soap bubble × ice rink
Brick × pillow
Super ball × trampoline
Water balloon × concrete floor
Glass ornament × chalkboard
Beach ball × trampoline
Bowling ball × pillow
```

This makes the model's decisions visibly different across collisions.

---

## Tech Stack

* **Python**
* **NumPy** — physics calculations
* **Matplotlib** — simulation and animation
* **Requests** — TypeSafe AI API requests
* **Pillow** — GIF generation
* **TypeSafe AI / Jev** — typed model decisions

---

## Project Structure

```text
jev-physics-lab/
│
├── jev_physics_lab.py
├── README.md
├── requirements.txt
├── .gitignore
│
└── demo/
    └── jev_physics_lab.gif
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/AkshayTripathi4/jev-physics-lab.git
```

Move into the project:

```bash
cd jev-physics-lab
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

---

## API Key Setup

The API key is **not stored in the source code**.

Set it as an environment variable instead.

### Windows PowerShell

```powershell
$env:TYPESAFE_API_KEY="YOUR_API_KEY"
```

### macOS / Linux

```bash
export TYPESAFE_API_KEY="YOUR_API_KEY"
```

> Never commit your API key to GitHub.

---

## Running the Demo

Run with the default configuration:

```bash
python jev_physics_lab.py
```

Generate a 15-second GIF:

```bash
python jev_physics_lab.py --seconds 15 --fps 20
```

Specify an output file:

```bash
python jev_physics_lab.py \
    --seconds 15 \
    --fps 20 \
    --out jev_physics_lab.gif
```

On Windows PowerShell:

```powershell
python jev_physics_lab.py `
    --seconds 15 `
    --fps 20 `
    --out "C:\Users\YourName\Downloads\jev_physics_lab.gif"
```

---

## Command-Line Options

| Option       |               Default | Description                         |
| ------------ | --------------------: | ----------------------------------- |
| `--seconds`  |                  `15` | Duration of the generated animation |
| `--fps`      |                  `20` | Frames per second                   |
| `--box-size` |                  `10` | Size of the physics simulation      |
| `--out`      | `jev_physics_lab.gif` | Output GIF path                     |

Example:

```bash
python jev_physics_lab.py --seconds 20 --fps 24
```

---

## Fallback Mode

The demo can run even when a Jev API key is not configured.

If `TYPESAFE_API_KEY` is unavailable, the program uses deterministic-style fallback behavior based on the material and surface combination.

This allows the physics simulation and GIF generation to be tested without making API requests.

The generated UI indicates when a response came from fallback logic instead of Jev.

For the actual Jev demonstration, configure a valid API key.

---

## Architecture

At a high level, the application works like this:

```text
┌───────────────────────────┐
│      Physics Engine       │
│                           │
│      Ball hits wall       │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│       World State         │
│                           │
│  "Soap bubble collides    │
│       with ice rink"      │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│           Jev             │
│                           │
│   Score + Choice output   │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│     Structured Output     │
│                           │
│   bounciness = 0.91       │
│   sound = "ding"          │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│      Physics Updated      │
│                           │
│   velocity × 0.91         │
└───────────────────────────┘
```

---

## The Interesting Part

The interesting part of this project isn't the physics engine.

The physics itself is intentionally simple.

The experiment is about using a model as a **decision layer inside a software system**.

Instead of:

```text
LLM → text
```

the application uses:

```text
LLM → typed decision → program behavior
```

This pattern can be extended beyond a physics toy to systems where model decisions need to be constrained to a known set of outputs.

---

## Possible Extensions

Some directions for extending the experiment:

* Add more typed decision types
* Let Jev choose different collision reactions
* Add multiple interacting objects
* Add gravity and friction
* Compare Jev-driven physics against fixed physics
* Add an asynchronous decision queue
* Add live sound effects
* Build an interactive browser version
* Add additional model-controlled properties

For example:

```text
Material
    ↓
Jev
    ↓
┌──────────────┬──────────────┬──────────────┐
│ Bounciness   │ Sound        │ Reaction     │
│ Score        │ Choice       │ Choice       │
└──────────────┴──────────────┴──────────────┘
                     ↓
                Simulation
```

---

## Security

Do not hardcode API credentials in the Python source.

Use:

```python
API_KEY = os.environ.get("TYPESAFE_API_KEY")
```

and configure the environment variable locally.

If an API key is accidentally committed to a public repository, revoke/rotate it immediately.

---

## License

This project is intended as a small demonstration and experimentation project.

