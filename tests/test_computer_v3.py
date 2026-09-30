import unittest
from unittest.mock import patch

from computer_agent.schemas import ValidationError, validate_schema
from computer_agent.executor import terminal
from computer_agent.tools import APP_SCHEMA, MOUSE_SCHEMA
from computer_agent.tools import open_application

class TestComputerV3(unittest.TestCase):
    def test_valid_schema(self):
        validate_schema({"application": "Visual Studio Code"}, APP_SCHEMA)

    def test_unknown_argument_rejected(self):
        with self.assertRaises(ValidationError):
            validate_schema({"application": "Code", "shell": True}, APP_SCHEMA)

    def test_bad_coordinates_rejected(self):
        with self.assertRaises(ValidationError):
            validate_schema({"x": -1, "y": 20}, MOUSE_SCHEMA)

    def test_shell_operator_blocked(self):
        result = terminal("dir && whoami")
        self.assertFalse(result["success"])
        self.assertEqual(result["error_type"], "BlockedCommand")

    def test_unknown_command_blocked(self):
        result = terminal("format C:")
        self.assertFalse(result["success"])
        self.assertEqual(result["error_type"], "BlockedCommand")

    @patch("computer_agent.tools.require_desktop_access", return_value={
        "success": False, "status": "permission_required"
    })
    def test_desktop_permission_gate(self, _permission):
        result = open_application("notepad")
        self.assertEqual(result["status"], "permission_required")

if __name__ == "__main__":
    unittest.main()
