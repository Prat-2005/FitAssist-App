# Design System Document: Deep Space Minimalism

## 1. Overview & Creative North Star
**Creative North Star: "The Kinetic Observatory"**

This design system is engineered to feel like a high-precision flight deck. We are moving away from the "friendly fitness coach" trope and toward a high-performance, data-centric interface that demands excellence. The aesthetic—Deep Space Minimalism—relies on the tension between the infinite void of the background (`surface`) and the piercing precision of the neon accents (`primary_container`). 

To break the "template" look, we utilize **intentional asymmetry**. Do not center-align everything. Use wide gutters and left-aligned, aggressive typography to create a sense of forward motion. Elements should feel like they are floating in a vacuum, held together by gravitational hierarchy rather than rigid boxes.

---

## 2. Colors & Surface Architecture

### Palette Roles
- **The Void (Primary Background):** Use `#131317` (`surface`) as the base. It is not pure black, allowing for "true black" shadows to create depth.
- **Neon Precision (Accent):** `#00E8FF` (`primary_container`) is reserved strictly for interactive states, progress metrics, and critical data points. Use it sparingly to maintain its "glow" impact.
- **Muted Tech (Secondary):** `#97d0d9` (`secondary`) is used for non-critical interactive elements to prevent visual fatigue.

### The "No-Line" Rule
Sectioning must be achieved through tonal shifts, never 1px solid lines. To separate a workout summary from the main feed, shift the background from `surface` to `surface_container_low`. 

### Surface Hierarchy & Nesting
Treat the UI as a series of stacked panels. 
1.  **Base Layer:** `surface` (#131317)
2.  **Sectional Layer:** `surface_container_low` (#1b1b1f)
3.  **Interactive Cards:** `surface_container` (#1f1f23)
4.  **Floating Modals:** `surface_bright` (#39393d)

### The "Glass & Gradient" Rule
For hero elements (e.g., your current heart rate or PR), use a glassmorphism effect: 
- **Fill:** `surface_container` at 60% opacity.
- **Backdrop Blur:** 12px to 20px.
- **Edge:** See "Ghost Borders" in Section 4.
- **Gradients:** Use a linear gradient from `primary_container` (#00E8FF) to `primary_fixed_dim` (#00daf0) at a 135-degree angle for primary CTA buttons to give them a "charged" energy.

---

## 3. Typography: The "Inter" Engine
We use **Inter** exclusively to maintain a utilitarian, Swiss-inspired tech aesthetic.

- **The Metric Aggression (Display-LG/MD):** Used for weights, reps, and timers. Set to **Bold (700)** or **Black (900)**. Letter spacing should be set to `-0.02em` to feel tighter and more industrial.
- **The Instruction (Body-LG/MD):** Used for workout descriptions. Set to **Regular (400)** with increased line-height (1.6) to ensure maximum readability during high-intensity movement.
- **The Technical Label (Label-MD/SM):** All-caps, **Medium (500)** weight, with `+0.05em` letter spacing. Use these for category tags or secondary data units (e.g., "KCAL" or "BPM").

---

## 4. Elevation & Depth

### The Layering Principle
Hierarchy is created by "lifting" colors. A "Selected" workout state shouldn't just have a border; it should transition from `surface_container` to `surface_container_high`.

### Ambient Shadows
Forget heavy shadows. Use "Vacuum Shadows":
- **Color:** `#000000` at 40% opacity.
- **Blur:** 30px to 40px.
- **Spread:** -5px (to keep the shadow tucked under the element, simulating a float rather than a drop).

### The "Ghost Border" Fallback
If a boundary is required for a card, use a 1px border with `outline_variant` (#3b494c) at **15% opacity**. This creates a "cyan-tinted glass edge" that catches the light without boxing in the content.

### Glassmorphism Depth
Apply `backdrop-filter: blur(10px)` to any element using the `surface_container_low` or `medium` tokens when they overlay the base `surface`. This ensures the "Deep Space" feel is maintained as the user scrolls.

---

## 5. Components

### Buttons (Sharp & Functional)
- **Primary:** `primary_container` background, `on_primary_container` text. **Radius: 8dp (`lg`)**. No pill shapes.
- **Secondary:** `surface_container_high` background with a `Ghost Border`.
- **Tertiary:** Text-only in `primary_fixed_dim`, all caps, bold.

### Cards & Data Modules
- **Rule:** Never use dividers. Use `2.5rem` (`10`) of vertical space between content groups.
- **Radius:** **12dp (`xl`)**.
- **Interaction:** On tap/press, a card should scale down to 0.98 and increase in brightness to `surface_bright`.

### Performance Inputs
- **Text Fields:** `surface_container_lowest` background. 1px `Ghost Border`. **8dp (`lg`)** radius. Focus state: Border opacity increases to 100% using `primary_container` color.
- **Selection Chips:** Rectangular, never rounded. Use `surface_container_high` for unselected and `primary_container` for selected.

### Signature Component: The "Precision Pulse"
A custom progress bar using `primary_container`. Instead of a smooth fill, use a repeating pattern of 2px vertical gaps every 8px to mimic a digital readout or telemetry scale.

---

## 6. Do's and Don'ts

### Do
- **Do** embrace the void. Negative space is your strongest tool for focus.
- **Do** use aggressive type scales (e.g., jumping from `label-sm` directly to `display-lg`) to highlight key data.
- **Do** use crisp, high-haptic feedback triggers for every button press.

### Don't
- **Don't use pill shapes.** Every corner must be an 8dp or 12dp radius to maintain the aggressive, high-performance tone.
- **Don't use 100% white (#FFFFFF).** Use `on_surface` (#e4e1e7) for text to prevent "retina burn" against the dark background.
- **Don't use standard dividers.** If you can't separate it with space or a color shift, rethink the layout hierarchy.