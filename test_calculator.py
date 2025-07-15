import unittest
import tkinter as tk
import numpy as np
import cmath
import math
from unittest.mock import MagicMock, patch

# Since the calculator is a GUI application, we need to import it and instantiate it.
# This can be tricky. For some functions, we can test the logic directly without a live GUI.
# For others, we might need to simulate GUI events.

# Assuming the main calculator code is in a file named 'calculator.py'
# and the main class is EngineeringCalculator
from calculator import EngineeringCalculator

class TestEngineeringCalculatorLogic(unittest.TestCase):
    """
    Tests for the non-GUI logic of the EngineeringCalculator.
    This includes parsing, calculations, and data transformations.
    """

    @classmethod
    def setUpClass(cls):
        # Create a dummy Tk root window once for the test class.
        # This is necessary because the EngineeringCalculator class initializes Tkinter widgets.
        # We use a "dummy" master that won't be displayed.
        cls.root = tk.Tk()
        cls.root.withdraw() # Hide the window
        cls.app = EngineeringCalculator(cls.root)

    @classmethod
    def tearDownClass(cls):
        # Destroy the dummy root window after all tests in the class have run.
        cls.root.destroy()

    def test_parse_matrix_input(self):
        """Test the logic for parsing matrix strings."""
        # Test valid matrix
        mat_str = "1,2;3,4"
        expected_mat = np.array([[1.0, 2.0], [3.0, 4.0]])
        parsed_mat = self.app.parse_matrix_input(mat_str)
        self.assertTrue(np.array_equal(parsed_mat, expected_mat))

        # Test valid vector
        vec_str = "1.5, -2, 0"
        expected_vec = np.array([1.5, -2.0, 0.0])
        parsed_vec = self.app.parse_matrix_input(vec_str, is_vector=True)
        self.assertTrue(np.array_equal(parsed_vec, expected_vec))

        # Test invalid input (should return None and display an error)
        # We can't easily test the GUI error display, but we can check for None return.
        with patch.object(self.app, '_display_matrix_error') as mock_error_display:
            invalid_mat = self.app.parse_matrix_input("1,2;3,a")
            self.assertIsNone(invalid_mat)
            mock_error_display.assert_called_once() # Check that error display was triggered

    def test_basic_arithmetic_evaluation(self):
        """Test the main display's evaluation logic for basic arithmetic."""
        self.app.display_var.set("3 * (5 - 2)")
        self.app.on_button_click('=')
        self.assertEqual(self.app.display_var.get(), "9")

        self.app.display_var.set("2^10")
        self.app.on_button_click('=')
        self.assertEqual(self.app.display_var.get(), "1024")

        self.app.display_var.set("10 / 4")
        self.app.on_button_click('=')
        self.assertEqual(self.app.display_var.get(), "2.5")

    def test_trig_functions_with_angle_modes(self):
        """Test trigonometric functions respecting the angle mode setting."""
        # Test Radians mode (default)
        self.app.angle_mode = 'radians'
        self.app.display_var.set(f"sin({np.pi/2})")
        self.app.on_button_click('=')
        self.assertAlmostEqual(float(self.app.display_var.get()), 1.0)

        # Test Degrees mode - check if the button click correctly wraps with deg2rad
        self.app.angle_mode = 'degrees'
        self.app.display_var.set("") # Clear display
        self.app.on_button_click('sin')
        self.app.display_var.set(self.app.display_var.get() + "90)") # Manually add 90 and closing paren
        # The display should now be "sin(deg2rad(90))"
        self.assertEqual(self.app.display_var.get(), "sin(deg2rad(90))")
        self.app.on_button_click('=')
        self.assertAlmostEqual(float(self.app.display_var.get()), 1.0)

    def test_user_variables(self):
        """Test creation and usage of user-defined variables."""
        self.app.user_variables = {} # Reset variables for test
        self.app._update_main_eval_context_with_user_vars()

        # Define a variable 'g'
        self.app.user_variables['g'] = 9.81
        self.app._update_main_eval_context_with_user_vars()

        # Use 'g' in a calculation
        self.app.display_var.set("10 * g")
        self.app.on_button_click('=')
        self.assertAlmostEqual(float(self.app.display_var.get()), 98.1)

        # Define a variable in terms of another
        self.app.user_variables['half_g'] = self.app.user_variables['g'] / 2
        self.app._update_main_eval_context_with_user_vars()
        self.app.display_var.set("half_g")
        self.app.on_button_click('=')
        self.assertAlmostEqual(float(self.app.display_var.get()), 4.905)

    def test_complex_number_parsing_and_formatting(self):
        """Test parsing and formatting of complex numbers."""
        # Mock the entry widget for parsing
        mock_entry = tk.Entry(self.root)

        # Test rectangular parsing
        mock_entry.insert(0, "3.5-2j")
        c_num, err = self.app.parse_complex_from_entry(mock_entry)
        self.assertIsNone(err)
        self.assertEqual(c_num, 3.5-2j)

        # Test polar parsing
        mock_entry.delete(0, tk.END)
        mock_entry.insert(0, "5∠53.13")
        c_num, err = self.app.parse_complex_from_entry(mock_entry)
        self.assertIsNone(err)
        self.assertAlmostEqual(c_num.real, 3.0, places=2)
        self.assertAlmostEqual(c_num.imag, 4.0, places=2)

        # Test formatting
        c_to_format = 2 - 3j
        rect_str = self.app.format_complex_number(c_to_format, mode="rect")
        self.assertEqual(rect_str, "2.0000 - 3.0000j")
        polar_str = self.app.format_complex_number(c_to_format, mode="polar")
        r, phi_deg = cmath.polar(c_to_format)[0], math.degrees(cmath.polar(c_to_format)[1])
        self.assertEqual(polar_str, f"{r:.4f} ∠ {phi_deg:.2f}°")

    def test_polynomial_operations(self):
        """Test polynomial operations logic."""
        p1 = np.poly1d([1, 0, -4]) # x^2 - 4
        p2 = np.poly1d([1, 2])     # x + 2

        # Test addition
        p_add = p1 + p2 # x^2 + x - 2
        self.assertTrue(np.array_equal(p_add.coeffs, [1, 1, -2]))

        # Test multiplication
        p_mul = p1 * p2 # (x^2 - 4)(x + 2) = x^3 + 2x^2 - 4x - 8
        self.assertTrue(np.allclose(p_mul.coeffs, [1, 2, -4, -8]))

        # Test roots
        roots = p1.roots
        self.assertTrue(np.allclose(sorted(roots), [-2, 2]))

    def test_unit_conversion(self):
        """Test the unit conversion logic."""
        # Test length conversion: meters to feet
        # Setup the state needed for the conversion function
        self.app.unit_category_var.set("طول")
        self.app.from_unit_var.set("متر (m)")
        self.app.to_unit_var.set("فوت (ft)")
        self.app.unit_input_value_entry = tk.Entry(self.root) # a dummy entry
        self.app.unit_input_value_entry.insert(0, "10")

        self.app.perform_unit_conversion()

        # 10 meters is approx 32.8084 feet
        result_str = self.app.unit_result_var.get()
        result_val = float(result_str.split()[0])
        self.assertAlmostEqual(result_val, 32.8084, places=4)

        # Test temperature conversion: Celsius to Fahrenheit
        self.app.unit_category_var.set("دما")
        self.app.from_unit_var.set("سانتی‌گراد (°C)")
        self.app.to_unit_var.set("فارنهایت (°F)")
        self.app.unit_input_value_entry.delete(0, tk.END)
        self.app.unit_input_value_entry.insert(0, "100")

        self.app.perform_unit_conversion()

        result_str = self.app.unit_result_var.get()
        result_val = float(result_str.split()[0])
        self.assertAlmostEqual(result_val, 212.0)

    def test_config_save_and_load(self):
        """Test saving and loading of the configuration file."""
        # Setup a known state
        self.app.calculation_history = ["1+1=2", "2*2=4"]
        self.app.user_variables = {"my_var": 123}
        self.app.decimal_precision = 8
        self.app.angle_mode = "degrees"

        # Use a temporary file for testing
        test_config_file = "test_config.json"
        self.app.config_file = test_config_file

        # Save config
        self.app.save_config()

        # Create a new calculator instance to load the config
        new_app = EngineeringCalculator(self.root)
        new_app.config_file = test_config_file
        new_app.load_config()

        # Assert that the state was loaded correctly
        self.assertEqual(new_app.calculation_history, self.app.calculation_history)
        self.assertEqual(new_app.user_variables, self.app.user_variables)
        self.assertEqual(new_app.decimal_precision, self.app.decimal_precision)
        self.assertEqual(new_app.angle_mode, self.app.angle_mode)

        # Clean up the test config file
        import os
        if os.path.exists(test_config_file):
            os.remove(test_config_file)

    def test_beam_analysis_calculation(self):
        """Test the Civil Engineering beam analysis calculation."""
        # This requires the civil engineering window and its widgets to exist.
        # We can call the creation method directly to ensure widgets are there.
        self.app.open_civil_engineering_window()

        # Set input values for a known scenario
        L, w, E, I = 5.0, 10000.0, 200e9, 8.33e-6
        self.app.beam_L_entry.delete(0, tk.END)
        self.app.beam_L_entry.insert(0, str(L))
        self.app.beam_w_entry.delete(0, tk.END)
        self.app.beam_w_entry.insert(0, str(w))
        self.app.beam_E_entry.delete(0, tk.END)
        self.app.beam_E_entry.insert(0, str(E))
        self.app.beam_I_entry.delete(0, tk.END)
        self.app.beam_I_entry.insert(0, str(I))

        # Expected results
        expected_max_moment = (w * L**2) / 8
        expected_max_deflection = (5 * w * L**4) / (384 * E * I)

        # Mock the result display to capture the output
        with patch.object(self.app, '_display_beam_result') as mock_display:
            self.app.calculate_beam_analysis()

            # Check that the display function was called
            mock_display.assert_called_once()

            # Get the string that was passed to the display function
            call_args = mock_display.call_args[0]
            result_string = call_args[0]

            # Verify the calculated values are in the output string
            self.assertIn(f"{expected_max_moment:.4g}", result_string)
            self.assertIn(f"{expected_max_deflection:.4g}", result_string)

        # Close the engineering window to avoid clutter if tests continue
        self.app.civil_eng_window.destroy()


# To run these tests from the command line:
# python -m unittest test_calculator.py
if __name__ == '__main__':
    unittest.main(verbosity=2)
