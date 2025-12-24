use crate::engine::types::Number;
use crate::engine::errors::EngineError;
use crate::engine::functions::FunctionDef;
use num::complex::Complex64;

fn one_arg(args: &[Number], name: &str) -> Result<Complex64, EngineError> {
    if args.len() != 1 {
        return Err(EngineError::ArgumentMismatch(name.into(), 1));
    }
    Ok(args[0].to_complex())
}

pub fn conj(args: &[Number]) -> Result<Number, EngineError> {
    Ok(Number::Complex(one_arg(args, "conj")?.conj()))
}

pub fn re(args: &[Number]) -> Result<Number, EngineError> {
    Ok(Number::Float(one_arg(args, "re")?.re))
}

pub fn im(args: &[Number]) -> Result<Number, EngineError> {
    Ok(Number::Float(one_arg(args, "im")?.im))
}

pub fn abs(args: &[Number]) -> Result<Number, EngineError> {
    Ok(Number::Float(one_arg(args, "abs")?.norm()))
}

inventory::submit! { FunctionDef { name: "conj", func: conj } }
inventory::submit! { FunctionDef { name: "re", func: re } }
inventory::submit! { FunctionDef { name: "im", func: im } }
inventory::submit! { FunctionDef { name: "lm", func: im } } // Alias
inventory::submit! { FunctionDef { name: "abs", func: abs } }
