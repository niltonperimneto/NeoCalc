pub mod trigonometry;
pub mod hyperbolic;
pub mod complex_ops;
pub mod core_funcs;
pub mod statistics;
pub mod bitwise;
pub mod financial;


use num::complex::Complex64;
use crate::engine::types::Number;

// Helper to convert args to Complex64 for legacy functions
fn to_complex_args(args: &[Number]) -> Vec<Complex64> {
    args.iter().map(|n| n.to_complex()).collect()
}

pub fn apply(name: &str, args: Vec<Number>) -> Result<Number, String> {
    let _one_arg = || {
        if args.len() != 1 {
            return Err(format!("'{}' requires exactly 1 argument", name));
        }
        Ok(args[0].clone())
    };

    let one_complex = || {
        if args.len() != 1 {
            return Err(format!("'{}' requires exactly 1 argument", name));
        }
        Ok(args[0].to_complex())
    };

    match name {
        /* Trigonometry (Complex) */
        "sin" => Ok(Number::Complex(trigonometry::sin(one_complex()?)?)),
        "cos" => Ok(Number::Complex(trigonometry::cos(one_complex()?)?)),
        "tan" => Ok(Number::Complex(trigonometry::tan(one_complex()?)?)),
        "asin" => Ok(Number::Complex(trigonometry::asin(one_complex()?)?)),
        "acos" | "cosin" => Ok(Number::Complex(trigonometry::acos(one_complex()?)?)),
        "atan" => Ok(Number::Complex(trigonometry::atan(one_complex()?)?)),

        /* Hyperbolic (Complex) */
        "sinh" => Ok(Number::Complex(hyperbolic::sinh(one_complex()?)?)),
        "cosh" => Ok(Number::Complex(hyperbolic::cosh(one_complex()?)?)),
        "tanh" => Ok(Number::Complex(hyperbolic::tanh(one_complex()?)?)),

        /* Core */
        // Explicitly handle sqrt for perfect squares here? Or inside core_funcs?
        // Let's delegate to functions, assuming updated signatures or manual conversion.
        "log" => Ok(Number::Complex(core_funcs::log(one_complex()?)?)),
        "ln" => Ok(Number::Complex(core_funcs::ln(one_complex()?)?)),
        "sqrt" => Ok(Number::Complex(core_funcs::sqrt(one_complex()?)?)),

        /* Complex Ops */
        "conj" => Ok(Number::Complex(complex_ops::conj(one_complex()?)?)),
        "re" => Ok(Number::Float(complex_ops::re(one_complex()?)?.re)),
        "im" | "lm" => Ok(Number::Float(complex_ops::im(one_complex()?)?.re)),
        "abs" => Ok(Number::Float(complex_ops::abs(one_complex()?)?.re)),

        /* Statistics (Number aware) */
        "mean" => statistics::mean(&args),
        "median" => statistics::median(&args),
        "var" => statistics::variance(&args),
        "std" => statistics::std_dev(&args),

        /* Bitwise (Number aware) */
        "band" => bitwise::band(&args),
        "bor" => bitwise::bor(&args),
        "bxor" => bitwise::bxor(&args),
        "bnot" => bitwise::bnot(&args),
        "lsh" => bitwise::lsh(&args),
        "rsh" => bitwise::rsh(&args),
        "rol" => bitwise::rol(&args),
        "ror" => bitwise::ror(&args),

        /* Financial (Complex) */
        "fv" => Ok(Number::Complex(financial::fv(&to_complex_args(&args))?)),
        "pv" => Ok(Number::Complex(financial::pv(&to_complex_args(&args))?)),
        "pmt" => Ok(Number::Complex(financial::pmt(&to_complex_args(&args))?)),
        "nper" => Ok(Number::Complex(financial::nper(&to_complex_args(&args))?)),
        "rate" => Ok(Number::Complex(financial::rate(&to_complex_args(&args))?)),
        "npv" => Ok(Number::Complex(financial::npv(&to_complex_args(&args))?)),
        "irr" => Ok(Number::Complex(financial::irr(&to_complex_args(&args))?)),

        _ => Err(format!("'{}' is not a known function.", name)),
    }
}
