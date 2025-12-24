use super::types::{Number, factorial, pow};
use super::functions;
use super::errors::EngineError;
use std::collections::HashMap;

#[derive(Debug, Clone)]
pub struct UserFunction {
    pub params: Vec<String>,
    pub body: Expr,
}

#[derive(Debug, Clone)]
pub struct Context {
    pub scopes: Vec<HashMap<String, Number>>,
    pub functions: HashMap<String, UserFunction>,
}

impl Default for Context {
    fn default() -> Self {
        Self {
            scopes: vec![HashMap::new()],
            functions: HashMap::new(),
        }
    }
}

impl Context {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn get_var(&self, name: &str) -> Option<&Number> {
        // Search from top (local) to bottom (global)
        for scope in self.scopes.iter().rev() {
            if let Some(val) = scope.get(name) {
                return Some(val);
            }
        }
        None
    }

    pub fn set_var(&mut self, name: String, value: Number) {
        // Set in current usage scope (usually global for assignments unless explicit local)
        // Simplest strategy: Assignment = update closest scope if exists, else define in global? 
        // OR define in current (top) scope?
        // Standard scripting: Local assignment -> create local.
        // Update: update local.
        // If I want to update Global from Local? `global x`.
        // NeoCalc approach: Simple dynamic scoping. Assignment always sets in TOP scope.
        if let Some(scope) = self.scopes.last_mut() {
            scope.insert(name, value);
        }
    }

    pub fn push_scope(&mut self) {
        self.scopes.push(HashMap::new());
    }

    pub fn pop_scope(&mut self) {
        if self.scopes.len() > 1 {
            self.scopes.pop();
        }
    }
}

#[derive(Debug, Clone, PartialEq)]
pub enum BinaryOp {
    Add,
    Sub,
    Mul,
    Div,
    Mod,
    Pow,
}

#[derive(Debug, Clone, PartialEq)]
pub enum UnaryOp {
    Neg,
    Factorial,
}

#[derive(Debug, Clone, PartialEq)]
pub enum Expr {
    Literal(Number),
    Variable(String),
    BinaryOp(BinaryOp, Box<Expr>, Box<Expr>),
    UnaryOp(UnaryOp, Box<Expr>),
    FunctionCall(String, Vec<Expr>),
    Assignment(String, Box<Expr>),
    FunctionDef(String, Vec<String>, Box<Expr>),
} 

impl Expr {
    pub fn eval(&self, context: &mut Context) -> Result<Number, EngineError> {
        // Optimization: Iterative traversal for left-associative BinaryOps to prevent stack overflow
        let mut stack = Vec::new();
        let mut current_expr = self;
        
        // Traverse down the left side, pushing operations to stack
        while let Expr::BinaryOp(op, lhs, rhs) = current_expr {
            stack.push((op, rhs));
            current_expr = lhs;
        }

        // Evaluate the leaf (LHS base)
        let mut result = match current_expr {
            Expr::Literal(n) => Ok(n.clone()),
            Expr::Variable(name) => {
                context.get_var(name).cloned().ok_or_else(|| EngineError::UndefinedVariable(name.clone()))
            },
            Expr::Assignment(name, expr) => {
                let val = expr.eval(context)?;
                context.set_var(name.clone(), val.clone());
                Ok(val)
            },
            Expr::FunctionDef(name, params, body) => {
                let func = UserFunction {
                    params: params.clone(),
                    body: *body.clone(),
                };
                context.functions.insert(name.clone(), func);
                Ok(Number::Integer(num_bigint::BigInt::from(0))) 
            },
            Expr::UnaryOp(op, expr) => {
                let val = expr.eval(context)?;
                match op {
                    UnaryOp::Neg => Ok(-val),
                    UnaryOp::Factorial => factorial(val).map_err(EngineError::Generic),
                }
            },
            Expr::FunctionCall(name, args_exprs) => {
                let mut args = Vec::with_capacity(args_exprs.len());
                for arg_expr in args_exprs {
                    args.push(arg_expr.eval(context)?);
                }
                
                if let Some(user_func) = context.functions.get(name).cloned() {
                    if args.len() != user_func.params.len() {
                        return Err(EngineError::ArgumentMismatch(name.clone(), user_func.params.len()));
                    }
                    context.push_scope();
                    for (param, value) in user_func.params.iter().zip(args.iter()) {
                        context.set_var(param.clone(), value.clone());
                    }
                    let result = user_func.body.eval(context);
                    context.pop_scope();
                    result
                } else {
                    functions::apply(name, args)
                }
            },
            Expr::BinaryOp(_, _, _) => unreachable!("BinaryOp should be handled by the loop"),
        }?;

        // Unwind stack: apply operators from left to right (bottom of stack is first op)
        // Wait. `1+2+3`. Stack: `[(+, 2), (+, 3)]`. (pushed in reverse order?)
        // `((1+2)+3)`.
        // `current=1`. Stack pushes: `(+, 3)` first? No.
        // `BinaryOp(+, BinaryOp(+, 1, 2), 3)`.
        // Loop 1: `current=Op(+, 1, 2)`. Push `(+, 3)`. `current=lhs` -> `Op(+, 1, 2)`.
        // Loop 2: `current=Op(+, 1, 2)`.
        // `stack.push((+, 2))`. `current=1`.
        // Loop 3: `current=1`. Not BinaryOp. Break.
        // Stack: `[(+, 3), (+, 2)]`.
        // We pop `(+, 2)`. Result = `1 + 2`.
        // We pop `(+, 3)`. Result = `3 + 3`? No `Result + 3`.
        // Yes. `pop` returns LAST pushed item.
        // Last pushed was `(+, 2)`.
        // So we apply `(+, 2)` then `(+, 3)`. Correct order for `((1+2)+3)`.
        
        while let Some((op, rhs_expr)) = stack.pop() {
            let rhs = rhs_expr.eval(context)?;
            result = match op {
                BinaryOp::Add => result + rhs,
                BinaryOp::Sub => result - rhs,
                BinaryOp::Mul => result * rhs,
                BinaryOp::Div => result / rhs,
                BinaryOp::Mod => result % rhs,
                BinaryOp::Pow => pow(result, rhs),
            };
        }
        
        Ok(result)
    }
}

