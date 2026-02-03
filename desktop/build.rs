fn main() {
    // Only link in the binary, not if checking
    println!("cargo:rerun-if-changed=build.rs");

    // Quick fix: force link python 3.14 as reported by the system
    // ideal solution uses pyo3-build-config or shells out to python3-config

    let output = std::process::Command::new("python3-config")
        .arg("--ldflags")
        .arg("--embed")
        .output();

    if let Ok(o) = output {
        let s = String::from_utf8_lossy(&o.stdout);
        for part in s.split_whitespace() {
            if part.starts_with("-l") {
                println!("cargo:rustc-link-lib={}", &part[2..]);
            } else if part.starts_with("-L") {
                println!("cargo:rustc-link-search=native={}", &part[2..]);
            }
        }
    } else {
        // Fallback if python3-config is missing but we know it's 3.14
        println!("cargo:rustc-link-lib=python3.14");
    }
}
