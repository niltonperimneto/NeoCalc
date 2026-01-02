pub mod engine;
pub mod utils;

use std::collections::HashMap;

#[derive(Clone, Debug)]
pub enum Number {
    Integer(num_bigint::BigInt),
    Float(f64),
}

#[derive(Debug)]
pub struct EngineError(String);

impl std::fmt::Display for EngineError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.0)
    }
}

impl std::error::Error for EngineError {}

#[derive(Clone, Default)]
pub struct Context {
    // Based on usage (**v) in calculator.rs, likely Box or similar indirection
    pub scopes: Vec<HashMap<String, Box<Number>>>, 
}

impl Context {
    pub fn new() -> Self {
        Self { scopes: vec![HashMap::new()] }
    }
}
