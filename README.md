# NeoCalc (The "Why Do We Exist" Fork)

Originally was created as a simple calculator to teach kids how to program. It was simple. It was pure. It added 2 and 2 and got 4.

But then **I** came along. I saw a perfectly functional teaching tool and thought, "You know what this needs? Unnecessary complexity and a bad attitude." So I forked it, injected it with Rust, and stripped it of its innocence.

## Usage
It calculates things. Sometimes. Mostly it judges you for needing a calculator to multiply single digits.

## Installation
If you really want to verify that mass times acceleration equals force (or merely headache):

```bash
# Don't ask me why ABI3 is involved.
PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1 cargo run --manifest-path rust_runner/Cargo.toml
```

## Building (For the Masochists)
So you want a standalone binary to cherish forever? Fine.

1. **Install Prerequisites**: You need Rust, GTK4, and Python development headers. Consult your distro's wiki for the specific incantations.
2. **Compile**:
   ```bash
   PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1 cargo build --release --manifest-path rust_runner/Cargo.toml
   ```
3. **Locate the Artifact**: The binary `neocalc_runner` awaits you in `target/release/`. It still needs the `python_gui` folder nearby because we're not magic.

## Safety Notice
This calculator assumes no liability for failed math exams or existential crises triggered by its output.
