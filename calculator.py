import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
import math
import cmath
import keyword
from tkinter import messagebox

class ToolTip:
    def __init__(self, widget):
        self.widget = widget
        self.tip_window = None
        self.id = None
        self.x = self.y = 0
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(500, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()

    def bind(self, widget, text):
        def enter(event):
            self.text = text
            self.schedule()

        def leave(event):
            self.unschedule()
            self.hidetip()

        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

class EngineeringCalculator:
    def __init__(self, master):
        self.master = master
        master.title("ماشین حساب مهندسی")
        master.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.config_file = "calculator_config.json"
        self.tooltip = ToolTip(master)

        style = ttk.Style()
        style.theme_use('clam')

        menubar = tk.Menu(master)
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="درباره ماشین حساب", command=self.show_about_dialog)
        help_menu.add_command(label="راهنمای سریع", command=self.show_quick_help_dialog)
        menubar.add_cascade(label="راهنما", menu=help_menu)
        master.config(menu=menubar)

        self.display_var = tk.StringVar()
        self.display = ttk.Entry(master, textvariable=self.display_var, font=('Arial', 20), justify='right', state='readonly')
        self.display.grid(row=0, column=0, columnspan=5, sticky="nsew", padx=5, pady=5)
        self.tooltip.bind(self.display, "نمایشگر ورودی و خروجی محاسبات")

        self.calculation_history = []
        self.user_variables = {}
        self.decimal_precision = 10
        self.angle_mode = "radians"

        self.load_config()
        self._initialize_eval_globals()

        buttons = [
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('/', 1, 3), ('C', 1, 4),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('*', 2, 3), ('AC', 2, 4),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('-', 3, 3), ('(', 3, 4),
            ('0', 4, 0), ('.', 4, 1), ('=', 4, 2), ('+', 4, 3), (')', 4, 4),
            ('sin', 5, 0), ('cos', 5, 1), ('tan', 5, 2), ('log', 5, 3), ('ln', 5, 4),
            ('sqrt', 6, 0), ('^', 6, 1), ('pi', 6, 2), ('e', 6, 3), ('Plot', 6, 4),
            ('Matrix Ops', 7, 0, 1), ('Solve Eq', 7, 1, 1), ('Calculus', 7, 2, 1),
            ('Interpolate', 7, 3, 1), ('Curve Fit', 7, 4, 1),
            ('Bitwise', 8, 0, 1), ('Units', 8, 1, 1), ('Stats', 8, 2, 1),
            ('Complex', 8, 3, 1), ('SpecialFunc', 8, 4, 1),
            ('SysNonlinearEq', 9, 0, 1), ('Optimize', 9, 1, 1),
            ('Polynomials', 9, 2, 1), ('History', 9, 3, 1), ('Vars', 9, 4, 1),
            ('Settings', 10, 0, 1), ('ProbDist', 10, 1, 1), ('FFT', 10, 2, 1),
            ('CivilEng', 10, 3, 2)
        ]

        for (text, r_grid, c_grid, *span_info) in buttons:
            colspan = span_info[0] if span_info else 1
            action = self.get_action_for_button(text)
            button = ttk.Button(master, text=text, command=action)
            button.grid(row=r_grid, column=c_grid, columnspan=colspan, sticky="nsew", padx=2, pady=2)

            tooltip_text = self.get_tooltip_for_button(text)
            if tooltip_text:
                self.tooltip.bind(button, tooltip_text)

        max_grid_row_used = 10
        for i in range(max_grid_row_used + 1):
            master.grid_rowconfigure(i, weight=1)
        for i in range(5):
            master.grid_columnconfigure(i, weight=1)

    def get_action_for_button(self, text):
        actions = {
            'Matrix Ops': self.open_matrix_window,
            'Plot': self.open_plot_window,
            'Solve Eq': self.open_solve_equation_window,
            'Calculus': self.open_calculus_window,
            'Interpolate': self.open_interpolation_window,
            'Curve Fit': self.open_curve_fit_window,
            'Bitwise': self.open_bitwise_window,
            'Units': self.open_units_window,
            'Stats': self.open_stats_window,
            'Complex': self.open_complex_calculator_window,
            'SpecialFunc': self.open_special_functions_window,
            'SysNonlinearEq': self.open_sys_nonlinear_eq_window,
            'Optimize': self.open_optimization_window,
            'Polynomials': self.open_polynomials_window,
            'History': self.open_history_window,
            'Vars': self.open_variables_window,
            'Settings': self.open_settings_window,
            'ProbDist': self.open_prob_dist_window,
            'FFT': self.open_fourier_analysis_window,
            'CivilEng': self.open_civil_engineering_window
        }
        return actions.get(text, lambda t=text: self.on_button_click(t))

    def on_button_click(self, char):
        current_text = self.display_var.get()
        if char == 'C':
            self.display_var.set(current_text[:-1])
        elif char == 'AC':
            self.display_var.set("")
        elif char == '=':
            self.evaluate_expression()
        elif char in ['sin', 'cos', 'tan']:
            self.handle_trig_button(char, current_text)
        elif char in ['ln', 'log', 'sqrt']:
            self.display_var.set(current_text + f"{char}(")
        else:
            self.append_to_display(char, current_text)

    def evaluate_expression(self):
        try:
            expression = self.display_var.get().replace('^', '**')
            result = eval(expression, self.eval_globals, {})
            result_str = self.format_result(result)
            self.display_var.set(result_str)
            self.add_to_history(expression, result_str)
        except Exception as e:
            self.display_var.set("Error")
            self.add_to_history(self.display_var.get(), "Error: " + str(e))

    def handle_trig_button(self, func, current_text):
        if self.angle_mode == 'degrees':
            self.display_var.set(current_text + f"{func}(deg2rad(")
        else:
            self.display_var.set(current_text + f"{func}(")

    def append_to_display(self, char, current_text):
        if char in ['/', '*', '-', '+', '^'] and (not current_text or current_text[-1] in ['/', '*', '-', '+', '^']):
            if char == '-' and (not current_text or current_text[-1] in ['/', '*', '(', '^']):
                 self.display_var.set(current_text + str(char))
        elif char == '.' and '.' in self._get_last_number(current_text):
            pass
        else:
            self.display_var.set(current_text + str(char))

    def format_result(self, result):
        precision = getattr(self, 'decimal_precision', 10)
        if isinstance(result, (int, float)):
            return f"{result:.{precision}g}"
        elif isinstance(result, complex):
            real_part = f"{result.real:.{precision}g}"
            imag_part = f"{result.imag:.{precision}g}"
            return f"{real_part}{'+' if result.imag >= 0 else ''}{imag_part}j"
        return str(result)

    def _get_last_number(self, text):
        for op in ['+', '-', '*', '/', '(', ')', '^']:
            text = text.replace(op, ' ')
        parts = text.split()
        return parts[-1] if parts else ""

    def add_to_history(self, expression, result_str):
        history_entry = f"{expression} = {result_str}"
        self.calculation_history.append(history_entry)
        if len(self.calculation_history) > 50:
            self.calculation_history.pop(0)
        if hasattr(self, 'history_listbox') and self.history_listbox.winfo_exists():
            self.history_listbox.insert(0, history_entry)
            if self.history_listbox.size() > 50:
                self.history_listbox.delete(tk.END)

    def load_config(self):
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                self.calculation_history = config.get("history", [])
                self.user_variables = config.get("variables", {})
                self.decimal_precision = config.get("precision", 10)
                self.angle_mode = config.get("angle_mode", "radians")
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    def save_config(self):
        config = {
            "history": self.calculation_history,
            "variables": self.user_variables,
            "precision": self.decimal_precision,
            "angle_mode": self.angle_mode
        }
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)

    def on_closing(self):
        if messagebox.askokcancel("خروج", "آیا می‌خواهید از برنامه خارج شوید؟\nتمام تنظیمات و تاریخچه فعلی ذخیره خواهند شد."):
            self.save_config()
            self.master.destroy()

    def show_about_dialog(self):
        messagebox.showinfo("درباره ماشین حساب", "ماشین حساب مهندسی پیشرفته نسخه 1.0")

    def show_quick_help_dialog(self):
        messagebox.showinfo("راهنمای سریع", "نکات و راهنمایی‌های استفاده از ماشین حساب.")

    def get_tooltip_for_button(self, button_text):
        tooltips = {
            "Matrix Ops": "عملیات ماتریسی", "Solve Eq": "حل معادله",
            "Calculus": "محاسبات دیفرانسیل و انتگرال", "Plot": "رسم نمودار",
            "C": "پاک کردن آخرین کاراکتر", "AC": "پاک کردن کل نمایشگر",
            "=": "محاسبه"
        }
        return tooltips.get(button_text, "")

    def _initialize_eval_globals(self):
        self.base_eval_globals = {
            "np": np, "cmath": cmath, "math": math,
            "sin": np.sin, "cos": np.cos, "tan": np.tan,
            "asin": np.arcsin, "acos": np.arccos, "atan": np.arctan,
            "sinh": np.sinh, "cosh": np.cosh, "tanh": np.tanh,
            "asinh": np.arcsinh, "acosh": np.arccosh, "atanh": np.arctanh,
            "ln": np.log, "log": np.log10, "log2": np.log2,
            "exp": np.exp, "sqrt": np.sqrt, "cbrt": np.cbrt,
            "abs": abs, "factorial": math.factorial,
            "gamma": math.gamma, "pi": np.pi, "e": np.e, "j": 1j,
            "deg2rad": np.deg2rad, "rad2deg": np.rad2deg,
        }
        self.eval_globals = self.base_eval_globals.copy()
        self.eval_globals.update(self.user_variables)

    # Placeholder for all window-opening methods
    def open_matrix_window(self): messagebox.showinfo("Info", "Matrix Operations window placeholder")
    def open_plot_window(self): messagebox.showinfo("Info", "Plotting window placeholder")
    def open_solve_equation_window(self): messagebox.showinfo("Info", "Equation Solver window placeholder")
    def open_calculus_window(self): messagebox.showinfo("Info", "Calculus window placeholder")
    def open_interpolation_window(self): messagebox.showinfo("Info", "Interpolation window placeholder")
    def open_curve_fit_window(self): messagebox.showinfo("Info", "Curve Fitting window placeholder")
    def open_bitwise_window(self): messagebox.showinfo("Info", "Bitwise Operations window placeholder")
    def open_units_window(self): messagebox.showinfo("Info", "Unit Conversion window placeholder")
    def open_stats_window(self): messagebox.showinfo("Info", "Statistics window placeholder")
    def open_complex_calculator_window(self): messagebox.showinfo("Info", "Complex Calculator window placeholder")
    def open_special_functions_window(self): messagebox.showinfo("Info", "Special Functions window placeholder")
    def open_sys_nonlinear_eq_window(self): messagebox.showinfo("Info", "System of Nonlinear Equations window placeholder")
    def open_optimization_window(self): messagebox.showinfo("Info", "Optimization window placeholder")
    def open_polynomials_window(self): messagebox.showinfo("Info", "Polynomials window placeholder")
    def open_history_window(self): messagebox.showinfo("Info", "History window placeholder")
    def open_variables_window(self): messagebox.showinfo("Info", "Variables window placeholder")
    def open_settings_window(self): messagebox.showinfo("Info", "Settings window placeholder")
    def open_prob_dist_window(self): messagebox.showinfo("Info", "Probability Distributions window placeholder")
    def open_fourier_analysis_window(self): messagebox.showinfo("Info", "Fourier Analysis window placeholder")
    def open_civil_engineering_window(self): messagebox.showinfo("Info", "Civil Engineering window placeholder")


if __name__ == '__main__':
    root = tk.Tk()
    app = EngineeringCalculator(root)
    root.mainloop()
