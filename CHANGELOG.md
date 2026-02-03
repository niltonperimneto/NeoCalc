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
- **Synchronization**: Updated backend submodule to latest commit (dd543a4), incorporating upstream variable scoping refactors and number formatting unification.
- **Bindings**: Updated Python bindings (`calculator.rs`) to support the restored `use_decimals` feature and ensure compatibility with the new backend signature.



