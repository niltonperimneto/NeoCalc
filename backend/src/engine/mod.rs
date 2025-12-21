pub mod parser;
pub mod functions;

pub mod types;
use types::Number;

pub fn evaluate(expression: &str) -> Result<Number, String> {
    parser::evaluate(expression)
}
