use std::f64::consts;
use num_complex::Complex64;
use logos::Logos;
use super::functions;

#[derive(Logos, Debug, Clone, PartialEq)]
#[logos(skip r"[ \t\n\f]+")] // Skip whitespace
enum Token<'a> {
    #[token("+")]
    Plus,
    #[token("-")]
    Minus,
    #[token("*")]
    Multiply,
    #[token("/")]
    Divide,
    #[token("^")]
    Power,
    #[token("(")]
    LParen,
    #[token(")")]
    RParen,

    #[regex(r"[0-9]+(\.[0-9]+)?", |lex| lex.slice().parse::<f64>().ok())]
    Number(f64),

    #[regex("[a-zA-Z]+", |lex| lex.slice())]
    Identifier(&'a str),

    Eof, // Virtual EOF token for parser logic
}

pub fn evaluate(expression: &str) -> Result<Complex64, String> {
    let mut lexer = Token::lexer(expression);
    let mut tokens = Vec::new();
    
    while let Some(res) = lexer.next() {
        match res {
            Ok(token) => tokens.push(token),
            Err(_) => return Err("Invalid token encountered".to_string()),
        }
    }
    tokens.push(Token::Eof);

    let mut parser = Parser::new(&tokens);
    let result = parser.parse_bp(0)?;
    
    if parser.current() != &Token::Eof {
        return Err(format!("Unexpected token at end: {:?}", parser.current()));
    }
    
    Ok(result)
}

struct Parser<'a> {
    tokens: &'a [Token<'a>],
    pos: usize,
}

impl<'a> Parser<'a> {
    fn new(tokens: &'a [Token<'a>]) -> Self {
        Parser { tokens, pos: 0 }
    }

    fn current(&self) -> &Token<'a> {
        &self.tokens[self.pos]
    }

    fn advance(&mut self) {
        if self.pos < self.tokens.len() {
            self.pos += 1;
        }
    }

    fn parse_bp(&mut self, min_bp: u8) -> Result<Complex64, String> {
        let token = self.current().clone();
        self.advance();

        let mut lhs = match token {
            Token::Number(n) => Complex64::new(n, 0.0),
            Token::Identifier(s) => {
                match s {
                    "pi" => Complex64::new(consts::PI, 0.0),
                    "e" => Complex64::new(consts::E, 0.0),
                    "i" | "j" => Complex64::new(0.0, 1.0),
                    _ => {
                        // Function call
                        if let Token::LParen = self.current() {
                            self.advance();
                            let arg = self.parse_bp(0)?;
                            if let Token::RParen = self.current() {
                                self.advance();
                            } else {
                                return Err("Expected ')'".to_string());
                            }
                            functions::apply(s, arg)?
                        } else {
                            // Variable? For now just error or 0
                             return Err(format!("Unknown identifier or missing '(': {}", s));
                        }
                    }
                }
            }
            Token::LParen => {
                let val = self.parse_bp(0)?;
                if let Token::RParen = self.current() {
                    self.advance();
                    val
                } else {
                    return Err("Expected ')'".to_string());
                }
            }
            Token::Minus => {
                // Unary minus
                // -x^2 should be - (x^2) usually in math (precedence of ^ > unary -)
                // But in many langs -x^2 is (-x)^2.
                // Standard math: -2^2 = -4.
                // So unary minus binding power must be lower than Power?
                // Let's check:
                // Power infix bp = (10, 9) (Right associative)
                // If unary minus bp is ((), 8) -> - 2 ^ 2
                // parse -: recurse with min_bp 8.
                //   parse 2.
                //   peek ^. bp(^) = 10. 10 > 8. Continue loop in recursive call.
                //   consume ^. recurse with bp 9. parse 2.
                //   return 4.
                // Unary minus applies to 4 -> -4. Correct.
                
                let ((), r_bp) = prefix_binding_power(&Token::Minus)?;
                let rhs = self.parse_bp(r_bp)?;
                -rhs
            }
            Token::Eof => return Err("Unexpected EOF".to_string()),
            t => return Err(format!("Unexpected token: {:?}", t)),
        };

        loop {
            let op = self.current();
            if let Token::Eof = op { break; }
            
            let (l_bp, r_bp) = match infix_binding_power(op) {
                Some(bp) => bp,
                None => break,
            };

            if l_bp < min_bp {
                break;
            }

            let op_token = op.clone();
            self.advance();
            let rhs = self.parse_bp(r_bp)?;

            lhs = match op_token {
                Token::Plus => lhs + rhs,
                Token::Minus => lhs - rhs,
                Token::Multiply => lhs * rhs,
                Token::Divide => {
                     if rhs.norm() == 0.0 { return Err("Division by zero".to_string()); }
                     lhs / rhs
                }
                Token::Power => lhs.powc(rhs),
                _ => return Err("Impossible operator".to_string()),
            };
        }

        Ok(lhs)
    }
}

fn prefix_binding_power(op: &Token) -> Result<((), u8), String> {
    match op {
        // Unary minus binding power: should be fairly high, but lower than Power if we want -2^2 to be -(2^2).
        // If Power is 10/9.
        // If Unary is 8.
        // - 2 ^ 2:
        // parse(-) -> recurse(8)
        //   parse(2)
        //   peek(^) -> 10 > 8 -> continue
        //   parse(^) -> recurse(9) -> parses 2
        //   returns 2^2 = 4
        // returns -4. Correct.
        
        Token::Minus => Ok(((), 8)), 
        _ => Err(format!("Bad prefix operator: {:?}", op)),
    }
}

fn infix_binding_power(op: &Token) -> Option<(u8, u8)> {
    match op {
        Token::Plus | Token::Minus => Some((1, 2)),
        Token::Multiply | Token::Divide => Some((3, 4)),
        Token::Power => Some((10, 9)), // Right associative: 2^3^4 = 2^(3^4) -> right bp lower than left
        _ => None,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use num_complex::Complex64;

    fn eval(s: &str) -> Complex64 {
        evaluate(s).expect(&format!("Failed to parse: {}", s))
    }

    fn assert_close(a: Complex64, b: Complex64) {
        let diff = (a - b).norm();
        assert!(diff < 1e-10, "Expected {}, got {}, diff {}", b, a, diff);
    }

    #[test]
    fn test_basic_arithmetic() {
        assert_close(eval("1 + 2"), Complex64::new(3.0, 0.0));
        assert_close(eval("10 - 4"), Complex64::new(6.0, 0.0));
        assert_close(eval("3 * 5"), Complex64::new(15.0, 0.0));
        assert_close(eval("12 / 4"), Complex64::new(3.0, 0.0));
    }

    #[test]
    fn test_precedence() {
        assert_close(eval("1 + 2 * 3"), Complex64::new(7.0, 0.0));
        assert_close(eval("(1 + 2) * 3"), Complex64::new(9.0, 0.0));
        assert_close(eval("10 - 2 + 3"), Complex64::new(11.0, 0.0)); // Left associative + -
    }

    #[test]
    fn test_power_associativity() {
        // 2^3^2 = 2^(3^2) = 2^9 = 512
        // (2^3)^2 = 8^2 = 64
        assert_close(eval("2^3^2"), Complex64::new(512.0, 0.0));
    }

    #[test]
    fn test_unary_minus() {
        assert_close(eval("-5"), Complex64::new(-5.0, 0.0));
        assert_close(eval("5 + - 3"), Complex64::new(2.0, 0.0));
    }

    #[test]
    fn test_unary_vs_power() {
        // -2^2 should be -4
        assert_close(eval("-2^2"), Complex64::new(-4.0, 0.0));
        // (-2)^2 should be 4
        assert_close(eval("(-2)^2"), Complex64::new(4.0, 0.0));
    }

    #[test]
    fn test_functions() {
        assert_close(eval("sqrt(4)"), Complex64::new(2.0, 0.0));
        assert_close(eval("abs(-5)"), Complex64::new(5.0, 0.0));
        // sin(0) = 0
        assert_close(eval("sin(0)"), Complex64::new(0.0, 0.0));
    }
    
    #[test]
    fn test_complex() {
        // i * i = -1
        assert_close(eval("i * i"), Complex64::new(-1.0, 0.0));
    }

    #[test]
    fn test_sqrt_negative() {
        let neg_one = eval("-1");
        assert_close(neg_one, Complex64::new(-1.0, 0.0));
        
        // Ensure principal root (i) is returned for sqrt(-1)
        let root = eval("sqrt(-1)");
        assert_close(root, Complex64::new(0.0, 1.0));
    }
}
