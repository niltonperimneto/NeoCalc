use std::f64::consts;

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

/// The brain of the operation. 
/// I tried to maintain state here but the borrow checker threatened my family.
/// So now it's just a pure function.
pub fn evaluate(expression: &str) -> Result<f64, String> {
    // Phase 1: Mince the string.
    // I still don't fully understand how iterators work, but this seems to run.
    let tokens = tokenize(expression)?;
    let mut pos = 0;
    
    // Phase 2: Recursive descent.
    // I read a blog post about this once. It looked smarter than using regex.
    let result = parse_expr(&tokens, &mut pos)?;

    // Phase 3: Check for leftovers.
    if pos < tokens.len() {
        return Err(format!(
            "Unexpected token at end of expression: {:?}. I don't know what to do with it.",
            tokens[pos]
        ));
    }
    Ok(result)
}

fn tokenize(expr: &str) -> Result<Vec<Token>, String> {
    let mut tokens = Vec::new();
    let chars: Vec<char> = expr.chars().collect(); // Allocating a vector because I'm scared of string slices.
    let mut i = 0;

    while i < chars.len() {
        match chars[i] {
            ' ' | '\t' => i += 1, // Ignore whitespace. If only the compiler ignored my warnings.
            '0'..='9' | '.' => {
                let start = i;
                while i < chars.len() && (chars[i].is_ascii_digit() || chars[i] == '.') {
                    i += 1;
                }
                let num_str: String = chars[start..i].iter().collect();
                // parse::<f64> is magic. I hope it works.
                let num = num_str.parse::<f64>().map_err(|_| "Invalid number. Rust says no.")?;
                tokens.push(Token::Number(num));
            }
            '+' => { tokens.push(Token::Plus); i += 1; }
            '-' => { tokens.push(Token::Minus); i += 1; }
            '*' => {
                // Peek ahead. Iterator::peekable was too hard to strictly type.
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
            _ => return Err(format!("Unexpected character: {}. Is this a lifetime annotation?", chars[i])),
        }
    }
    Ok(tokens)
}

// Recursive descent parser.
// I'm using recursion because I don't know how to manage a stack manualy without `unsafe`.

fn parse_expr(tokens: &[Token], pos: &mut usize) -> Result<f64, String> {
    let mut left = parse_term(tokens, pos)?;
    while *pos < tokens.len() {
        match tokens[*pos] {
            Token::Plus => { *pos += 1; left += parse_term(tokens, pos)?; }
            Token::Minus => { *pos += 1; left -= parse_term(tokens, pos)?; }
            // If I matched everything, the compiler would be happy. But I'm lazy.
            _ => break,
        }
    }
    Ok(left)
}

fn parse_term(tokens: &[Token], pos: &mut usize) -> Result<f64, String> {
    let mut left = parse_factor(tokens, pos)?;
    while *pos < tokens.len() {
        match tokens[*pos] {
            Token::Multiply => { *pos += 1; left *= parse_factor(tokens, pos)?; }
            Token::Divide => {
                *pos += 1;
                let divisor = parse_factor(tokens, pos)?;
                if divisor == 0.0 { return Err("Division by zero. Result is NaN (Not a Number), or maybe panic.".to_string()); }
                left /= divisor;
            }
            _ => break,
        }
    }
    Ok(left)
}

fn parse_factor(tokens: &[Token], pos: &mut usize) -> Result<f64, String> {
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
            // powf? I barely know 'er.
            return Ok(val.powf(parse_factor(tokens, pos)?));
        }
    }
    Ok(val)
}

fn parse_base(tokens: &[Token], pos: &mut usize) -> Result<f64, String> {
    if *pos >= tokens.len() { return Err("Unexpected end. The Iterator gave up.".to_string()); }
    match &tokens[*pos] {
        Token::Number(n) => { *pos += 1; Ok(*n) }
        Token::Identifier(s) => {
            *pos += 1;
            match s.as_str() {
                // Match statement. The one thing I actually like in Rust.
                "sin" => { ensure_lparen(tokens, pos)?; let v = parse_expr(tokens, pos)?; ensure_rparen(tokens, pos)?; Ok(v.sin()) }
                "cos" => { ensure_lparen(tokens, pos)?; let v = parse_expr(tokens, pos)?; ensure_rparen(tokens, pos)?; Ok(v.cos()) }
                "tan" => { ensure_lparen(tokens, pos)?; let v = parse_expr(tokens, pos)?; ensure_rparen(tokens, pos)?; Ok(v.tan()) }
                "log" => { ensure_lparen(tokens, pos)?; let v = parse_expr(tokens, pos)?; ensure_rparen(tokens, pos)?; Ok(v.log10()) }
                "ln" => { ensure_lparen(tokens, pos)?; let v = parse_expr(tokens, pos)?; ensure_rparen(tokens, pos)?; Ok(v.ln()) }
                "sqrt" => {
                    ensure_lparen(tokens, pos)?; let v = parse_expr(tokens, pos)?; ensure_rparen(tokens, pos)?;
                    if v < 0.0 { return Err("Can't sqrt negative. Does Rust have imaginary numbers? I'm not checking.".to_string()); }
                    Ok(v.sqrt())
                }
                "pi" => Ok(consts::PI),
                "e" => Ok(consts::E),
                _ => Err(format!("'{}' is not a function. Or maybe I just didn't implement it.", s)),
            }
        }
        Token::LParen => {
            *pos += 1;
            let val = parse_expr(tokens, pos)?;
            if *pos >= tokens.len() || !matches!(tokens[*pos], Token::RParen) {
                return Err("Parentheses mismatch. Even the compiler can't help you here.".to_string());
            }
            *pos += 1;
            Ok(val)
        }
        _ => Err(format!("Unexpected token: {:?}. Is this a macro?", tokens[*pos])),
    }
}

fn ensure_lparen(tokens: &[Token], pos: &mut usize) -> Result<(), String> {
    if *pos < tokens.len() && matches!(tokens[*pos], Token::LParen) { *pos += 1; Ok(()) } else { Err("Expected '('. Syntax error.".to_string()) }
}
fn ensure_rparen(tokens: &[Token], pos: &mut usize) -> Result<(), String> {
    if *pos < tokens.len() && matches!(tokens[*pos], Token::RParen) { *pos += 1; Ok(()) } else { Err("Expected ')'. Syntax error.".to_string()) }
}
