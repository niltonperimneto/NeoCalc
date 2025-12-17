import neocalc_backend
import asyncio

class CalculatorLogic:
    """
    Python wrapper for the Rust backend.
    I'm staying here in Python where the types are made up and the lifetimes don't matter.
    """
    
    
    def __init__(self):
        # Create a fresh Rust backend instance for this logic controller
        self._calc = neocalc_backend.Calculator()

    def append_text(self, current_text: str, new_text: str) -> str:
        """
        String manipulation.
        """
        if current_text == "Error":
            current_text = ""
        
        # Convert mathematical symbols to operators/constants
        symbol_map = {
            "÷": "/",
            "×": "*",
            "−": "-",
            "π": "pi",
        }
        new_text = symbol_map.get(new_text, new_text)
        
        return current_text + new_text

    def append_function(self, current_text: str, func_name: str) -> str:
        """
        Appending a function.
        """
        if current_text == "Error":
            current_text = ""
            
        # Map function symbols if needed
        func_map = {
            "√": "sqrt"
        }
        effective_name = func_map.get(func_name, func_name)
        
        return current_text + effective_name + "("

    def clear(self) -> str:
        # Just return an empty string. No allocations... wait, everything is an allocation in Python.
        return ""

    def evaluate(self, current_text: str) -> str:
        """
        Calling Rust instance.
        """
        return self._calc.evaluate(current_text)

    async def evaluate_async(self, current_text: str) -> str:
        """
        Async evaluation. 
        I don't know how Tokio works, but await makes it look easy.
        """
        return await self._calc.evaluate_async(current_text)
    
    def get_history(self) -> list:
        """
        Asking Rust for the history. 
        """
        return self._calc.get_history()
    
    def clear_history(self) -> None:
        """
        Telling Rust to forget everything. 
        I wish I could forget how Move Semantics work.
        """
        self._calc.clear_history()
