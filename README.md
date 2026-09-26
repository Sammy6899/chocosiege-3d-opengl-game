# 🍫 Chocosiege: Save The CandyWorld 🍭🏰

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![OpenGL](https://img.shields.io/badge/OpenGL-PyOpenGL-5586A4.svg?logo=opengl&logoColor=white)](https://pyopengl.sourceforge.net/)
[![Course](https://img.shields.io/badge/Course-CSE423%20Computer%20Graphics-red.svg)]()
[![Status](https://img.shields.io/badge/Status-Complete-success.svg)]()

> An interactive 3D multi-stage action-adventure game built with Python, PyOpenGL, GLU, and GLUT without external game engines. Battle hostile snowmen on an infinite runner track, defeat the Chocolate King inside his royal fortress, and navigate an overhead fog-of-war procedural cupcake maze to restore Candyworld!

---

## 🎮 Game Controls 🕹️

### Stages 1 & 2: Forest Trail & Chocolate Kingdom
| Action | Input | Description |
| :--- | :---: | :--- |
| **Change Lanes** | `A` / `D` | Shift left or right across 3 runner lanes (`-150`, `0`, `150`) |
| **Jump** | `SPACE` | Jump upward with kinematic gravity physics to dodge obstacles |
| **Shoot Blaster** | `Left Click` | Fires high-speed fireballs from hero's arm cannon (monitors heat bar) |
| **Camera Angle Orbit** | `Left` / `Right` Arrows | Rotates camera yaw angle around hero |
| **Camera Elevation** | `Up` / `Down` Arrows | Adjusts camera height above track |
| **Cycle Camera POV** | `Right Click` | Toggles between **Third-Person Follow**, **First-Person POV**, and **Top-Down** |
| **Pause / Resume** | `P` | Freezes game state, timers, and animations |
| **Start / Restart** | `ENTER` / `R` | `ENTER`: Start run from title screen; `R`: Reset game state |

### Stage 3: Cupcake Maze Mode
| Action | Input | Description |
| :--- | :---: | :--- |
| **Step Forward / Backward** | `W` / `S` | Moves 1 grid cell relative to facing direction |
| **Turn Left / Right** | `A` / `D` | Rotates heading 90° and steps into adjacent path |
| **Toggle Minimap Map** | `T` or `Right Click` | Switches between close corridor view and overhead tactical view |
| **Map Zoom In / Out** | `Up` / `Down` Arrows | Zooms altitude when in overhead top-down view |

---

## 🗺️ Progression & Game Stages 🏆

1. **Stage 1 — The Forest Trail Runner:**
   - Continuous runner illusion driven by coordinate wrapping and modulo track striping.
   - Dodge marshmallow mounds, collect 12 glowing spinning crystals, and eliminate hostile snowman scouts with your flame blaster.
2. **Stage 2 — The Chocolate Fortress & Boss Arena:**
   - Battle the 30-HP **Chocolate King**.
   - Avoid royal chocolate boulder lane spreads while managing blaster heat accumulation.
   - Defeating the boss triggers an animated portcullis door lift and yields 3 rare gold crystals.
3. **Stage 3 — The Cupcake Maze Escape:**
   - A fully procedural $21 \times 17$ maze rendered as frosted 3D cupcakes.
   - Explored under dynamic **Fog of War** (corridors reveal only as your line-of-sight reaches them).
   - Reach the glowing exit crystal at the far quadrant to trigger the victory sequence!

---

## 🛠️ Computer Graphics Architecture & Highlights 📐

* **Hierarchical Geometric Modeling:**
  - Built from primitive composition using `gluSphere`, `gluCylinder`, and `glutSolidCube`.
  - Articulated character modeling: 3-tier wave-oscillating cape, animated running limbs, rotating snowman horns, and multi-tier frosted cupcake barriers.
* **Kinematics & Smooth Motion:**
  - Quadratic gravity integration for jumping: $z(t) = z_0 + v_0 t - \frac{1}{2}gt^2$.
  - Exponential lerp smoothing for horizontal lane-switching transitions instead of instant teleports.
  - Delta-time ($\Delta t$) clamping via `time.monotonic()` to maintain stable frame rates across displays.
* **Camera Transformations & Viewports:**
  - **Dynamic Frustum:** Configured via `gluPerspective(72, width/height, 0.1, 4500)`.
  - **LookAt Matrix:** Positions camera dynamically relative to target coordinates using trigonometric spherical offsets.
  - **Windows Client Area Resizing:** Uses `ctypes.windll.user32` to dynamically recalculate projection aspect ratios when resizing.
* **Procedural Algorithms & Optimization:**
  - **DFS Backtracking Maze:** Builds a perfect maze from solid blocks, followed by cycle-braiding to introduce alternate paths.
  - **Painter's Algorithm & Distance Culling:** Sorts maze walls from back-to-front by distance to the camera before drawing to optimize rasterization.
  - **Fog of War Raycasting:** Casts 4-directional cardinal line-of-sight checks to uncover maze cells in real time.
* **Screen-Space HUD:**
  - Temporarily swaps `GL_PROJECTION` to `gluOrtho2D(0, width, 0, height)` to render 2D text overlays (health, heat, crystals, and radar angles) with `glutBitmapCharacter`.

---

## 🚀 Installation & Running 💻

### 1️⃣ Clone the Repository
```bash
git clone [https://github.com/YOUR_USERNAME/chocosiege-save-the-candyworld.git](https://github.com/YOUR_USERNAME/chocosiege-save-the-candyworld.git)
cd chocosiege-save-the-candyworld
```

### 2️⃣ Set Up Virtual Environment
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

> **Note for Windows Users:** If you run into `OpenGL.error.NullFunctionError: Attempt to call an undefined function glutInit`[cite: 7], install pre-compiled FreeGLUT binaries:
> ```bash
> pip install PyOpenGL PyOpenGL_accelerate freeglut
> ```

### 4️⃣ Launch Game
```bash
python src/Chocosiege-SaveTheCandyWorld.py
```

---

## 👤 Author & Acknowledgments

- **Developer:** [Sammy6899](https://github.com/Sammy6899)
- **Course:** CSE423 - Computer Graphics
