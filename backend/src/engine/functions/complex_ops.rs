use num::complex::Complex64;

pub fn conj(c: Complex64) -> Result<Complex64, String> { Ok(c.conj()) }
pub fn re(c: Complex64) -> Result<Complex64, String> { Ok(Complex64::new(c.re, 0.0)) }
pub fn im(c: Complex64) -> Result<Complex64, String> { Ok(Complex64::new(c.im, 0.0)) }
pub fn abs(c: Complex64) -> Result<Complex64, String> { Ok(Complex64::new(c.norm(), 0.0)) }
