use num_complex::Complex64;

fn to_int(c: Complex64) -> Result<i64, String> {
    if c.im != 0.0 {
        return Err("Bitwise operations require real numbers".to_string());
    }
    if c.re.fract() != 0.0 {
        return Err("Bitwise operations require integers".to_string()); 
    }
    Ok(c.re as i64)
}

pub fn band(args: &[Complex64]) -> Result<Complex64, String> {
    if args.len() != 2 { return Err("band requires 2 arguments".to_string()); }
    let a = to_int(args[0])?;
    let b = to_int(args[1])?;
    Ok(Complex64::new((a & b) as f64, 0.0))
}

pub fn bor(args: &[Complex64]) -> Result<Complex64, String> {
    if args.len() != 2 { return Err("bor requires 2 arguments".to_string()); }
    let a = to_int(args[0])?;
    let b = to_int(args[1])?;
    Ok(Complex64::new((a | b) as f64, 0.0))
}

pub fn bxor(args: &[Complex64]) -> Result<Complex64, String> {
    if args.len() != 2 { return Err("bxor requires 2 arguments".to_string()); }
    let a = to_int(args[0])?;
    let b = to_int(args[1])?;
    Ok(Complex64::new((a ^ b) as f64, 0.0))
}

pub fn bnot(args: &[Complex64]) -> Result<Complex64, String> {
    if args.len() != 1 { return Err("bnot requires 1 argument".to_string()); }
    let a = to_int(args[0])?;
    Ok(Complex64::new((!a) as f64, 0.0))
}

pub fn lsh(args: &[Complex64]) -> Result<Complex64, String> {
    if args.len() != 2 { return Err("lsh requires 2 arguments".to_string()); }
    let a = to_int(args[0])?;
    let b = to_int(args[1])?;
    if b < 0 { return Err("Shift count cannot be negative".to_string()); }
    Ok(Complex64::new((a << b) as f64, 0.0))
}

pub fn rsh(args: &[Complex64]) -> Result<Complex64, String> {
    if args.len() != 2 { return Err("rsh requires 2 arguments".to_string()); }
    let a = to_int(args[0])?;
    let b = to_int(args[1])?;
    if b < 0 { return Err("Shift count cannot be negative".to_string()); }
    Ok(Complex64::new((a >> b) as f64, 0.0))
}

pub fn rol(args: &[Complex64]) -> Result<Complex64, String> {
    if args.len() != 2 { return Err("rol requires 2 arguments".to_string()); }
    let a = to_int(args[0])?;
    let b = to_int(args[1])?;
    if b < 0 { return Err("Rotate count cannot be negative".to_string()); }
    // Rotate left on 64-bit integer
    Ok(Complex64::new(a.rotate_left(b as u32) as f64, 0.0))
}

pub fn ror(args: &[Complex64]) -> Result<Complex64, String> {
    if args.len() != 2 { return Err("ror requires 2 arguments".to_string()); }
    let a = to_int(args[0])?;
    let b = to_int(args[1])?;
    if b < 0 { return Err("Rotate count cannot be negative".to_string()); }
    // Rotate right on 64-bit integer
    Ok(Complex64::new(a.rotate_right(b as u32) as f64, 0.0))
}
