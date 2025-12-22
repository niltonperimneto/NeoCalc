use crate::engine::types::Number;
use num::Zero;
use num_bigint::BigInt;

pub fn mean(args: &[Number]) -> Result<Number, String> {
    if args.is_empty() { return Err("mean requires at least one argument".to_string()); }
    let mut sum = Number::Integer(BigInt::zero());
    for arg in args {
        sum = sum + arg.clone();
    }
    // Divide by count (Rational)
    let count = Number::Integer(BigInt::from(args.len()));
    Ok(sum / count)
}

pub fn median(args: &[Number]) -> Result<Number, String> {
    if args.is_empty() { return Err("median requires at least one argument".to_string()); }
    
    // Convert to float for sorting? No, we should define PartialOrd for Number if possible.
    // Since implementing PartialOrd for complex numbers is undefined, we act like before:
    // Only support Real numbers for median.
    
    let mut reals = Vec::with_capacity(args.len());
    for n in args {
        // Approximate sorting value (f64).
        // For exactness, we'd need exact comparison (Rational vs Rational).
        // Let's rely on f64 conversion for sorting order, but keep original values.
        if let Some(f) = n.to_f64() {
             reals.push((f, n.clone()));
        } else {
             return Err("median only supports real numbers".to_string());
        }
    }
    
    // Sort by f64 key
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

pub fn variance(args: &[Number]) -> Result<Number, String> {
    if args.len() < 2 { return Err("variance requires at least two arguments".to_string()); }
    
    let m = mean(args)?;
    let mut sum_sq_diff = Number::Integer(BigInt::zero());
    
    for x in args {
        let diff = x.clone() - m.clone();
        sum_sq_diff = sum_sq_diff + (diff.clone() * diff);
    }
    
    Ok(sum_sq_diff / Number::Integer(BigInt::from(args.len() - 1)))
}

pub fn std_dev(args: &[Number]) -> Result<Number, String> {
    let v = variance(args)?;
    // Number type doesn't have sqrt natively (irrational).
    // Promote to Complex/Float.
    let c = v.to_complex();
    Ok(Number::Complex(c.sqrt()))
}
