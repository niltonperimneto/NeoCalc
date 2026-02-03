import neocalc_backend

from gi.repository import GLib
import asyncio
import threading

from neocalc_backend import DisplayManager, CalculatorManager

class CalculatorLogic:
    """
    Python wrapper for the Rust backend.
    Manages calculator state and async execution.
    """

    def __init__(self):

        self._calc = neocalc_backend.Calculator()
        
        # Create a dedicated event loop for background tasks.
        # GTK runs its own main loop on the main thread. To avoid blocking the UI
        # during heavy calculations, we run a separate asyncio loop in a background thread.
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
        Evaluate expression synchronously.
        """
        return self._calc.evaluate(current_text)

    async def evaluate_async(self, current_text: str = None) -> str:
        """
        Evaluate expression asynchronously to prevent blocking the UI thread.
        """
        return await self._calc.evaluate_async(current_text)

    def evaluate_non_blocking(self, current_text: str = None, on_success=None, on_error=None):
        """
        Schedules the async evaluation on the background thread.
        on_success(result_str) and on_error(error_str) are called on the main thread via GLib.
        """
        async def _wrapper():
            try:
                # Run the calculation in the background
                result = await self.evaluate_async(current_text)
                
                # Schedule the success callback on the main GTK thread
                # This ensures thread safety when updating the UI
                if on_success:
                    GLib.idle_add(on_success, result)
            except Exception as e:
                error_msg = str(e)
                # Schedule the error callback on the main GTK thread
                if on_error:
                    GLib.idle_add(on_error, error_msg)
        
        # Submit the coroutine to the background loop
        asyncio.run_coroutine_threadsafe(_wrapper(), self._loop)

    def get_history(self) -> list:
        """
        Retrieve calculation history.
        """
        return self._calc.get_history()

    def clear_history(self) -> None:
        """
        Clear calculation history.
        """
        self._calc.clear_history()

    def set_expression(self, text: str) -> None:
        """
        Set buffer directly.
        """
        self._calc.set_expression(text)

    def get_variables(self) -> dict:
        """
        Get all defined variables.
        """
        return self._calc.get_variables()

    def set_decimal_mode(self, enabled: bool) -> None:
        """
        Enable or disable decimal display mode.
        """
        self._calc.set_decimal_mode(enabled)
