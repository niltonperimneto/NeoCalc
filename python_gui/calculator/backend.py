import neocalc_backend
import asyncio

class CalculatorLogic:
    """
    Python wrapper for the Rust backend.
    I'm staying here in Python where the types are made up and the lifetimes don't matter.
    """
    
    # Static instance. I hope Rust handles static memory correctly.
    _calc = neocalc_backend.Calculator()

    @staticmethod
    def append_text(current_text: str, new_text: str) -> str:
        """
        String manipulation. Python is good at this. Rust makes me convert String to &str back to String.
        """
        if current_text == "Error":
            current_text = ""
        
        # Convert mathematical symbols to operators
        symbol_map = {
            "÷": "/",
            "×": "*",
            "−": "-"
        }
        new_text = symbol_map.get(new_text, new_text)
        
        return current_text + new_text

    @staticmethod
    def append_function(current_text: str, func_name: str) -> str:
        """
        Appending a function. Simple. No 'Result<Option<...>>' here.
        """
        if current_text == "Error":
            current_text = ""
        return current_text + func_name + "("

    @staticmethod
    def clear() -> str:
        # Just return an empty string. No allocations... wait, everything is an allocation in Python.
        return ""

    @staticmethod
    def evaluate(current_text: str) -> str:
        """
        Calling Rust. 
        I assume it returns a string. If it panics, does the whole GUI crash?
        Let's find out.
        """
        return CalculatorLogic._calc.evaluate(current_text)

    @staticmethod
    async def evaluate_async(current_text: str) -> str:
        """
        Async evaluation. 
        I don't know how Tokio works, but await makes it look easy.
        """
        return await CalculatorLogic._calc.evaluate_async(current_text)
    
    @staticmethod
    def get_history() -> list:
        """
        Asking Rust for the history. 
        """
        return CalculatorLogic._calc.get_history()
    
    @staticmethod
    def clear_history() -> None:
        """
        Telling Rust to forget everything. 
        I wish I could forget how Move Semantics work.
        """
        CalculatorLogic._calc.clear_history()

