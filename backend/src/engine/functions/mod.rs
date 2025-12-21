pub mod trigonometry;
pub mod hyperbolic;
pub mod complex_ops;
pub mod core_funcs;
pub mod statistics;
pub mod bitwise;
pub mod financial;


use num_complex::Complex64;


pub fn apply(name: &str, args: Vec<Complex64>) -> Result<Complex64, String> {
    let one_arg = || {
        if args.len() != 1 {
            return Err(format!("'{}' requires exactly 1 argument", name));
        }
        Ok(args[0])
    };

    match name {
        /* Trigonometry */
        "sin" => trigonometry::sin(one_arg()?),
        "cos" => trigonometry::cos(one_arg()?),
        "tan" => trigonometry::tan(one_arg()?),
        "asin" => trigonometry::asin(one_arg()?),
        "acos" | "cosin" => trigonometry::acos(one_arg()?),
        "atan" => trigonometry::atan(one_arg()?),

        /* Hyperbolic */
        "sinh" => hyperbolic::sinh(one_arg()?),
        "cosh" => hyperbolic::cosh(one_arg()?),
        "tanh" => hyperbolic::tanh(one_arg()?),

        /* Core */
        "log" => core_funcs::log(one_arg()?),
        "ln" => core_funcs::ln(one_arg()?),
        "sqrt" => core_funcs::sqrt(one_arg()?),

        /* Complex Ops */
        "conj" => complex_ops::conj(one_arg()?),
        "re" => complex_ops::re(one_arg()?),
        "im" | "lm" => complex_ops::im(one_arg()?),
        "abs" => complex_ops::abs(one_arg()?),

        /* Statistics */
        "mean" => statistics::mean(&args),
        "median" => statistics::median(&args),
        "var" => statistics::variance(&args),
        "std" => statistics::std_dev(&args),

        /* Bitwise (Programmer) */
        "band" => bitwise::band(&args),
        "bor" => bitwise::bor(&args),
        "bxor" => bitwise::bxor(&args),
        "bnot" => bitwise::bnot(&args),
        "lsh" => bitwise::lsh(&args),
        "rsh" => bitwise::rsh(&args),
        "rol" => bitwise::rol(&args),
        "ror" => bitwise::ror(&args),

        /* Financial */
        "fv" => financial::fv(&args),
        "pv" => financial::pv(&args),

        _ => Err(format!("'{}' is not a known function.", name)),
    }
}
