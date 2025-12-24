use crate::engine::types::Number;
use crate::engine::errors::EngineError;
use crate::engine::functions::FunctionDef;
use num::Zero;
use num_bigint::BigInt;

pub fn mean(args: &[Number]) -> Result<Number, EngineError> {
    if args.is_empty() { return Err(EngineError::ArgumentMismatch("mean".into(), 1)); }
    let mut sum = Number::Integer(BigInt::zero());
    for arg in args {
        sum = sum + arg.clone();
    }
    let count = Number::Integer(BigInt::from(args.len()));
    Ok(sum / count)
}

pub fn median(args: &[Number]) -> Result<Number, EngineError> {
    if args.is_empty() { return Err(EngineError::ArgumentMismatch("median".into(), 1)); }
    
    let mut reals = Vec::with_capacity(args.len());
    for n in args {
        if let Some(f) = n.to_f64() {
             reals.push((f, n.clone()));
        } else {
             return Err(EngineError::TypeMismatch("Median requires real numbers".into(), "Complex".into()));
        }
    }
    
    reals.sort_by(|a, b| a.0.partial_cmp(&b.0).unwrap_or(std::cmp::Ordering::Equal));
    
    let mid = reals.len() / 2;
    if reals.len() % 2 == 1 {
        Ok(reals[mid].1.clone())
    } else {
        let left = reals[mid-1].1.clone();
        let right = reals[mid].1.clone();
        Ok((left + right) / Number::Integer(BigInt::from(2)))
    }
}

pub fn variance(args: &[Number]) -> Result<Number, EngineError> {
    if args.len() < 2 { return Err(EngineError::ArgumentMismatch("variance".into(), 2)); }
    
    let m = mean(args)?;
    let mut sum_sq_diff = Number::Integer(BigInt::zero());
    
    for x in args {
        let diff = x.clone() - m.clone();
        sum_sq_diff = sum_sq_diff + (diff.clone() * diff);
    }
    
    Ok(sum_sq_diff / Number::Integer(BigInt::from(args.len() - 1)))
}

pub fn std_dev(args: &[Number]) -> Result<Number, EngineError> {
    let v = variance(args)?;
    let c = v.to_complex();
    Ok(Number::Complex(c.sqrt()))
}

inventory::submit! { FunctionDef { name: "mean", func: mean } }
inventory::submit! { FunctionDef { name: "median", func: median } }
inventory::submit! { FunctionDef { name: "var", func: variance } }
inventory::submit! { FunctionDef { name: "std", func: std_dev } }
