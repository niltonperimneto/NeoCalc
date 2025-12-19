import neocalc_backend

from gi.repository import GLib
import asyncio
import threading
import concurrent.futures

from neocalc_backend import DisplayManager, CalculatorManager

class CalculatorLogic:
    """
    Python wrapper for the Rust backend.
    Now instance-based so everyone gets their own sandbox.
    """

    def __init__(self):

        self._calc = neocalc_backend.Calculator()
        
        ## Create a dedicated event loop for background tasks
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._start_background_loop, daemon=True)
        self._thread.start()

    def _start_background_loop(self):
        """Runs the asyncio loop in a separate thread."""
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

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

    def evaluate_non_blocking(self, current_text: str = None, on_success=None, on_error=None):
        """
        Schedules the async evaluation on the background thread.
        on_success(result_str) and on_error(error_str) are called on the main thread via GLib.
        """
        async def _wrapper():
            try:
                result = await self.evaluate_async(current_text)
                if on_success:
                    GLib.idle_add(on_success, result)
            except Exception as e:
                error_msg = str(e)
                if on_error:
                    GLib.idle_add(on_error, error_msg)
        
        asyncio.run_coroutine_threadsafe(_wrapper(), self._loop)

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
