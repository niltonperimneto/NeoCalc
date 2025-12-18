use num_complex::Complex64;

pub fn log(c: Complex64) -> Result<Complex64, String> { Ok(c.log(10.0)) }
pub fn ln(c: Complex64) -> Result<Complex64, String> { Ok(c.ln()) }
pub fn sqrt(c: Complex64) -> Result<Complex64, String> { 
    // Fix for signed zero causing sqrt(-1) = -i
    // We want the principal root on the positive side of the branch cut for real inputs.
    if c.im == 0.0 && c.re < 0.0 {
        Ok(Complex64::new(c.re, 0.0).sqrt())
    } else {
        Ok(c.sqrt()) 
    }
}
