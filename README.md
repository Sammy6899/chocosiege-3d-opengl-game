# 🍬 Sugarflare: Candy Kingdom Rescue 🐉✨

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![OpenGL](https://img.shields.io/badge/OpenGL-PyOpenGL-5586A4.svg?logo=opengl&logoColor=white)](https://pyopengl.sourceforge.net/)
[![Course](https://img.shields.io/badge/Course-CSE423%20Computer%20Graphics-red.svg)]()
[![Status](https://img.shields.io/badge/Status-Complete-success.svg)]()

> A 3D real-time interactive action game written in Python using standard OpenGL, GLU, and GLUT pipelines. Guide Sugarflare the dragon through an enchanted confectionery kingdom, overcome caramel and syrup environmental hazards, melt corrupted sweet enemies, gather magic crystals, and defeat the Marshmallow King!

---

## 🎮 Game Controls 🕹️

| Action | Input | Description |
| :--- | :---: | :--- |
| **Move Forward / Backward** | `W` / `S` | Moves dragon along its facing direction (affected by hazards) |
| **Rotate Dragon** | `A` / `D` | Turns the character left or right by 10° increments |
| **Dash Ability** | `SPACE` | Sudden burst of speed forward (has a 2.5s cooldown) |
| **Shoot Fireball** | `Left Click` | Fires offensive heat projectiles (increases Heat bar) |
| **Cycle Camera Mode** | `Right Click` | Toggles between **Third-Person**, **First-Person**, and **Top-Down** |
| **Camera Orbit & Elevation** | `Arrow Keys` | Adjust camera elevation (`Up`/`Down`) & orbit angle (`Left`/`Right`) |
| **Game State Controls** | `ENTER` / `P` / `R` | `ENTER`: Start game; `P`: Toggle Pause; `R`: Reset / Restart |

---

## 🌟 Key Gameplay Features 🎯

- 🐉 **Playable Dragon Mechanics:** Full movement steering, animated flapping wings driven by a sinusoidal clock, an evasive dash mechanic, and an overheating heat meter.
- 🔥 **Multi-Tier Candy Power-Ups:**
  - 🔴 **Red Candy:** Boosts fireball damage to double potency.
  - 🔵 **Blue Candy:** Instant heat cooldown and accelerated cooling rate.
  - 🟢 **Green Candy:** Restores +1 dragon heart/health.
  - 🟡 **Yellow Candy:** Gives a supercharged movement speed boost.
- 🍬 **Enemy AI Archetypes:**
  - 🐻 **Gummy Bears:** Aggressive melee chasers with squash-and-stretch rendering.
  - 💂 **Sugar Guards:** Defensive sentries patrolling designated paths until the player gets close.
  - 🧁 **Marshmallow Spitters:** Ranged enemies that keep distance and fire marshmallow projectiles.
- 🍯 **Dynamic Melting Animation:** Defeated enemies melt flat into the ground using real-time Z-axis matrix scaling before rewarding score points.
- 👑 **Boss Encounter (The Marshmallow King):** Unlocked upon collecting all 3 kingdom crystals; features high health, phase transitions (enrages at $\le 50\%$ HP), and large projectile attacks.
- ⚠️ **Environmental Hazards & Barriers:** Sticky caramel surfaces that reduce movement speed by $55\%$, boiling syrup puddles causing periodic damage, and destructible wafer barriers.

---

## 🛠️ Computer Graphics & Architecture Highlights 📐

This project relies on core OpenGL pipelines and matrix transformations without external game engines:

1. **Hierarchical 3D Modeling:**
   - Primitive composition using `gluSphere`, `glutSolidCube`, and `gluCylinder`.
   - Matrix stack manipulation (`glPushMatrix()` / `glPopMatrix()`) combined with nested `glTranslatef`, `glRotatef`, and `glScalef` for articulated character parts (head, flapping wings, snout, horns, and tail).
2. **Camera Modes & Coordinate Transformations:**
   - Setup using `gluPerspective(72, width/height, 0.1, 2400)`.
   - **Third-Person Follow:** Trig-based offset relative to dragon orientation with adjustable orbit and elevation.
   - **First-Person POV:** Placed directly at the dragon's head coordinates.
   - **Top-Down / Map View:** Orthogonal overhead perspective centered on the player.
3. **Collision Detection & Physics:**
   - **Circle-to-Point Proximity:** Euclidean distance squared checks for projectile hits and item pickups (`near()`).
   - **Axis-Aligned Bounding Box (AABB):** Obstacle, boundary wall, and rectangle hazard checks (`inside()`, `blocked()`).
4. **2D Heads-Up Display (HUD) Projection:**
   - Switches to orthogonal projection via `gluOrtho2D` to render real-time health, heat level, crystal count, objectives, and text alerts using `glutBitmapCharacter`.

---

## 🚀 Installation & Running 💻

### 1️⃣ Clone the Repository
```bash
git clone [https://github.com/YOUR_USERNAME/sugarflare-candy-kingdom-rescue.git](https://github.com/YOUR_USERNAME/sugarflare-candy-kingdom-rescue.git)
cd sugarflare-candy-kingdom-rescue
```

### 2️⃣ Create and Activate a Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

> **Note for Windows Users:** If you encounter `OpenGL.error.NullFunctionError: Attempt to call an undefined function glutInit` install the pre-compiled FreeGLUT binaries via pip:
> ```bash
> pip install PyOpenGL PyOpenGL_accelerate freeglut
> ```

### 4️⃣ Run the Game
```bash
python src/Sugarflare_Candy_Kingdom_Rescue.py
```

---
## 👤 Author & Acknowledgments

- **Developer:** [Sammy6899](https://github.com/Sammy6899)
- **Course:** CSE423 - Computer Graphics
