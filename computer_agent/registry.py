from tools import ToolRegistry
from . import tools as ct

def build_computer_tools(registry: ToolRegistry):
    registry.register("computer.open_application", "Open a Windows application by installed application name.", ct.open_application,
                      schema=ct.APP_SCHEMA, risk_level="LOW", requires_confirmation=False, timeout=10)
    registry.register("computer.close_application", "Gracefully terminate a matching application process.", ct.close_app,
                      schema=ct.APP_SCHEMA, risk_level="MEDIUM", requires_confirmation=False, timeout=10)
    registry.register("computer.open_file", "Open an existing file with its associated Windows application.", ct.open_file,
                      schema=ct.PATH_SCHEMA, risk_level="MEDIUM", requires_confirmation=False, timeout=10)
    registry.register("computer.open_folder", "Open an existing folder in Windows Explorer.", ct.open_folder,
                      schema=ct.PATH_SCHEMA, risk_level="LOW", requires_confirmation=False, timeout=10)
    registry.register("computer.take_screenshot", "Capture the current primary display locally.", ct.take_screen,
                      schema=ct.EMPTY_SCHEMA, risk_level="LOW", requires_confirmation=False, timeout=10)
    registry.register("computer.read_screen", "Capture the current screen for on-demand inspection; no continuous observation.", ct.read_screen,
                      schema=ct.EMPTY_SCHEMA, risk_level="LOW", requires_confirmation=False, timeout=10)
    registry.register("computer.mouse.move", "Move the mouse to validated coordinates.", ct.mouse_move,
                      schema=ct.MOUSE_SCHEMA, risk_level="MEDIUM", requires_confirmation=False, timeout=5)
    registry.register("computer.mouse.click", "Click at validated coordinates.", ct.mouse_click,
                      schema=ct.MOUSE_SCHEMA, risk_level="MEDIUM", requires_confirmation=False, timeout=5)
    registry.register("computer.mouse.double_click", "Double-click at validated coordinates.", ct.mouse_double_click,
                      schema=ct.MOUSE_SCHEMA, risk_level="MEDIUM", requires_confirmation=False, timeout=5)
    registry.register("computer.mouse.right_click", "Right-click at validated coordinates.", ct.mouse_right_click,
                      schema=ct.MOUSE_SCHEMA, risk_level="MEDIUM", requires_confirmation=False, timeout=5)
    registry.register("computer.keyboard.type", "Type bounded text into the focused application.", ct.keyboard_type,
                      schema=ct.TYPE_SCHEMA, risk_level="MEDIUM", requires_confirmation=False, timeout=5)
    registry.register("computer.keyboard.press", "Press one validated keyboard key.", ct.keyboard_press,
                      schema=ct.PRESS_SCHEMA, risk_level="MEDIUM", requires_confirmation=False, timeout=5)
    registry.register("computer.keyboard.hotkey", "Press a validated keyboard shortcut.", ct.keyboard_hotkey,
                      schema=ct.HOTKEY_SCHEMA, risk_level="MEDIUM", requires_confirmation=False, timeout=5)
    registry.register("computer.terminal.execute", "Execute only an allowlisted non-shell terminal command; shell operators are blocked.", ct.terminal_execute,
                      schema=ct.TERMINAL_SCHEMA, risk_level="HIGH", requires_confirmation=True, timeout=30)
    return registry
