# Changelog

## v2026.2-2

### Refactoring
- **Grids**: Deduplicated initialization logic in `CalculatorGrid` and its subclasses. Moved homogeneity settings to the base class and removed redundant imports.
- **Comments**: Conducted a deep clean of code comments. Removed stale development notes and added comprehensive architectural explanations to `backend.py`, `main_window.py`, `calculator.py`, and `base.py`.

### UI Polish
- **Header**: Centered the calculator mode selector.
- **Icons**: Updated the Financial mode icon to `network-cellular-signal-excellent-symbolic`.

### Build System
- **Windows**: Fixed build failures in `binaries_build.yml` by implementing dynamic Python version detection, safer dependency scanning, and conditional locale copying.
- **Flatpak**: Improved distribution pipeline with persistent repository, GPG signing support, delta updates, and `.flatpakrepo` file for easy installation.

### Backend Improvements
- **Safety**: Added factorial input limit (max 10,000) to prevent UI hangs.
- **Formatting**: Improved `format_float` to trim trailing zeros and added `format_number_decimal` for decimal display mode.
- **Cleanup**: Removed dead `DivisionByZero` error, unused `use_decimals` field, and fixed stress test warnings.


