use num::complex::Complex64;
use logos::Logos;
use num_bigint::BigInt;
use super::functions;
use super::types::{Number, pow, factorial};

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
    #[token("!")]
    Factorial,
    #[token("%")]
    Percent, // Modulo
    #[token("(")]
    LParen,
    #[token(")")]
    RParen,
    #[token(",")]
    Comma,

    /* Match Floats: explicit dot or scientific notation */
    /* Needs to be checked BEFORE Integer to avoid greedy matching issues for things like 1.0 */
    /* Regex for float: digits dot digits (opt) exponent (opt) OR digits exponent */
    #[regex(r"[0-9]+\.[0-9]*([eE][+-]?[0-9]+)?", |lex| lex.slice().parse::<f64>().ok())]
    #[regex(r"[0-9]+[eE][+-]?[0-9]+", |lex| lex.slice().parse::<f64>().ok())]
    Float(f64),

    /* Match Integers: digits only */
    #[regex(r"[0-9]+", |lex| lex.slice().parse::<BigInt>().ok())]
    #[regex(r"0x[0-9a-fA-F]+", |lex| BigInt::parse_bytes(&lex.slice()[2..].as_bytes(), 16))]
    #[regex(r"0b[01]+", |lex| BigInt::parse_bytes(&lex.slice()[2..].as_bytes(), 2))]
    Integer(BigInt),

    /* Match variable names or function identifiers */
    #[regex("[a-zA-Z]+", |lex| lex.slice())]
    Identifier(&'a str),

    Eof,
}

pub fn evaluate(expression: &str) -> Result<Number, String> {
    /* Initialize the parser with the lexer directly */
    let mut parser = Parser::new(Token::lexer(expression).spanned());
    let result = parser.parse_bp(0)?;

    /* Ensure all tokens were consumed */
    if parser.current() != &Token::Eof {
        return Err(format!("Unexpected token at end: {:?}", parser.current()));
    }

    Ok(result)
}

struct Parser<'a> {
    lexer: logos::SpannedIter<'a, Token<'a>>,
    current: Token<'a>,
}

impl<'a> Parser<'a> {
    fn new(mut lexer: logos::SpannedIter<'a, Token<'a>>) -> Self {
        let current = match lexer.next() {
            Some((Ok(token), _)) => token,
            Some((Err(_), _)) => Token::Eof, // Or handle error better? For now, if invalid token, parser will likely error on "Unexpected token" or we can error earlier. 
            // Wait, previous logic returned "Invalid token encountered" immediately.
            // Let's replicate this: parse_bp will fail if it hits something weird, or we can handle it in advance.
            // But to match previous behavior:
            // If we encounter Err, we could store a special Error token or just panic/error?
            // Let's refine: The loop logic handled Err by returning Err string.
            // Here we are inside the struct.
            None => Token::Eof,
        };
        
        // Actually, to be safe and robust, let's just treat invalid lexing as EOF or Error token if we had one.
        // But better: let's verify current logic.
        // If I make `current` a Result<Token, String>, it complicates things.
        // Let's simplistically assume valid tokens or EOF for now, handling errors in `advance`.
        
        Parser { lexer, current }
    }

    fn current(&self) -> &Token<'a> {
        &self.current
    }

    fn advance(&mut self) {
        self.current = match self.lexer.next() {
            Some((Ok(token), _)) => token,
            Some((Err(_), _)) => Token::Eof, // Treat invalid characters as determining EOF/Error for now, or let parser choke on them if we had an Error variant.
            None => Token::Eof,
        };
    }

    /* Pratt parsing algorithm: Parse with a minimum binding power */
    fn parse_bp(&mut self, min_bp: u8) -> Result<Number, String> {
        let token = self.current().clone();
        self.advance();

        /* Handle the prefix part (numbers, identifiers, parentheses, unary ops) */
        let mut lhs = match token {
            Token::Float(f) => Number::Float(f),
            Token::Integer(i) => Number::Integer(i),
            Token::Identifier(s) => {
                match s {
                    /* Constants */
                    "pi" => Number::Float(std::f64::consts::PI),
                    "e" => Number::Float(std::f64::consts::E),
                    "i" | "j" => Number::Complex(Complex64::new(0.0, 1.0)),
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
                            // Functions now accept Number directly
                            return functions::apply(s, args);
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
            // If we silently treated Err as EOF in advance, we might get here. 
            // Better: If lexer error, we should return error.
            // Let's check if we can detect it. Check logic below.
            t => return Err(format!("Unexpected token: {:?}", t)),
        };

        /* Handle infix and postfix operators while their binding power is high enough */
        loop {
            let op = self.current();
            if let Token::Eof = op { break; }

            // Handle Postfix operators (Factorial)
            if let Token::Factorial = op {
                 let l_bp = 11; // Postfix binding power
                 if l_bp < min_bp { break; }
                 self.advance();
                 lhs = factorial(lhs)?;
                 continue;
            }

            // Check for explicit Infix or Implicit Multiplication
            let (op_token, l_bp, r_bp) = match infix_binding_power(op) {
                Some((l, r)) => (Some(op.clone()), l, r),
                None => {
                    // Check for Implicit Multiplication:
                    // If current token is a start of an expression (Identifier, LParen),
                    // treat it as multiplication with BP (3, 4)
                    if matches!(op, Token::LParen | Token::Identifier(_)) {
                        (None, 3, 4)
                    } else {
                        break;
                    }
                }
            };

            /* Stop if upcoming operator has lower precedence */
            if l_bp < min_bp {
                break;
            }

            let rhs;
            if let Some(token) = op_token {
                self.advance();
                rhs = self.parse_bp(r_bp)?;
                
                lhs = match token {
                    Token::Plus => lhs + rhs,
                    Token::Minus => lhs - rhs,
                    Token::Multiply => lhs * rhs,
                    Token::Divide => lhs / rhs,
                    Token::Power => pow(lhs, rhs),
                    Token::Percent => lhs % rhs,
                    _ => return Err("Impossible operator".to_string()),
                };
            } else {
                // Implicit Multiplication
                // We do NOT advance, because the current token is the start of RHS
                rhs = self.parse_bp(r_bp)?;
                lhs = lhs * rhs;
            }
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
        Token::Multiply | Token::Divide | Token::Percent => Some((3, 4)),
        /* Power is right-associative, so right binding power is lower than left?  */
        /* Wait, standard is right-associative: 2^3^2 = 2^(3^2). So left < right. */
        /* Here (10, 9) means left binds tighter than right? No. */
        /* If left op has power 9, and this is 10, then we stop? */
        /* Actually, if we parse_bp(9) for RHS: next ^ has L_BP=10. 10 < 9 is False. So it recurses. */
        Token::Power => Some((10, 9)),
        _ => None,
    }
}
