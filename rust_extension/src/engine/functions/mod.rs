pub mod trigonometry;
pub mod hyperbolic;
pub mod complex_ops;
pub mod core_funcs;

use num_complex::Complex64;

pub fn apply(name: &str, val: Complex64) -> Result<Complex64, String> {
    match name {
        // Trigonometry
        "sin" => trigonometry::sin(val),
        "cos" => trigonometry::cos(val),
        "tan" => trigonometry::tan(val),
        "asin" => trigonometry::asin(val),
        "acos" | "cosin" => trigonometry::acos(val),
        "atan" => trigonometry::atan(val),

        // Hyperbolic
        "sinh" => hyperbolic::sinh(val),
        "cosh" => hyperbolic::cosh(val),
        "tanh" => hyperbolic::tanh(val),

        // Core
        "log" => core_funcs::log(val),
        "ln" => core_funcs::ln(val),
        "sqrt" => core_funcs::sqrt(val),

        // Complex
        "conj" => complex_ops::conj(val),
        "re" => complex_ops::re(val),
        "im" | "lm" => complex_ops::im(val),
        "abs" => complex_ops::abs(val),

        _ => Err(format!("'{}' is not a known function.", name)),
    }
}
