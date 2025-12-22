use num::complex::Complex64;

/// Future Value
/// fv(rate, nper, pv, [pmt], [type])
/// args: rate, nper, pv, pmt (optional, default 0), type (optional, default 0)
pub fn fv(args: &[Complex64]) -> Result<Complex64, String> {
    if args.len() < 3 || args.len() > 5 {
        return Err("fv requires 3 to 5 arguments: rate, nper, pv, [pmt], [type]".to_string());
    }
    let rate = args[0];
    let nper = args[1];
    let pv = args[2];
    let pmt = if args.len() >= 4 { args[3] } else { Complex64::new(0.0, 0.0) };
    let type_val = if args.len() >= 5 { args[4].re as i32 } else { 0 };

    // Standard TVM formula
    // if rate == 0: FV + PV + PMT * nper = 0
    // else: FV + PV*(1+r)^n + PMT*(1+r*type)*(((1+r)^n - 1)/r) = 0
    
    let result = if rate.norm() < 1e-9 {
        -(pv + pmt * nper)
    } else {
        let one = Complex64::new(1.0, 0.0);
        let factor = (one + rate).powc(nper);
        let term_pmt = (pmt * (one + rate * (type_val as f64))) * ((factor - one) / rate);
        -(pv * factor + term_pmt)
    };
    
    Ok(result)
}

/// Present Value
/// pv(rate, nper, fv, [pmt], [type])
pub fn pv(args: &[Complex64]) -> Result<Complex64, String> {
    if args.len() < 3 || args.len() > 5 {
        return Err("pv requires 3 to 5 arguments: rate, nper, fv, [pmt], [type]".to_string());
    }
    let rate = args[0];
    let nper = args[1];
    let fv = args[2];
    let pmt = if args.len() >= 4 { args[3] } else { Complex64::new(0.0, 0.0) };
    let type_val = if args.len() >= 5 { args[4].re as i32 } else { 0 };

    // Solve for PV from TVM equation
    let result = if rate.norm() < 1e-9 {
        -(fv + pmt * nper)
    } else {
        let one = Complex64::new(1.0, 0.0);
        let factor = (one + rate).powc(nper);
        let term_pmt = (pmt * (one + rate * (type_val as f64))) * ((factor - one) / rate);
        -(fv + term_pmt) / factor
    };
    
    Ok(result)
}

/// Payment
/// pmt(rate, nper, pv, [fv], [type])
pub fn pmt(args: &[Complex64]) -> Result<Complex64, String> {
    if args.len() < 3 || args.len() > 5 {
        return Err("pmt requires 3 to 5 arguments: rate, nper, pv, [fv], [type]".to_string());
    }
    let rate = args[0];
    let nper = args[1];
    let pv = args[2];
    let fv = if args.len() >= 4 { args[3] } else { Complex64::new(0.0, 0.0) };
    let type_val = if args.len() >= 5 { args[4].re as i32 } else { 0 };

    let result = if rate.norm() < 1e-9 {
        -(fv + pv) / nper
    } else {
        let one = Complex64::new(1.0, 0.0);
        let factor = (one + rate).powc(nper);
        let num = (pv * factor + fv) * rate;
        let den = (one + rate * (type_val as f64)) * (factor - one);
        -(num / den)
    };
    
    Ok(result)
}

/// Number of Periods
/// nper(rate, pmt, pv, [fv], [type])
pub fn nper(args: &[Complex64]) -> Result<Complex64, String> {
    if args.len() < 3 || args.len() > 5 {
        return Err("nper requires 3 to 5 arguments: rate, pmt, pv, [fv], [type]".to_string());
    }
    let rate = args[0];
    let pmt = args[1];
    let pv = args[2];
    let fv = if args.len() >= 4 { args[3] } else { Complex64::new(0.0, 0.0) };
    let type_val = if args.len() >= 5 { args[4].re as i32 } else { 0 };

    // Solving for n in TVM equation
    // Requires logarithmic math. 
    // This is mathematically complex if arguments are complex.
    // For nper, we assume arguments are valid such that solution exists.
    
    if rate.norm() < 1e-9 {
        Ok(-(fv + pv) / pmt)
    } else {
        let one = Complex64::new(1.0, 0.0);
        let r_type = one + rate * (type_val as f64);
        let num = pmt * r_type - fv * rate;
        let den = pmt * r_type + pv * rate;
        // n = log(num/den) / log(1+r)
        // Note: Sign handling in finance formulas is tricky. 
        // Standard formula: n = ln( (PMT*(1+r*t) - FV*r) / (PMT*(1+r*t) + PV*r) ) / ln(1+r)
        
        // Safety check for div by zero or negative log? 
        // Complex log handles negative numbers seamlessly.
        
        Ok((num / den).ln() / (one + rate).ln())
    }
}

/// Net Present Value
/// npv(rate, val1, val2, ...)
pub fn npv(args: &[Complex64]) -> Result<Complex64, String> {
    if args.len() < 2 {
        return Err("npv requires at least 2 arguments: rate, value1...".to_string());
    }
    let rate = args[0];
    let mut sum = Complex64::new(0.0, 0.0);
    let one = Complex64::new(1.0, 0.0);
    
    for (i, &val) in args[1..].iter().enumerate() {
        let t = (i + 1) as f64;
        sum += val / (one + rate).powf(t);
    }
    
    Ok(sum)
}

/// Internal Rate of Return
/// irr(val1, val2, ...)
/// Uses Newton-Raphson method to find rate where NPV = 0
pub fn irr(args: &[Complex64]) -> Result<Complex64, String> {
    if args.len() < 1 {
        return Err("irr requires cash flow values".to_string());
    }
    
    // We treat inputs as real numbers for IRR stability.
    // Finding complex roots for IRR is rare and often meaningless.
    // We try to find a real root.
    
    let values: Vec<f64> = args.iter().map(|c| c.re).collect();
    let mut guess = 0.1; // 10% guess
    
    for _ in 0..100 {
        let mut npv = 0.0;
        let mut deriv = 0.0;
        
        for (i, &val) in values.iter().enumerate() {
            let t = i as f64; // Cash flow at time t. Convention: first arg is time 0?
            // Excel IRR assumes equally spaced, first value is time 0.
            // Formula: sum( val / (1+r)^t ) = 0
            
            let factor = (1.0_f64 + guess).powf(t);
            npv += val / factor;
            
            // Derivative of val * (1+r)^-t is -t * val * (1+r)^(-t-1)
            if t > 0.0 {
                let d_factor = (1.0_f64 + guess).powf(t + 1.0_f64);
                deriv -= t * val / d_factor;
            }
        }
        
        if npv.abs() < 1e-7 {
            return Ok(Complex64::new(guess, 0.0));
        }
        
        if deriv.abs() < 1e-10 {
            break; // Stationary point or failure
        }
        
        let new_guess = guess - npv / deriv;
        if (new_guess - guess).abs() < 1e-7 {
             return Ok(Complex64::new(new_guess, 0.0));
        }
        guess = new_guess;
    }
    
    // If convergence fails, return NaN or error?
    // Return guess as best effort.
    Ok(Complex64::new(guess, 0.0))
}

/// Rate (Interest Rate per period)
/// rate(nper, pmt, pv, [fv], [type], [guess])
pub fn rate(args: &[Complex64]) -> Result<Complex64, String> {
    if args.len() < 3 {
        return Err("rate requires arguments: nper, pmt, pv, [fv], [type], [guess]".to_string());
    }
    let nper = args[0].re;
    let pmt = args[1].re;
    let pv = args[2].re;
    let fv = if args.len() >= 4 { args[3].re } else { 0.0 };
    let type_val = if args.len() >= 5 { args[4].re as i32 } else { 0 };
    let mut guess = if args.len() >= 6 { args[5].re } else { 0.1 };

    // Newton-Raphson for Rate
    // Function: PV*(1+r)^n + PMT*(1+r*type)*(((1+r)^n - 1)/r) + FV = 0
    
    for _ in 0..100 {
        // Calculate y (Net Future Value at end? Or Present Value?)
        // Let's use Future Value equation = 0
        // FV_eq = PV*(1+r)^n + PMT*(1+r*t)*( ((1+r)^n - 1)/r ) + FV
        
        if guess.abs() < 1e-9 {
            // Linear case: PV + PMT*n + FV = 0
            // If satisfied, rate is 0. Else jump.
             let y = pv + pmt * nper + fv;
             if y.abs() < 1e-7 { return Ok(Complex64::new(0.0, 0.0)); }
             guess = 0.0001;
             continue;
        }
        
        let r = guess;
        let factor = (1.0 + r).powf(nper);
        let term_pmt = (pmt * (1.0 + r * (type_val as f64))) * ((factor - 1.0) / r);
        let y = pv * factor + term_pmt + fv;
        
        // Derivative?
        // d/dr (PV*(1+r)^n) = PV * n * (1+r)^(n-1)
        // d/dr (PMT * ...) is complex.
        // Use secant method or numerical derivative.
        
        let delta = 1e-5;
        let r_d = r + delta;
        let factor_d = (1.0 + r_d).powf(nper);
        let term_pmt_d = (pmt * (1.0 + r_d * (type_val as f64))) * ((factor_d - 1.0) / r_d);
        let y_d = pv * factor_d + term_pmt_d + fv;
        
        let deriv = (y_d - y) / delta;
        
        if deriv.abs() < 1e-10 { break; }
        
        let new_r = r - y / deriv;
        if (new_r - r).abs() < 1e-7 {
             return Ok(Complex64::new(new_r, 0.0));
        }
        guess = new_r;
    }
    
    Ok(Complex64::new(guess, 0.0))
}
