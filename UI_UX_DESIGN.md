**FitAssist**

**UI/UX Design Document**

*The High-Performance Hub*

Design Concept \| v1.0 \| March 2026

  --------------------- -------------------------------------------------
  Project               FitAssist --- The Daily Fitness Personal Trainer
                        App

  Design Concept        The High-Performance Hub

  Design Philosophy     Data-First --- A cockpit dashboard for personal
                        fitness

  Visual Style          Deep Space Minimalism + Glassmorphism-Lite

  Primary Background    #101014 (Deep Space Black)

  Primary Accent        #00E8FF (Neon Cyan)

  Platform              Mobile App --- Android (APK) + iOS (Expo Go)

  Reference Kit         Goals --- Fitness App UI Kit (Figma Community,
                        Free)

  Author                Pratham (Tech Lead)

  Version               1.0

  Status                Design Baseline --- Ready for Antigravity
                        Implementation
  --------------------- -------------------------------------------------

# 1. Design Philosophy

FitAssist\'s interface is built around one core metaphor: a cockpit
dashboard. Every screen is designed to feel authoritative, energizing,
and data-forward --- like high-end gym equipment brought to a mobile
screen. The user should feel in control and motivated the moment they
open the app.

  -----------------------------------------------------------------------
  **Principle**         **Value**
  --------------------- -------------------------------------------------
  Design Name           The High-Performance Hub

  Core Metaphor         Cockpit Dashboard --- clean, authoritative,
                        energizing

  Visual Language       Deep Space Minimalism --- dark backgrounds, neon
                        precision accents

  Target Emotion        Empowered, focused, and motivated

  Data Presentation     Health metrics treated like instrument readings
                        --- precise and prominent

  Interaction Feel      Crisp, high-contrast, haptic --- mimics high-end
                        gym equipment interfaces
  -----------------------------------------------------------------------

# 2. Color System

The color system is minimal and intentional. Neon Cyan (#00E8FF) is
reserved exclusively for action and insight --- interactive elements,
progress indicators, and critical health data. Everything else recedes
into the dark background, ensuring maximum visual hierarchy.

  --------------------------------------------------------------------------
  **Swatch**   **Hex Code**  **Name**      **Usage in FitAssist**
  ------------ ------------- ------------- ---------------------------------
               **#101014**   **Deep Space  Primary background --- all
                             Black**       screens

               **#1A1A1E**   **Card Dark** Glassmorphism cards, input
                                           fields, bottom nav bar

               **#00E8FF**   **Neon Cyan** CTA buttons, progress bars,
                                           active nav icons, key metrics,
                                           glow effects

               **#FFFFFF**   **Pure        Primary body text, exercise
                             White**       names, headings on dark
                                           backgrounds

               **#A0A0B0**   **Mid Grey**  Secondary text, labels,
                                           placeholder text, inactive nav
                                           icons

               **#1C3A3E**   **Teal        Gradient endpoint for charts and
                             Shadow**      activity visualizations (cyan →
                                           teal)

               **#FF4C4C**   **Alert Red** Caution warning chips on
                                           high-risk exercises

               **#FFB800**   **Amber**     Quick fix tips, rest day
                                           indicators, moderate-risk flags

               **#2ECC71**   **Success     Successful plan generation,
                             Green**       completed workout day indicators
  --------------------------------------------------------------------------

## 2.1 Color Usage Rules

-   Neon Cyan is used ONLY for interactive, actionable, or critical data
    elements --- never decorative

-   Never use Cyan as a background fill --- only as text, borders,
    glows, or progress indicators

-   White text on #101014 background is the default for all readable
    content

-   Alert Red (#FF4C4C) appears only on the caution warning chip ---
    never elsewhere

-   Gradients always run from Neon Cyan (#00E8FF) to Teal Shadow
    (#1C3A3E) --- never reversed

# 3. Typography

Typography uses a single bold sans-serif family throughout. Scale is
aggressive --- large, confident numbers for metrics, clean readable
sizes for instructions, and minimal use of mixed weights to avoid visual
noise.

  ----------------------------------------------------------------------------
  **Role**        **Font**        **Size**   **Usage & Color**
  --------------- --------------- ---------- ---------------------------------
  Display / Hero  Inter Bold or   72--96sp   Metric readouts (rep counters,
                  SF Pro Display             timers) --- Neon Cyan
                  Bold                       

  Screen Title    Inter Bold      28--32sp   Screen headers --- Pure White

  Section Heading Inter SemiBold  20--22sp   Card titles, module labels ---
                                             Pure White

  Body / Card     Inter Regular   15--16sp   Exercise instructions,
  Text                                       descriptions --- White / Mid Grey

  Label / Caption Inter Medium    12--13sp   Tags, chips, badges, metadata ---
                                             Mid Grey

  CTA Button Text Inter Bold      16sp       Button labels --- Deep Space
                                             Black (#101014) on Cyan fill

  Code / Data     JetBrains Mono  14sp       Calorie numbers, macro values ---
                  or SF Mono                 Neon Cyan
  ----------------------------------------------------------------------------

## 3.1 Typography Rules

-   Active workout timers and rep counters are always rendered in
    Display size (72--96sp) in Neon Cyan --- must remain readable during
    high-intensity movement

-   Never mix more than 2 font weights on a single screen

-   Line height should be 1.5x font size for body text, 1.2x for
    headings

-   All text must pass WCAG AA contrast ratio on #101014 background

# 4. Component Library

All UI components follow the \'Data-First\' design language --- sharp,
functional, and purposeful. No decorative elements that don\'t carry
information.

## 4.1 Glassmorphism-Lite Cards

Cards are the primary container for all content --- workouts, meals,
metrics, and settings.

  -----------------------------------------------------------------------
  **Property**          **Value**
  --------------------- -------------------------------------------------
  Background            #1A1A1E (Card Dark)

  Border                1px solid rgba(0, 232, 255, 0.15) --- dimmed cyan

  Border Radius         12dp

  Shadow                0px 4px 24px rgba(0, 232, 255, 0.06) --- subtle
                        cyan glow

  Padding               16dp horizontal, 14dp vertical

  Usage                 Exercise cards, meal cards, metric cards,
                        onboarding option cards
  -----------------------------------------------------------------------

## 4.2 CTA Buttons --- Primary

Primary actions like \'Generate My Plan\', \'Start Workout\', \'Save
Profile\'.

  -----------------------------------------------------------------------
  **Property**          **Value**
  --------------------- -------------------------------------------------
  Background            #00E8FF (Neon Cyan)

  Text                  Bold, 16sp, #101014 (Deep Space Black)

  Border Radius         8dp (sharp, not pill-shaped)

  Height                52dp minimum for touch accessibility

  Pressed State         Scale to 0.97 + brightness reduction to 80%

  Loading State         Cyan spinner centered, button text hidden

  Disabled State        Background: #1A1A1E, Text: Mid Grey --- no cyan
  -----------------------------------------------------------------------

## 4.3 Secondary / Ghost Buttons

  -----------------------------------------------------------------------
  **Property**          **Value**
  --------------------- -------------------------------------------------
  Background            Transparent

  Border                1px solid #00E8FF

  Text                  SemiBold, 15sp, #00E8FF

  Border Radius         8dp

  Usage                 Regenerate Plan, Skip, Cancel actions
  -----------------------------------------------------------------------

## 4.4 Circular Progress Bars --- Glow Effect

Used on the Dashboard for step counts, calorie burns, and workout
completion.

  -----------------------------------------------------------------------
  **Property**          **Value**
  --------------------- -------------------------------------------------
  Track Color           #1A1A1E (Card Dark)

  Progress Color        #00E8FF (Neon Cyan)

  Glow                  Drop shadow: 0px 0px 12px rgba(0,232,255,0.6) on
                        the progress arc

  Size                  120dp diameter for dashboard, 64dp for compact
                        cards

  Center Text           Display size font --- metric value in Cyan, unit
                        label in Mid Grey below

  Animation             Ease-in-out fill from 0 on screen enter --- 600ms
                        duration
  -----------------------------------------------------------------------

## 4.5 Caution Warning Chip

Appears on exercise cards for moderate/high-risk exercises (FR-025,
FR-026).

  -----------------------------------------------------------------------
  **Property**          **Value**
  --------------------- -------------------------------------------------
  Background            #FF4C4C at 15% opacity (#1A1414 tint)

  Border                1px solid #FF4C4C

  Icon                  ⚠ warning icon in #FF4C4C, 14sp

  Text                  Caption size, #FF4C4C --- caution message from AI
                        JSON

  Expanded State        Amber (#FFB800) quick fix tip revealed below with
                        a 1px amber left border

  Border Radius         6dp

  Tap Behaviour         Tapping chip toggles quick fix expansion ---
                        smooth 200ms height animation
  -----------------------------------------------------------------------

## 4.6 Bottom Navigation Bar

  -----------------------------------------------------------------------
  **Property**          **Value**
  --------------------- -------------------------------------------------
  Background            #1A1A1E with frosted glass blur effect
                        (backdrop-filter: blur 12px)

  Height                64dp + safe area inset

  Icons                 24dp outline icons --- inactive state: Mid Grey
                        (#A0A0B0)

  Active State          Icon in Neon Cyan + 2dp Cyan underline bar below
                        icon

  Active Glow           Soft outer glow: 0px 0px 8px rgba(0,232,255,0.4)
                        on active icon

  Tabs                  Home, Workout, Nutrition, Profile (4 tabs)

  Border                1px top border: rgba(0,232,255,0.12)
  -----------------------------------------------------------------------

## 4.7 Input Fields --- Onboarding

  -----------------------------------------------------------------------
  **Property**          **Value**
  --------------------- -------------------------------------------------
  Background            #1A1A1E

  Border (default)      1px solid rgba(255,255,255,0.08)

  Border (focused)      1px solid #00E8FF + subtle cyan glow

  Text                  White, 16sp, Inter Regular

  Placeholder           Mid Grey, 15sp

  Border Radius         8dp

  Height                52dp
  -----------------------------------------------------------------------

## 4.8 Selection Cards --- Onboarding Options

Used for goal selection, fitness level, equipment, days per week, and
duration.

  -----------------------------------------------------------------------
  **Property**          **Value**
  --------------------- -------------------------------------------------
  Default State         Card Dark background (#1A1A1E), dimmed cyan 1px
                        border, White label text

  Selected State        Cyan border 2px + Cyan background at 8% opacity +
                        Checkmark icon in Cyan

  Border Radius         10dp

  Icon                  Category icon in Mid Grey (default) → Neon Cyan
                        (selected)

  Animation             Border and fill transition at 150ms ease

  Layout                2-column grid for most options, single column for
                        duration/days
  -----------------------------------------------------------------------

# 5. Screen-by-Screen Design Specifications

Each screen is mapped to its module from the FitAssist Module Map. All
screens use #101014 as the base background unless stated otherwise.

## 5.1 Auth Screens (Module 1)

  -----------------------------------------------------------------------
  **Splash Screen**

  -----------------------------------------------------------------------

-   Full #101014 background

-   FitAssist wordmark centered --- white, bold, Display size

-   Neon Cyan tagline below: \'Your AI Personal Trainer\' in 18sp

-   Subtle cyan glow pulse animation on the logo --- 1.5s loop

-   Auto-navigate to Login or Onboarding after 2 seconds

  -----------------------------------------------------------------------
  **Sign Up / Login Screen**

  -----------------------------------------------------------------------

-   Screen title: \'Welcome Back\' (login) / \'Let\'s Get Started\'
    (signup) --- 28sp bold white

-   Email + Password input fields --- onboarding style (Section 4.7)

-   Primary CTA: \'Sign In\' / \'Create Account\' --- full-width Cyan
    button

-   Toggle link: \'Don\'t have an account? Sign Up\' --- Mid Grey, Cyan
    on the action word

-   No social login at MVP --- email/password only

## 5.2 Onboarding Screens (Module 2)

  -----------------------------------------------------------------------
  **Flow: 5-step card selector sequence**

  -----------------------------------------------------------------------

-   Progress indicator at top: 5 dots --- active dot in Cyan, inactive
    in Card Dark with dim border

-   Each screen: large bold question header (22sp) + selection cards in
    2-column grid

-   Selected option highlights with Cyan border + 8% fill + checkmark
    (Section 4.8)

-   \'Continue\' CTA always fixed at bottom --- Cyan primary button

-   Back arrow top-left in Mid Grey

**Step Sequence:**

-   Step 1 --- What\'s your goal? (Weight Loss / Muscle Gain / General
    Fitness / Flexibility)

-   Step 2 --- Your fitness level? (Beginner / Intermediate / Advanced)

-   Step 3 --- Available equipment? (None / Dumbbells / Full Gym /
    Resistance Bands)

-   Step 4 --- How many days per week? (2 / 3 / 4 / 5 --- shown as
    number cards)

-   Step 5 --- Preferred session duration? (20 / 30 / 45 / 60 min)

-   Optional Step --- Age & Weight (skippable with \'Skip for now\'
    ghost button)

## 5.3 Plan Generation Screen (Module 3)

  -----------------------------------------------------------------------
  **Loading State**

  -----------------------------------------------------------------------

-   Full dark screen --- centered content

-   Large animated Cyan circular spinner (80dp)

-   Rotating messages below spinner in 16sp Mid Grey:

```{=html}
<!-- -->
```
-   \"Analysing your profile\...\"

-   \"Building your 7-day plan\...\"

-   \"Crafting your meal plan\...\"

-   \"Warming up server\...\" --- shown only on first request (Render
    cold start)

```{=html}
<!-- -->
```
-   Each message fades in/out every 2.5 seconds

  -----------------------------------------------------------------------
  **Error State**

  -----------------------------------------------------------------------

-   Alert Red icon (⚠) centered, 48dp

-   Error message in white: \'Something went wrong. Please try again.\'

-   \'Retry\' primary Cyan button below

## 5.4 Workout Plan Display (Module 4)

  -----------------------------------------------------------------------
  **7-Day Plan Screen**

  -----------------------------------------------------------------------

-   Screen title: \'Your 7-Day Plan\' --- 28sp bold white

-   Horizontal day selector strip at top --- 7 day pills (Day 1--7)

```{=html}
<!-- -->
```
-   Active day: Cyan fill + Black text

-   Today marker: small Cyan dot below the pill

-   Rest day: Mid Grey fill + \'Rest\' label

```{=html}
<!-- -->
```
-   Plan name displayed as a subtitle below day selector --- Mid Grey,
    14sp italic

  -----------------------------------------------------------------------
  **Exercise Card**

  -----------------------------------------------------------------------

-   Glassmorphism-Lite card (Section 4.1) for each exercise

-   Exercise name: Section Heading size, White, bold

-   Stats row: \[Sets × Reps\] \[Rest: Xs\] --- displayed as
    Cyan-bordered mini chips

-   Instructions: Body text, Mid Grey, 15sp --- collapsed by default

-   Expand arrow (chevron) on right --- rotates 180° on tap to show full
    instructions

-   Caution chip (if applicable): Alert Red --- Section 4.5 spec

-   Quick fix (if applicable): Amber --- revealed on caution chip tap

  -----------------------------------------------------------------------
  **Rest Day Card**

  -----------------------------------------------------------------------

-   Full-width card with Amber (#FFB800) left border accent

-   Large \'Rest Day 🌙\' heading in white

-   Subtext: \'Recovery is part of the plan. Let your muscles rebuild.\'
    --- Mid Grey

## 5.5 Nutrition Display (Module 5)

  -----------------------------------------------------------------------
  **Daily Meal Plan Screen**

  -----------------------------------------------------------------------

-   Screen title: \'Your Nutrition Plan\' --- 28sp bold white

-   Daily calorie target displayed prominently --- Cyan circular
    progress bar at top (Section 4.4)

```{=html}
<!-- -->
```
-   Center: target kcal in Display size Cyan, \'DAILY TARGET\' label in
    Mid Grey below

```{=html}
<!-- -->
```
-   Macro breakdown bar below the circle --- horizontal 3-part bar:

```{=html}
<!-- -->
```
-   Protein: Neon Cyan fill

-   Carbs: Desaturated teal (#4ABFCC)

-   Fats: Dimmed blue-grey (#6A8FA0)

-   Labels below each segment with grams value

```{=html}
<!-- -->
```
-   4 meal cards below --- Breakfast, Lunch, Dinner, Snack

```{=html}
<!-- -->
```
-   Each card: meal name in white bold + description in Mid Grey +
    approx kcal in Cyan on right

-   Neon glow icon per meal type (☀ Breakfast, 🌤 Lunch, 🌙 Dinner, ⚡
    Snack)

  -----------------------------------------------------------------------
  **Nutrition Tips Section**

  -----------------------------------------------------------------------

-   3 tip cards below meals --- each with a left 2px Cyan border accent

-   Tip text in white 15sp, icon prefix in Cyan

## 5.6 Profile / Settings Screen (Module 2 + Module 6)

-   User avatar placeholder (initials in Cyan circle)

-   Fitness goal + level displayed as Cyan-bordered tags

-   \'Regenerate Plan\' ghost button --- full width, Cyan border

-   Rate limit indicator: \'Plan generations today: X/2\' --- Mid Grey
    label, Cyan progress dots

-   Settings list --- dark rows with right chevron, Mid Grey labels,
    Cyan toggle for active states

# 6. Screen Navigation Flow

The complete user journey from first open to viewing their plan:

  -----------------------------------------------------------------------
  **Screen**               **Navigation**
  ------------------------ ----------------------------------------------
  Splash Screen            Auto-advance after 2s → checks auth token

  → Login / Sign Up        New user → Sign Up → Onboarding Step 1

  → Onboarding (5 steps)   Completes all steps → Generate Plan screen

  → Plan Generation        API call in progress → success or error
  Loading                  

  → Workout Plan Display   7-day plan rendered → user taps exercises

  → Nutrition Plan Display Bottom nav Nutrition tab → meal plan

  → Profile Screen         Bottom nav Profile tab → settings, regenerate

  Returning User           App open → auth token valid → direct to
                           Workout Plan screen
  -----------------------------------------------------------------------

# 7. Data Visualization Specs

Charts and visualizations follow the \'flow and momentum\' principle ---
gradients represent energy, not just data.

## 7.1 Activity / Progress Charts

  -----------------------------------------------------------------------
  **Property**          **Value**
  --------------------- -------------------------------------------------
  Chart Type            Linear area chart (weekly workout completion)

  Line Color            #00E8FF --- 2px stroke

  Fill Gradient         Linear: rgba(0,232,255,0.4) at top →
                        rgba(0,232,255,0.0) at bottom

  Grid Lines            Horizontal only --- rgba(255,255,255,0.04) ---
                        barely visible

  Axis Labels           Mid Grey, 11sp, JetBrains Mono

  Data Points           4dp Cyan filled circle with white 1px border

  Animation             Line draws left to right on screen enter ---
                        800ms ease-in-out
  -----------------------------------------------------------------------

## 7.2 Macro Breakdown Bar

  -----------------------------------------------------------------------
  **Property**          **Value**
  --------------------- -------------------------------------------------
  Type                  Horizontal segmented bar, full width, 12dp height

  Border Radius         6dp on outer edges only

  Segment Gap           2dp gap between segments

  Protein Segment       #00E8FF (Neon Cyan)

  Carbs Segment         #4ABFCC (Desaturated Teal)

  Fats Segment          #6A8FA0 (Dimmed Blue-Grey)

  Labels                Below each segment --- nutrient name + grams
                        value, 11sp Mid Grey

  Animation             Segments fill from left on screen enter --- 500ms
                        ease
  -----------------------------------------------------------------------

# 8. Spacing, Grid & Motion

## 8.1 Spacing System

FitAssist uses an 8dp base grid. All spacing values are multiples of 8.

  -----------------------------------------------------------------------
  **Token**             **Value**
  --------------------- -------------------------------------------------
  Base Unit             8dp

  Screen Padding        16dp horizontal (2 units) on all screens

  Card Gap              12dp between cards

  Section Gap           24dp between major sections

  Inner Card Pad        16dp horizontal, 14dp vertical

  Icon Size             24dp standard, 48dp hero states

  Touch Target          Minimum 48×48dp for all interactive elements
                        (WCAG AA)
  -----------------------------------------------------------------------

## 8.2 Border Radius

  -----------------------------------------------------------------------
  **Element**           **Radius**
  --------------------- -------------------------------------------------
  Buttons               8dp --- sharp, functional, gym-equipment feel

  Cards                 12dp

  Input Fields          8dp

  Chips / Tags          6dp

  Bottom Nav Bar        0dp top --- flush edge to screen

  Circular Elements     50% (fully round)
  -----------------------------------------------------------------------

## 8.3 Motion & Animation

  -----------------------------------------------------------------------
  **Element**            **Animation Spec**
  ---------------------- ------------------------------------------------
  Screen Transitions     Slide up from bottom --- 280ms ease-in-out

  Card Appear            Fade in + translate Y 12dp up --- 300ms
                         staggered (80ms delay per card)

  Button Press           Scale 0.97 + brightness 80% --- 100ms

  Progress Bars/Rings    Fill animation from 0 --- 600ms ease-in-out on
                         screen enter

  Caution Chip Expand    Height animation --- 200ms ease

  Onboarding Card Select Border + fill transition --- 150ms ease

  Loading Spinner        Continuous 360° rotation --- 1000ms linear loop
  -----------------------------------------------------------------------

# 9. Implementation Notes for Antigravity

When feeding this document to Antigravity as context, these are the most
important directives to include in your natural language instructions:

-   Always use #101014 as the root background color --- never white or
    light grey

-   Neon Cyan (#00E8FF) is the ONLY accent color --- no other colors for
    interactive elements

-   All cards use #1A1A1E background with a 1px rgba(0,232,255,0.15)
    border --- this is glassmorphism-lite

-   Bottom navigation has 4 tabs: Home, Workout, Nutrition, Profile

-   Exercise cards must include the caution chip component --- it is a
    Must Have feature (FR-025, FR-026)

-   The plan generation loading screen rotates through 4 messages ---
    not a static spinner

-   All touch targets must be minimum 48×48dp --- accessibility is
    non-negotiable

-   Border radius is consistently 8dp for buttons and inputs, 12dp for
    cards --- never pill-shaped buttons

-   Typography uses Inter font family throughout --- no serifs, no
    decorative fonts

-   Animations are purposeful, not decorative --- every animation
    communicates state change

## 9.1 React Native / Expo Implementation Tips

  -----------------------------------------------------------------------
  **Element**           **Implementation**
  --------------------- -------------------------------------------------
  Dark Background       Use backgroundColor: \'#101014\' on root View and
                        NavigationContainer

  Glassmorphism Cards   backgroundColor: \'#1A1A1E\' + borderWidth: 1 +
                        borderColor: \'rgba(0,232,255,0.15)\'

  Glow Effects          Use shadowColor: \'#00E8FF\' + shadowOpacity:
                        0.4 + elevation on Android

  Circular Progress     react-native-svg or expo\'s SVG --- draw arc with
                        stroke color #00E8FF

  Bottom Nav            React Navigation Bottom Tabs --- custom tabBar
                        with frosted glass style

  Animations            React Native Animated API or Reanimated v2 for
                        performance

  Font Loading          expo-font to load Inter and JetBrains Mono from
                        Google Fonts

  Haptics               expo-haptics ---
                        impactAsync(ImpactFeedbackStyle.Light) on button
                        press
  -----------------------------------------------------------------------

*FitAssist Design Document v1.0 \| The High-Performance Hub \| Pratham
\| March 2026 \| Open Source --- MIT License*
