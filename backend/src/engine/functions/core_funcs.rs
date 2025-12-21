use num::complex::Complex64;

pub fn log(c: Complex64) -> Result<Complex64, String> { Ok(c.log(10.0)) }
pub fn ln(c: Complex64) -> Result<Complex64, String> { Ok(c.ln()) }
pub fn sqrt(c: Complex64) -> Result<Complex64, String> {

    if c.im == 0.0 && c.re < 0.0 {
        Ok(Complex64::new(c.re, 0.0).sqrt())
    } else {
        Ok(c.sqrt())
    }
}
