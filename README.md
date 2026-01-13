# NeoCalc Desktop (The "Why Do We Exist" Fork)

Originally created as a simple calculator to teach kids how to program. It was simple. It was pure. It added 2 and 2 and got 4.

But then **I** came along. I saw a perfectly functional teaching tool and thought, "You know what this needs? Unnecessary complexity and a bad attitude." So I forked it, injected it with Rust, and stripped it of its innocence.

## Features
*   **Rust Backend**: Powered by `neocalc-core` via UniFFI for high performance and safety.
*   **Fraction Support**: Toggle between precise fractional (e.g., `1/2`) and decimal (e.g., `0.5`) outputs in Settings.
*   **4 Calculator Modes**: Standard, Scientific, Programming, and Financial.
*   **Responsive Layout**: Optimized for desktop resizing.
*   **Theming Engine**: Import your own `.css` themes (GTK-compatible).
*   **Dark Mode**: By default, because we respect your eyes.

## Flatpak
You can install downloading the flatpak from the release page and running:

```bash
flatpak install ./neocalc.flatpak
```   

## Installation
If you really want to verify that mass times acceleration equals force (or merely a headache):

```bash
# Don't ask me why ABI3 is involved.
PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1 cargo run --manifest-path desktop/Cargo.toml
```

## Theming Guide: How to Create Custom Themes

NeoCalc supports custom themes defined in simple `.css` files. These themes are compatible with the original GTK version of the app.

### How to Import a Theme
1.  Create a `.css` file (e.g., `my-cool-theme.css`).
2.  Open NeoCalc.
3.  Go to Settings or Theme Manager.
4.  Select "Import Theme" and choose your `.css` file.

### CSS Format
The theme parser looks for specific `@define-color` lines.
**Format**: `@define-color KEY #HEXCODE;`

### Theme Keys Reference

| Key | Description |
| :--- | :--- |
| **Window Colors** | |
| `window_bg_color` | Main background color of the app. |
| `window_fg_color` | Default text color. |
| **Number Buttons** | |
| `card_bg_color` | Background for number buttons (0-9). |
| `card_fg_color` | Text color for numbers. |
| **Operator Buttons** | |
| `warning_bg_color` | Background for operators (+, -, /, x). |
| `warning_fg_color` | Text color for operators. |
| **Function Buttons** | |
| `headerbar_bg_color`| Background for functions (Sin, Cos, Log). |
| `headerbar_fg_color`| Text color for functions. |
| **Accent / Equals** | |
| `accent_bg_color` | The "Equals" (=) button background. |
| `accent_fg_color` | Text on the Equals button. |
| **Destructive** | |
| `destructive_bg_color`| Delete / Clear button background. |
| `destructive_fg_color`| Delete / Clear button text. |

### Example Theme (`dracula.css`)

```css
@define-color window_bg_color #282a36;
@define-color window_fg_color #f8f8f2;

@define-color headerbar_bg_color #44475a;
@define-color headerbar_fg_color #f8f8f2;

@define-color card_bg_color #6272a4;
@define-color card_fg_color #f8f8f2;

@define-color accent_bg_color #bd93f9;
@define-color accent_fg_color #282a36;

@define-color warning_bg_color #ffb86c;
@define-color warning_fg_color #282a36;

@define-color destructive_bg_color #ff5555;
@define-color destructive_fg_color #282a36;
```

## Building (For the Masochists)
So you want a standalone binary to cherish forever? Fine.

1. **Install Prerequisites**: You need Rust, GTK4, and Python development headers. Consult your distro's wiki for the specific incantations.
2. **Compile**:
   ```bash
   PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1 cargo build --release --manifest-path desktop/Cargo.toml
   ```
3. **Locate the Artifact**: The binary `neocalc_runner` (or `launcher`) awaits you in `target/release/`. It needs to be run from the root directory so it can find the `python` folder.

## Versioning Scheme
We use a **Date-Based Versioning** scheme to keep things fresh:

`vYEAR.MONTH-REVISION`

*   **YEAR**: The current year (e.g., `2025`).
*   **MONTH**: The current month (e.g., `12`).
*   **REVISION**: An incrementing number for releases within that month (e.g., `1`, `2`, `5`).

## Safety Notice
This calculator assumes no liability for failed math exams or existential crises triggered by its output.

## License

All the code is licensed under the GPLv3 license. You can check under LICENSE file for more details.
