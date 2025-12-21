use num::complex::Complex64;

/// Future Value
/// fv(rate, nper, pv)
pub fn fv(args: &[Complex64]) -> Result<Complex64, String> {
    if args.len() != 3 {
        return Err("fv requires 3 arguments: rate, nper, pv".to_string());
    }
    let rate = args[0];
    let nper = args[1];
    let pv = args[2];

    // FV = PV * (1 + r)^n
    // note: standard finance often flips sign of PV, but let's keep it simple math here
    // If user inputs PV as positive, FV is returned.
    Ok(pv * (Complex64::new(1.0, 0.0) + rate).powc(nper))
}

/// Present Value
/// pv(rate, nper, fv)
pub fn pv(args: &[Complex64]) -> Result<Complex64, String> {
    if args.len() != 3 {
        return Err("pv requires 3 arguments: rate, nper, fv".to_string());
    }
    let rate = args[0];
    let nper = args[1];
    let fv = args[2];

    // PV = FV / (1 + r)^n
    Ok(fv / (Complex64::new(1.0, 0.0) + rate).powc(nper))
}
