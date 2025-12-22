pub mod parser;
pub mod functions;

pub mod types;
use types::Number;

pub fn evaluate(expression: &str, context: &mut types::Context) -> Result<Number, String> {
    parser::evaluate(expression, context)
}
