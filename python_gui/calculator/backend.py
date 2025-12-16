import neocalc_backend
import asyncio

class CalculatorLogic:
    """
    Handles higher-level calculator logic, such as input processing and result formatting.
    Decouples UI events from state manipulation.
    """

    @staticmethod
    def append_text(current_text: str, new_text: str) -> str:
        """
        Appends text to the current expression, handling 'Error' state.
        """
        if current_text == "Error":
            return new_text
        return current_text + new_text

    @staticmethod
    def append_function(current_text: str, func_name: str) -> str:
        """
        Appends a function call (e.g., 'sin(') to the current expression.
        """
        if current_text == "Error":
            current_text = ""
        return current_text + func_name + "("

    @staticmethod
    def clear() -> str:
        return ""

    @staticmethod
    def evaluate(current_text: str) -> str:
        """
        Evaluates the current expression string and returns the formatted result string or 'Error'.
        """
        """
        Evaluates the current expression string using the Rust backend.
        Returns the formatted result string or 'Error'.
        """
        return neocalc_backend.evaluate(current_text)

    @staticmethod
    async def evaluate_async(current_text: str) -> str:
        """
        Asynchronously evaluates the expression using the Rust backend.
        """
        return await neocalc_backend.evaluate_async(current_text)
