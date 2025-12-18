#!/bin/bash
set -x
echo "Starting build..." > debug.log
cargo build >> debug.log 2>&1
echo "Build finished. Running..." >> debug.log
./target/debug/rust_frontend >> debug.log 2>&1
echo "Finished." >> debug.log
