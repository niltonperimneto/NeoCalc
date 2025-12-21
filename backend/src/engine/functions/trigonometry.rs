use num::complex::Complex64;

pub fn sin(c: Complex64) -> Result<Complex64, String> { Ok(c.sin()) }
pub fn cos(c: Complex64) -> Result<Complex64, String> { Ok(c.cos()) }
pub fn tan(c: Complex64) -> Result<Complex64, String> { Ok(c.tan()) }
pub fn asin(c: Complex64) -> Result<Complex64, String> { Ok(c.asin()) }
pub fn acos(c: Complex64) -> Result<Complex64, String> { Ok(c.acos()) }
pub fn atan(c: Complex64) -> Result<Complex64, String> { Ok(c.atan()) }
