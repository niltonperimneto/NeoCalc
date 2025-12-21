use std::f64::consts;
use num_complex::Complex64;
use logos::Logos;
use super::functions;

/* Define the tokens that can appear in an expression using the Logos lexer */
#[derive(Logos, Debug, Clone, PartialEq)]
#[logos(skip r"[ \t\n\f]+")]
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
    #[token(",")]
    Comma,

    /* Match numbers, including decimals, hex, and binary */
    #[regex(r"[0-9]+(\.[0-9]+)?", |lex| lex.slice().parse::<f64>().ok())]
    #[regex(r"0x[0-9a-fA-F]+", |lex| i64::from_str_radix(&lex.slice()[2..], 16).map(|i| i as f64).ok())]
    #[regex(r"0b[01]+", |lex| i64::from_str_radix(&lex.slice()[2..], 2).map(|i| i as f64).ok())]
    Number(f64),

    /* Match variable names or function identifiers */
    #[regex("[a-zA-Z]+", |lex| lex.slice())]
    Identifier(&'a str),

    Eof,
}

pub fn evaluate(expression: &str) -> Result<Complex64, String> {
    /* Create a lexer to iterate over the tokens in the string */
    let mut lexer = Token::lexer(expression);
    let mut tokens = Vec::new();

    /* Collect all tokens into a vector */
    while let Some(res) = lexer.next() {
        match res {
            Ok(token) => tokens.push(token),
            Err(_) => return Err("Invalid token encountered".to_string()),
        }
    }
    tokens.push(Token::Eof);

    /* Initialize the parser and start parsing from binding power 0 */
    let mut parser = Parser::new(&tokens);
    let result = parser.parse_bp(0)?;

    /* Ensure all tokens were consumed */
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

    /* Return the current token being looked at */
    fn current(&self) -> &Token<'a> {
        &self.tokens[self.pos]
    }

    /* Move to the next token in the stream */
    fn advance(&mut self) {
        if self.pos < self.tokens.len() {
            self.pos += 1;
        }
    }

    /* Pratt parsing algorithm: Parse with a minimum binding power */
    fn parse_bp(&mut self, min_bp: u8) -> Result<Complex64, String> {
        let token = self.current().clone();
        self.advance();

        /* Handle the prefix part (numbers, identifiers, parentheses, unary ops) */
        let mut lhs = match token {
            Token::Number(n) => Complex64::new(n, 0.0),
            Token::Identifier(s) => {
                match s {
                    /* Constants */
                    "pi" => Complex64::new(consts::PI, 0.0),
                    "e" => Complex64::new(consts::E, 0.0),
                    "i" | "j" => Complex64::new(0.0, 1.0),
                    _ => {
                        /* Function calls like sin(...) or mean(1, 2, 3) */
                        if let Token::LParen = self.current() {
                            self.advance();
                            
                            let mut args = Vec::new();
                            
                            if let Token::RParen = self.current() {
                                /* Empty argument list: function() */
                                self.advance();
                            } else {
                                loop {
                                    args.push(self.parse_bp(0)?);
                                    
                                    if let Token::Comma = self.current() {
                                        self.advance();
                                    } else if let Token::RParen = self.current() {
                                        self.advance();
                                        break;
                                    } else {
                                        return Err("Expected ',' or ')' in argument list".to_string());
                                    }
                                }
                            }
                            functions::apply(s, args)?
                        } else {
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
                let ((), r_bp) = prefix_binding_power(&Token::Minus)?;
                let rhs = self.parse_bp(r_bp)?;
                -rhs
            }
            Token::Eof => return Err("Unexpected EOF".to_string()),
            t => return Err(format!("Unexpected token: {:?}", t)),
        };

        /* Handle infix operators while their binding power is high enough */
        loop {
            let op = self.current();
            if let Token::Eof = op { break; }

            let (l_bp, r_bp) = match infix_binding_power(op) {
                Some(bp) => bp,
                None => break,
            };

            /* Stop if upcoming operator has lower precedence */
            if l_bp < min_bp {
                break;
            }

            let op_token = op.clone();
            self.advance();
            let rhs = self.parse_bp(r_bp)?;

            /* Apply the operator */
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
        /* Unary minus has high binding power */
        Token::Minus => Ok(((), 8)),
        _ => Err(format!("Bad prefix operator: {:?}", op)),
    }
}

fn infix_binding_power(op: &Token) -> Option<(u8, u8)> {
    match op {
        /* Standard order of operations PEMDAS */
        Token::Plus | Token::Minus => Some((1, 2)),
        Token::Multiply | Token::Divide => Some((3, 4)),
        /* Power is right-associative, so right binding power is lower than left?  */
        /* Wait, standard is right-associative: 2^3^2 = 2^(3^2). So left < right. */
        /* Here (10, 9) means left binds tighter than right? No. */
        /* If left op has power 9, and this is 10, then we stop? */
        /* Let's verify: (10, 9) means if we are at power^, we have L_BP=10, R_BP=9. */
        /* If next op is also power, it checks L_BP(10) < current_min(9)? No. */
        /* Actually, if we parse_bp(9) for RHS: next ^ has L_BP=10. 10 < 9 is False. So it recurses. */
        Token::Power => Some((10, 9)),
        _ => None,
    }
}


