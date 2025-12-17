import neocalc_backend
from neocalc_backend import DisplayManager, CalculatorManager
import asyncio

class CalculatorLogic:
    """
    Python wrapper for the Rust backend.
    Now instance-based so everyone gets their own sandbox.
    """
    
    def __init__(self):
        self._calc = neocalc_backend.Calculator()

    def append_text(self, current_text: str, new_text: str) -> str:
        if current_text == "Error":
            current_text = ""
        
        symbol_map = {
            "÷": "/",
            "×": "*",
            "−": "-",
            "π": "pi",
        }
        new_text = symbol_map.get(new_text, new_text)
        
        return current_text + new_text

    def append_function(self, current_text: str, func_name: str) -> str:
        if current_text == "Error":
            current_text = ""
            
        func_map = {
            "√": "sqrt"
        }
        effective_name = func_map.get(func_name, func_name)
        
        return current_text + effective_name + "("

    def clear(self) -> str:
        return ""

    def evaluate(self, current_text: str) -> str:
        return self._calc.evaluate(current_text)

    async def evaluate_async(self, current_text: str) -> str:
        return await self._calc.evaluate_async(current_text)
    
    def get_history(self) -> list:
        return self._calc.get_history()
    
    def clear_history(self) -> None:
        self._calc.clear_history()

