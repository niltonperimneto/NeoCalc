# Changelog

## [1.0.0] - 2026-01-13
### Restructured
- **Repository Layout**: Transitioned to a "NeoCalc Desktop" structure.
  - Renamed `launcher` package to `neocalc-desktop`.
  - Renamed `core` directory to `backend` to align with Android repository conventions.
  - Established a flat Cargo Workspace containing `backend`, `desktop`, and `bindings/python`.
- **Documentation**: Updated `README.md` to reflect the new identity as "NeoCalc Desktop" and provided updated build instructions.
- **Python Bindings**: Fixed compilation issues in `bindings/python` by handling new `Number` types (`Rational`, `Complex`) exposed by the core backend.
