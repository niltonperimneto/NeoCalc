import neocalc_backend

from neocalc_backend import DisplayManager, CalculatorManager

class CalculatorLogic:
    """
    Python wrapper for the Rust backend.
    Now instance-based so everyone gets their own sandbox.
    """

    def __init__(self):

        self._calc = neocalc_backend.Calculator()

    def input(self, text: str) -> str:
        """
        Send input to Rust and return new state.
        """
        return self._calc.input(text)

    def backspace(self) -> str:
        """
        Remove last token.
        """
        return self._calc.backspace()

    def clear(self) -> str:
        """
        Clear buffer.
        """
        return self._calc.clear()

    def get_buffer(self) -> str:
        """
        Get current state.
        """
        return self._calc.get_buffer()

    def evaluate(self, current_text: str = None) -> str:
        """
        Calling Rust instance.
        """
        return self._calc.evaluate(current_text)

    async def evaluate_async(self, current_text: str = None) -> str:
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
        """
        self._calc.clear_history()

    def set_expression(self, text: str) -> None:
        """
        Set buffer directly.
        """
        self._calc.set_expression(text)
