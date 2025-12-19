use num_complex::Complex64;

pub fn mean(args: &[Complex64]) -> Result<Complex64, String> {
    if args.is_empty() { return Err("mean requires at least one argument".to_string()); }
    let sum: Complex64 = args.iter().sum();
    Ok(sum / (args.len() as f64))
}

pub fn median(args: &[Complex64]) -> Result<Complex64, String> {
    if args.is_empty() { return Err("median requires at least one argument".to_string()); }
    
    // Check if we are dealing with real numbers only and collect them
    // We reserve capacity to avoid multiple allocations
    let mut reals = Vec::with_capacity(args.len());
    for c in args {
        if c.im != 0.0 {
            return Err("median only supported for real numbers".to_string());
        }
        if c.re.is_nan() {
             return Err("NaN encountered in input".to_string());
        }
        reals.push(c.re);
    }
    
    let mid = reals.len() / 2;
    
    // Use select_nth_unstable for O(n) performance instead of O(n log n)
    let (_, &mut mid_val, _) = reals.select_nth_unstable_by(mid, |a, b| a.partial_cmp(b).unwrap_or(std::cmp::Ordering::Equal));
    
    if reals.len() % 2 == 1 {
        Ok(Complex64::new(mid_val, 0.0))
    } else {
        // For even numbers, we need the average of mid and mid-1.
        // select_nth_unstable partitions the array, so everything to the left of mid is smaller.
        // We need the max of the left side.
        // Since we already partitioned at mid, we can search 0..mid for the max.
        let left_max = reals[0..mid].iter().max_by(|a, b| a.partial_cmp(b).unwrap()).cloned().unwrap_or(mid_val);
        Ok(Complex64::new((left_max + mid_val) / 2.0, 0.0))
    }
}
 
pub fn variance(args: &[Complex64]) -> Result<Complex64, String> {
    if args.len() < 2 { return Err("variance requires at least two arguments".to_string()); }
    
    let m = mean(args)?;
    let mut sum_sq_diff = Complex64::new(0.0, 0.0);
    
    for x in args {
        let diff = x - m;
        sum_sq_diff += diff * diff; // Or diff.norm_sqr() for real variance? Standard variance of complex?
        // Let's stick to standard formula E[(X-u)^2]
    }
    
    // Sample variance (n-1)
    Ok(sum_sq_diff / ((args.len() - 1) as f64))
}

pub fn std_dev(args: &[Complex64]) -> Result<Complex64, String> {
    let v = variance(args)?;
    Ok(v.sqrt())
}
