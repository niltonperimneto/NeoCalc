use std::f64::consts;
use num_complex::Complex64;
use super::functions;

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

pub fn evaluate(expression: &str) -> Result<Complex64, String> {
    let tokens = tokenize(expression)?;
    let mut pos = 0;
    let result = parse_expr(&tokens, &mut pos)?;

    if pos < tokens.len() {
        return Err(format!("Unexpected token at end: {:?}", tokens[pos]));
    }
    Ok(result)
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
                if i + 1 < chars.len() && chars[i + 1] == '*' {
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

fn parse_expr(tokens: &[Token], pos: &mut usize) -> Result<Complex64, String> {
    let mut left = parse_term(tokens, pos)?;
    while *pos < tokens.len() {
        match tokens[*pos] {
            Token::Plus => { *pos += 1; left += parse_term(tokens, pos)?; }
            Token::Minus => { *pos += 1; left -= parse_term(tokens, pos)?; }
            _ => break,
        }
    }
    Ok(left)
}

fn parse_term(tokens: &[Token], pos: &mut usize) -> Result<Complex64, String> {
    let mut left = parse_factor(tokens, pos)?;
    while *pos < tokens.len() {
        match tokens[*pos] {
            Token::Multiply => { *pos += 1; left *= parse_factor(tokens, pos)?; }
            Token::Divide => {
                *pos += 1;
                let divisor = parse_factor(tokens, pos)?;
                if divisor.norm() == 0.0 { return Err("Division by zero".to_string()); }
                left /= divisor;
            }
            _ => break,
        }
    }
    Ok(left)
}

fn parse_factor(tokens: &[Token], pos: &mut usize) -> Result<Complex64, String> {
    if *pos < tokens.len() {
        if let Token::Minus = tokens[*pos] {
            *pos += 1;
            return Ok(-parse_factor(tokens, pos)?);
        }
    }
    let val = parse_base(tokens, pos)?;
    if *pos < tokens.len() {
        if let Token::Power = tokens[*pos] {
            *pos += 1;
            return Ok(val.powc(parse_factor(tokens, pos)?));
        }
    }
    Ok(val)
}

fn parse_base(tokens: &[Token], pos: &mut usize) -> Result<Complex64, String> {
    if *pos >= tokens.len() { return Err("Unexpected end".to_string()); }
    match &tokens[*pos] {
        Token::Number(n) => { *pos += 1; Ok(Complex64::new(*n, 0.0)) }
        Token::Identifier(s) => {
            *pos += 1;
            // Constants
            match s.as_str() {
                "pi" => return Ok(Complex64::new(consts::PI, 0.0)),
                "e" => return Ok(Complex64::new(consts::E, 0.0)),
                "i" | "j" => return Ok(Complex64::new(0.0, 1.0)),
                _ => {}
            }
            
            // Function call
            ensure_lparen(tokens, pos)?;
            let arg = parse_expr(tokens, pos)?;
            ensure_rparen(tokens, pos)?;
            
            functions::apply(s, arg)
        }
        Token::LParen => {
            *pos += 1;
            let val = parse_expr(tokens, pos)?;
            if *pos >= tokens.len() || !matches!(tokens[*pos], Token::RParen) {
                return Err("Mismatched parentheses".to_string());
            }
            *pos += 1;
            Ok(val)
        }
        _ => Err(format!("Unexpected token: {:?}", tokens[*pos])),
    }
}

fn ensure_lparen(tokens: &[Token], pos: &mut usize) -> Result<(), String> {
    if *pos < tokens.len() && matches!(tokens[*pos], Token::LParen) { *pos += 1; Ok(()) } else { Err("Expected '('".to_string()) }
}
fn ensure_rparen(tokens: &[Token], pos: &mut usize) -> Result<(), String> {
    if *pos < tokens.len() && matches!(tokens[*pos], Token::RParen) { *pos += 1; Ok(()) } else { Err("Expected ')'".to_string()) }
}
