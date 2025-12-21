use num::complex::Complex64;

pub fn sinh(c: Complex64) -> Result<Complex64, String> { Ok(c.sinh()) }
pub fn cosh(c: Complex64) -> Result<Complex64, String> { Ok(c.cosh()) }
pub fn tanh(c: Complex64) -> Result<Complex64, String> { Ok(c.tanh()) }
