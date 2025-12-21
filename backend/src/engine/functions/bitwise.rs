use crate::engine::types::Number;
use num_bigint::BigInt;
use num::ToPrimitive;

fn to_int(n: &Number) -> Result<BigInt, String> {
    match n {
        Number::Integer(i) => Ok(i.clone()),
        _ => Err("Bitwise operations require integers".to_string()),
    }
}

pub fn band(args: &[Number]) -> Result<Number, String> {
    if args.len() != 2 { return Err("band requires 2 arguments".to_string()); }
    let a = to_int(&args[0])?;
    let b = to_int(&args[1])?;
    Ok(Number::Integer(a & b))
}

pub fn bor(args: &[Number]) -> Result<Number, String> {
    if args.len() != 2 { return Err("bor requires 2 arguments".to_string()); }
    let a = to_int(&args[0])?;
    let b = to_int(&args[1])?;
    Ok(Number::Integer(a | b))
}

pub fn bxor(args: &[Number]) -> Result<Number, String> {
    if args.len() != 2 { return Err("bxor requires 2 arguments".to_string()); }
    let a = to_int(&args[0])?;
    let b = to_int(&args[1])?;
    Ok(Number::Integer(a ^ b))
}

pub fn bnot(args: &[Number]) -> Result<Number, String> {
    if args.len() != 1 { return Err("bnot requires 1 argument".to_string()); }
    let a = to_int(&args[0])?;
    Ok(Number::Integer(!a))
}

pub fn lsh(args: &[Number]) -> Result<Number, String> {
    if args.len() != 2 { return Err("lsh requires 2 arguments".to_string()); }
    let a = to_int(&args[0])?;
    let b = to_int(&args[1])?;
    // Shift amount must be primitive type usually
    if let Some(shift) = b.to_usize() {
         Ok(Number::Integer(a << shift))
    } else {
         Err("Shift count too large or negative".to_string())
    }
}

pub fn rsh(args: &[Number]) -> Result<Number, String> {
    if args.len() != 2 { return Err("rsh requires 2 arguments".to_string()); }
    let a = to_int(&args[0])?;
    let b = to_int(&args[1])?;
    if let Some(shift) = b.to_usize() {
         Ok(Number::Integer(a >> shift))
    } else {
         Err("Shift count too large or negative".to_string())
    }
}

// Rotate is tricky for BigInt as it depends on bit width. 
// Standard calculators often assume 64-bit or 32-bit for rotate.
// Since BigInts are arbitrary size, 'rotate' is ill-defined without a bit width.
// We will mimic previous behavior: Convert to i64 (if fits), rotate, convert back.
pub fn rol(args: &[Number]) -> Result<Number, String> {
    if args.len() != 2 { return Err("rol requires 2 arguments".to_string()); }
    let a = to_int(&args[0])?;
    let b = to_int(&args[1])?;
    
    // Fallback to 64-bit logic for rotation as typical
    if let (Some(val), Some(rot)) = (a.to_i64(), b.to_u32()) {
         Ok(Number::Integer(BigInt::from(val.rotate_left(rot))))
    } else {
         Err("Rotation arguments too large (supports 64-bit integers)".to_string())
    }
}

pub fn ror(args: &[Number]) -> Result<Number, String> {
    if args.len() != 2 { return Err("ror requires 2 arguments".to_string()); }
    let a = to_int(&args[0])?;
    let b = to_int(&args[1])?;
    
    if let (Some(val), Some(rot)) = (a.to_i64(), b.to_u32()) {
         Ok(Number::Integer(BigInt::from(val.rotate_right(rot))))
    } else {
         Err("Rotation arguments too large (supports 64-bit integers)".to_string())
    }
}
