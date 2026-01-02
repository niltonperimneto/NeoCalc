use crate::{Context, Number, EngineError};

pub fn evaluate(_expr: &str, _context: &mut Context) -> Result<Number, EngineError> {
    Ok(Number::Float(0.0))
}
