# Creating Themes for NeoCalc

NeoCalc supports custom theming through CSS files. This guide will help you create your own themes.

## Theme Location

All theme files are located in:
`python/neocalc/styling/themes/`

## How to Create a New Theme

1. Cannot create a new file in the themes directory with a `.css` extension, e.g., `my-cool-theme.css`.
2. Define the required color variables.
3. (Optional) Override specific CSS classes if you need more granular control.
4. Restart NeoCalc to see your theme in the settings menu.

## Required Variables

NeoCalc uses GTK's named colors mechanism. You should define the following colors at the top of your CSS file using the `@define-color` syntax.

| Variable | Description |
|----------|-------------|
| `window_bg_color` | Main window background color |
| `window_fg_color` | Main window text color |
| `accent_bg_color` | Primary accent color (used for suggested actions, active states) |
| `accent_fg_color` | Text color on top of the accent background |
| `destructive_bg_color` | Color for destructive actions (e.g., Clear All) |
| `destructive_fg_color` | Text color on top of destructive background |
| `headerbar_bg_color` | Background for the top header bar |
| `headerbar_fg_color` | Text/Icon color for the header bar |
| `headerbar_border_color` | Border color separating header from content |
| `popover_bg_color` | Background for dropdowns and popups |
| `popover_fg_color` | Text color for dropdowns and popups |
| `view_bg_color` | Background for the main view content |
| `view_fg_color` | Text color for the main view |
| `card_bg_color` | Background for cards (grouped content) |
| `card_fg_color` | Text color for cards |

### Example Template

```css
/* My Cool Theme */

@define-color window_bg_color #1e1e2e;
@define-color window_fg_color #cdd6f4;

@define-color accent_bg_color #cba6f7;
@define-color accent_fg_color #1e1e2e;
@define-color destructive_bg_color #f38ba8;
@define-color destructive_fg_color #1e1e2e;

@define-color headerbar_bg_color #181825;
@define-color headerbar_fg_color #cdd6f4;
@define-color headerbar_border_color #313244;
@define-color headerbar_backdrop_color @window_bg_color;
@define-color headerbar_shade_color rgba(0, 0, 0, 0.36);

@define-color popover_bg_color #1e1e2e;
@define-color popover_fg_color #cdd6f4;

@define-color view_bg_color #1e1e2e;
@define-color view_fg_color #cdd6f4;

@define-color card_bg_color #313244;
@define-color card_fg_color #cdd6f4;
@define-color card_shade_color rgba(0, 0, 0, 0.36);
```

## Styling Specific Components

You can style specific parts of the UI using standard CSS selectors.

### Calculator Grid Buttons

The buttons in the keypad use the `.calc-grid-button` class.

```css
.calc-grid-button {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
}

.calc-grid-button:hover {
    background-color: #45475a;
}

.calc-grid-button:active {
    background-color: @accent_bg_color;
    color: @accent_fg_color;
}
```

### Accented Buttons

Operators often use the `.accent` class.

```css
.calc-grid-button.accent {
    background-color: @accent_bg_color;
    color: @accent_fg_color;
}

.calc-grid-button.accent:hover {
    filter: brightness(1.1);
}
```

### Sidebar

The sidebar (history/variables) uses `.sidebar`.

```css
.sidebar {
    background-color: @headerbar_bg_color;
    border-right: 1px solid @headerbar_border_color;
}
```

## Import Feature

Users can also import themes directly via the application menu ("Import Theme"). This copies the `.css` file into the themes directory automatically.
