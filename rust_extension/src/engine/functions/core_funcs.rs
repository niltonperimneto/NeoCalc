use num_complex::Complex64;

pub fn log(c: Complex64) -> Result<Complex64, String> { Ok(c.log(10.0)) }
pub fn ln(c: Complex64) -> Result<Complex64, String> { Ok(c.ln()) }
pub fn sqrt(c: Complex64) -> Result<Complex64, String> { Ok(c.sqrt()) }
