use pyo3::prelude::*;
use pyo3::wrap_pyfunction;


/// Safely evaluates a mathematical expression.
/// "Safely" here means we try not to let Python blow up your computer,
/// but no guarantees if you divide by zero in a philosophical sense.
fn safe_eval_inner(expression: &str) -> Result<f64, String> {
    // Basic parser implementation because we love reinventing wheels.
    // Expression grammar (aka hieroglyphics):
    // expr   -> term { (+|-) term }
    // term   -> factor { (*|/) factor }
    // factor -> NUMBER | ( expr ) | function( expr ) | - factor | IDENTIFIER (constants)

    let tokens = tokenize(expression).map_err(|e| e)?;
    let mut pos = 0;

    let result = parse_expr(&tokens, &mut pos)?;
    
    if pos < tokens.len() {
        return Err(format!("Unexpected token at end of expression: {:?}", tokens[pos]));
    }
    
    Ok(result)
}

#[derive(Debug, Clone)]
enum Token {
    Number(f64),
    Plus,
    Minus,
    Multiply,
    Divide,
    Power,
    LParen,
    RParen,
    Identifier(String),
}

fn tokenize(expr: &str) -> Result<Vec<Token>, String> {
    let mut tokens = Vec::new();
    let chars: Vec<char> = expr.chars().collect();
    let mut i = 0;

    while i < chars.len() {
        match chars[i] {
            ' ' | '\t' => i += 1,
            '0'..='9' | '.' => {
                let start = i;
                while i < chars.len() && (chars[i].is_ascii_digit() || chars[i] == '.') {
                    i += 1;
                }
                let num_str: String = chars[start..i].iter().collect();
                let num = num_str.parse::<f64>().map_err(|_| "Invalid number")?;
                tokens.push(Token::Number(num));
            }
            '+' => { tokens.push(Token::Plus); i += 1; }
            '-' => { tokens.push(Token::Minus); i += 1; }
            '*' => {
                if i + 1 < chars.len() && chars[i+1] == '*' {
                     tokens.push(Token::Power); i += 2;
                } else {
                     tokens.push(Token::Multiply); i += 1;
                }
            }
            '/' => { tokens.push(Token::Divide); i += 1; }
            '^' => { tokens.push(Token::Power); i += 1; }
            '(' => { tokens.push(Token::LParen); i += 1; }
            ')' => { tokens.push(Token::RParen); i += 1; }
            'a'..='z' | 'A'..='Z' => {
                let start = i;
                while i < chars.len() && chars[i].is_ascii_alphabetic() {
                    i += 1;
                }
                tokens.push(Token::Identifier(chars[start..i].iter().collect()));
            }
            _ => return Err(format!("Unexpected character: {}", chars[i])),
        }
    }
    Ok(tokens)
}

fn parse_expr(tokens: &[Token], pos: &mut usize) -> Result<f64, String> {
    let mut left = parse_term(tokens, pos)?;

    while *pos < tokens.len() {
        match tokens[*pos] {
            Token::Plus => {
                *pos += 1;
                left += parse_term(tokens, pos)?;
            }
            Token::Minus => {
                *pos += 1;
                left -= parse_term(tokens, pos)?;
            }
            _ => break,
        }
    }
    Ok(left)
}

fn parse_term(tokens: &[Token], pos: &mut usize) -> Result<f64, String> {
    let mut left = parse_factor(tokens, pos)?;

    while *pos < tokens.len() {
        match tokens[*pos] {
            Token::Multiply => {
                *pos += 1;
                left *= parse_factor(tokens, pos)?;
            }
            Token::Divide => {
                *pos += 1;
                let divisor = parse_factor(tokens, pos)?;
                if divisor == 0.0 {
                    return Err("Division by zero".to_string());
                }
                left /= divisor;
            }
            _ => break,
        }
    }
    Ok(left)
}

fn parse_factor(tokens: &[Token], pos: &mut usize) -> Result<f64, String> {
    // Handle Unary Minus
    if *pos < tokens.len() {
        if let Token::Minus = tokens[*pos] {
             *pos += 1;
             return Ok(-parse_factor(tokens, pos)?);
        }
    }

    let val = parse_base(tokens, pos)?;
    
    // Handle Power
    if *pos < tokens.len() {
        if let Token::Power = tokens[*pos] {
            *pos += 1;
            let exponent = parse_factor(tokens, pos)?; // Right associative? usually power is. let's just do simple
            return Ok(val.powf(exponent));
        }
    }
    
    Ok(val)
}

fn parse_base(tokens: &[Token], pos: &mut usize) -> Result<f64, String> {
    if *pos >= tokens.len() {
        return Err("Unexpected end of expression".to_string());
    }

    match &tokens[*pos] {
        Token::Number(n) => {
            *pos += 1;
            Ok(*n)
        }
        Token::Identifier(s) => {
            *pos += 1;
            match s.as_str() {
                "sin" => {
                    ensure_lparen(tokens, pos)?;
                    let val = parse_expr(tokens, pos)?;
                    ensure_rparen(tokens, pos)?;
                    Ok(val.sin())
                }
                "cos" => {
                    ensure_lparen(tokens, pos)?;
                    let val = parse_expr(tokens, pos)?;
                    ensure_rparen(tokens, pos)?;
                    Ok(val.cos())
                }
                "tan" => {
                    ensure_lparen(tokens, pos)?;
                    let val = parse_expr(tokens, pos)?;
                    ensure_rparen(tokens, pos)?;
                    Ok(val.tan())
                }
                "log" => {
                    ensure_lparen(tokens, pos)?;
                    let val = parse_expr(tokens, pos)?;
                    ensure_rparen(tokens, pos)?;
                    Ok(val.log10())
                }
                "ln" => {
                    ensure_lparen(tokens, pos)?;
                    let val = parse_expr(tokens, pos)?;
                    ensure_rparen(tokens, pos)?;
                    Ok(val.ln())
                }
                "sqrt" => {
                    ensure_lparen(tokens, pos)?;
                    let val = parse_expr(tokens, pos)?;
                    ensure_rparen(tokens, pos)?;
                    if val < 0.0 { return Err("Sqrt of negative number".to_string()); }
                    Ok(val.sqrt())
                }
                "pi" => Ok(std::f64::consts::PI),
                "e" => Ok(std::f64::consts::E),
                _ => Err(format!("Unknown function or constant: {}", s)),
            }
        }
        Token::LParen => {
            *pos += 1;
            let val = parse_expr(tokens, pos)?;
            if *pos >= tokens.len() || !matches!(tokens[*pos], Token::RParen) {
                return Err("Missing matching parenthesis".to_string());
            }
            *pos += 1;
            Ok(val)
        }
        _ => Err(format!("Unexpected token: {:?}", tokens[*pos])),
    }
}

fn ensure_lparen(tokens: &[Token], pos: &mut usize) -> Result<(), String> {
    if *pos < tokens.len() {
        if let Token::LParen = tokens[*pos] {
            *pos += 1;
            return Ok(());
        }
    }
    Err("Expected '(' after function name".to_string())
}

fn ensure_rparen(tokens: &[Token], pos: &mut usize) -> Result<(), String> {
    if *pos < tokens.len() {
        if let Token::RParen = tokens[*pos] {
            *pos += 1;
            return Ok(());
        }
    }
    Err("Expected ')'".to_string())
}


#[pyfunction]
fn evaluate(expression: String) -> PyResult<String> {
    match safe_eval_inner(&expression) {
        Ok(val) => {
            // Check if it is integer
            if val.fract() == 0.0 {
                Ok((val as i64).to_string())
            } else {
                Ok(val.to_string())
            }
        }
        Err(_) => Ok("Error".to_string()),
    }
}

#[pyfunction]
fn evaluate_async(py: Python<'_>, expression: String) -> PyResult<&PyAny> {
    pyo3_asyncio::tokio::future_into_py(py, async move {
        // Simulate async work or just run the calculation
        // In a real scenario, this might involve database calls or heavy computation
        let result = evaluate(expression);
        result
    })
}

#[pymodule]
pub fn neocalc_backend(_py: Python, m: &PyModule) -> PyResult<()> {
    // Exporting the chaos to Python.
    m.add_function(wrap_pyfunction!(evaluate, m)?)?;
    m.add_function(wrap_pyfunction!(evaluate_async, m)?)?;
    Ok(())
}
