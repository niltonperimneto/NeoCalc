use num::complex::Complex64;
use num_bigint::BigInt;
use num_rational::BigRational;
use num::{ToPrimitive, Zero, One};
use num::traits::Pow;
use std::ops::{Add, Sub, Mul, Div, Neg, Rem};

pub type Context = std::collections::HashMap<String, Number>;

#[derive(Debug, Clone, PartialEq)]
pub enum Number {
    Integer(BigInt),
    Rational(BigRational),
    Float(f64),
    Complex(Complex64),
}

impl Number {
    pub fn to_complex(&self) -> Complex64 {
        match self {
            Number::Integer(i) => Complex64::new(i.to_f64().unwrap_or(f64::INFINITY), 0.0),
            Number::Rational(r) => Complex64::new(r.to_f64().unwrap_or(f64::NAN), 0.0),
            Number::Float(f) => Complex64::new(*f, 0.0),
            Number::Complex(c) => *c,
        }
    }

    pub fn to_f64(&self) -> Option<f64> {
        match self {
            Number::Integer(i) => i.to_f64(),
            Number::Rational(r) => r.to_f64(),
            Number::Float(f) => Some(*f),
            Number::Complex(c) => if c.im == 0.0 { Some(c.re) } else { None },
        }
    }
}

// Helper to promote types
// Rank: Integer (0) -> Rational (1) -> Float (2) -> Complex (3)
fn promote(lhs: Number, rhs: Number) -> (Number, Number) {
    match (lhs, rhs) {
        (Number::Integer(l), Number::Integer(r)) => (Number::Integer(l), Number::Integer(r)),
        
        // Integer vs Rational -> Rational
        (Number::Integer(l), Number::Rational(r)) => (Number::Rational(BigRational::from_integer(l)), Number::Rational(r)),
        (Number::Rational(l), Number::Integer(r)) => (Number::Rational(l), Number::Rational(BigRational::from_integer(r))),
        (Number::Rational(l), Number::Rational(r)) => (Number::Rational(l), Number::Rational(r)),

        // Anything vs Float -> Float (Note: Rational -> Float loses precision)
        (Number::Float(l), r) => (Number::Float(l), Number::Float(r.to_f64().unwrap_or(f64::NAN))),
        (l, Number::Float(r)) => (Number::Float(l.to_f64().unwrap_or(f64::NAN)), Number::Float(r)),

        // Anything vs Complex -> Complex
        (Number::Complex(l), r) => (Number::Complex(l), Number::Complex(r.to_complex())),
        (l, Number::Complex(r)) => (Number::Complex(l.to_complex()), Number::Complex(r)),
    }
}

impl Add for Number {
    type Output = Number;
    fn add(self, rhs: Self) -> Self::Output {
        match promote(self, rhs) {
            (Number::Integer(l), Number::Integer(r)) => Number::Integer(l + r),
            (Number::Rational(l), Number::Rational(r)) => Number::Rational(l + r),
            (Number::Float(l), Number::Float(r)) => Number::Float(l + r),
            (Number::Complex(l), Number::Complex(r)) => Number::Complex(l + r),
            _ => unreachable!("Promote should handle all cases"),
        }
    }
}

impl Sub for Number {
    type Output = Number;
    fn sub(self, rhs: Self) -> Self::Output {
         match promote(self, rhs) {
            (Number::Integer(l), Number::Integer(r)) => Number::Integer(l - r),
            (Number::Rational(l), Number::Rational(r)) => Number::Rational(l - r),
            (Number::Float(l), Number::Float(r)) => Number::Float(l - r),
            (Number::Complex(l), Number::Complex(r)) => Number::Complex(l - r),
            _ => unreachable!(),
        }
    }
}

impl Mul for Number {
    type Output = Number;
    fn mul(self, rhs: Self) -> Self::Output {
         match promote(self, rhs) {
            (Number::Integer(l), Number::Integer(r)) => Number::Integer(l * r),
            (Number::Rational(l), Number::Rational(r)) => Number::Rational(l * r),
            (Number::Float(l), Number::Float(r)) => Number::Float(l * r),
            (Number::Complex(l), Number::Complex(r)) => Number::Complex(l * r),
            _ => unreachable!(),
        }
    }
}

impl Div for Number {
    type Output = Number;
    fn div(self, rhs: Self) -> Self::Output {
        match (self, rhs) {
            // Special Case: Integer / Integer = Rational (not Integer!)
            (Number::Integer(l), Number::Integer(r)) => {
                if r.is_zero() {
                     // Division by zero in integer arithmetic -> Promote to float for Inf/NaN handling?
                     // Or error? BigRational handles x/0? No, it panics.
                     // Let's promote to Float safely.
                     return Number::Float(l.to_f64().unwrap_or(0.0) / r.to_f64().unwrap_or(0.0));
                }
                Number::Rational(BigRational::new(l, r))
            },
             
            (l, r) => match promote(l, r) {
                 (Number::Rational(l), Number::Rational(r)) => {
                      if r.is_zero() { return Number::Float(f64::INFINITY); } // simplistic
                      Number::Rational(l / r)
                 },
                 (Number::Float(l), Number::Float(r)) => Number::Float(l / r),
                 (Number::Complex(l), Number::Complex(r)) => Number::Complex(l / r),
                 _ => unreachable!(),
            }
        }
    }
}

impl Neg for Number {
    type Output = Number;
    fn neg(self) -> Self::Output {
        match self {
            Number::Integer(i) => Number::Integer(-i),
            Number::Rational(r) => Number::Rational(-r),
            Number::Float(f) => Number::Float(-f),
            Number::Complex(c) => Number::Complex(-c),
        }
    }
}

impl Rem for Number {
    type Output = Number;
    fn rem(self, rhs: Self) -> Self::Output {
         match promote(self, rhs) {
            (Number::Integer(l), Number::Integer(r)) => Number::Integer(l % r),
            (Number::Rational(l), Number::Rational(r)) => Number::Rational(l % r),
            (Number::Float(l), Number::Float(r)) => Number::Float(l % r),
            (Number::Complex(l), Number::Complex(r)) => Number::Float(l.re % r.re), // Complex Modulo is weird, downgrade to Real Modulo
            _ => unreachable!(),
        }
    }
}

pub fn pow(base: Number, exp: Number) -> Number {
    match (base, exp) {
         (Number::Integer(b), Number::Integer(e)) => {
             if e >= BigInt::zero() {
                 // b^e can be huge.
                 // Limit? For now, let it fly or try to convert to u32
                 if let Some(e_u32) = e.to_u32() {
                     return Number::Integer(b.pow(e_u32));
                 }
             }
             // Negative exponent -> Rational
              // TODO: Implement
              Number::Float(b.to_f64().unwrap().powf(e.to_f64().unwrap()))
         },
         (b, e) => {
              // Fallback to Complex for generic power
              Number::Complex(b.to_complex().powc(e.to_complex()))
         }
    }
}

pub fn factorial(n: Number) -> Result<Number, String> {
    match n {
        Number::Integer(i) => {
            if i < BigInt::zero() { return Err("Factorial of negative integer".into()); }
            // Warning: Huge loop for big integers.
            // Simplified loop:
            let mut acc = BigInt::one();
            let mut k = BigInt::one();
            while k <= i {
                 acc = acc * &k;
                 k = k + 1;
                 // Safety brake? No, user asked for "Infinite" calculator.
            }
            Ok(Number::Integer(acc))
        },
        _ => Err("Factorial only implemented for Integers currently".into())
    }
}
