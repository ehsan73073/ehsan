import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class EngineeringCalculator:
    def __init__(self, master):
        self.master = master
        master.title("ماشین حساب مهندسی")
        master.protocol("WM_DELETE_WINDOW", self.on_closing) # Handle window close

        # --- Configuration File ---
        self.config_file = "calculator_config.json"

        # --- Tooltip Helper ---
        self.tooltip = ToolTip(master) # Initialize tooltip helper

        # Styling
        style = ttk.Style()
        style.theme_use('clam') # Using a modern theme

        # --- Menu Bar ---
        menubar = tk.Menu(master)
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="درباره ماشین حساب", command=self.show_about_dialog)
        help_menu.add_command(label="راهنمای سریع", command=self.show_quick_help_dialog) # Placeholder
        menubar.add_cascade(label="راهنما", menu=help_menu)
        master.config(menu=menubar)


        # Entry widget to display input/output
        self.display_var = tk.StringVar()
        self.display = ttk.Entry(master, textvariable=self.display_var, font=('Arial', 20), justify='right', state='readonly')
        self.display.grid(row=0, column=0, columnspan=5, sticky="nsew", padx=5, pady=5)
        self.tooltip.bind(self.display, "نمایشگر ورودی و خروجی محاسبات")

        # Initialize history and user variables attributes
        self.calculation_history = []
        self.user_variables = {}
        # Default settings (will be overridden by loaded config if available)
        self.decimal_precision = 10
        self.angle_mode = "radians"

        self.load_config() # Load config before initializing eval_globals which might use them

        self._initialize_eval_globals() # Setup the initial context for eval on main display

        # Button layout
        buttons = [
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('/', 1, 3), ('C', 1, 4),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('*', 2, 3), ('AC', 2, 4),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('-', 3, 3), ('(', 3, 4),
            ('0', 4, 0), ('.', 4, 1), ('=', 4, 2), ('+', 4, 3), (')', 4, 4),
            ('sin', 5, 0), ('cos', 5, 1), ('tan', 5, 2), ('log', 5, 3), ('ln', 5, 4),
            ('sqrt', 6, 0), ('^', 6, 1), ('pi', 6, 2), ('e', 6, 3), ('Plot', 6, 4), # Row 6
            ('sqrt', 6, 0), ('^', 6, 1), ('pi', 6, 2), ('e', 6, 3), ('Plot', 6, 4),
            ('Matrix Ops', 7, 0, 1), ('Solve Eq', 7, 1, 1), ('Calculus', 7, 2, 1), # Adjusted spans
            ('Interpolate', 7, 3, 1), ('Curve Fit', 7, 4, 1),
            ('Bitwise', 8, 0, 1), ('Units', 8, 1, 1), ('Stats', 8, 2, 1),
            ('Complex', 8, 3, 1), ('SpecialFunc', 8, 4, 1),
            ('SysNonlinearEq', 9, 0, 1), ('Optimize', 9, 1, 1),
            ('Polynomials', 9, 2, 1), ('History', 9, 3, 1), ('Vars', 9, 4, 1),
            ('Settings', 10, 0, 1), ('ProbDist', 10, 1, 2) # Added ProbDist, adjusted Settings span
            # Row 10: Settings(1), ProbDist(2), Empty(1), Empty(1)
        ]

        # Main display
        self.display_var = tk.StringVar()
        self.display = ttk.Entry(master, textvariable=self.display_var, font=('Arial', 20), justify='right', state='readonly')
        self.display.grid(row=0, column=0, columnspan=5, sticky="nsew", padx=5, pady=5)


        button_row_offset = 1 # Start buttons from row 1 since display is at row 0

        # Dynamically create buttons
        # Current button layout:
        # Row 1: 7 8 9 / C
        # Row 2: 4 5 6 * AC
        # Row 3: 1 2 3 - (
        # Row 4: 0 . = + )
        # Row 5: sin cos tan log ln
        # Row 6: sqrt ^ pi e Plot
        # Row 7: Matrix SolveEq Calculus Interpolate CurveFit
        # Row 8 (Future): Stats, Units, ...

        # We need to adjust the grid row indices in the buttons list if display is row 0
        # The r_idx in `buttons` list should correspond to the actual grid row.
        # Let's assume display is row 0, first row of buttons is row 1.
        # So, the 'r' values in the buttons list are effectively 1-based indices for button rows.

        for (text, r_grid, c_grid, *span_info) in buttons: # r_grid is now direct grid row for button
            colspan = span_info[0] if span_info else 1

            action = None
            if text == 'Matrix Ops':
                action = self.open_matrix_window
            elif text == 'Plot':
                action = self.open_plot_window
            elif text == 'Solve Eq':
                action = self.open_solve_equation_window
            elif text == 'Calculus':
                action = self.open_calculus_window
            elif text == 'Interpolate':
                action = self.open_interpolation_window
            elif text == 'Curve Fit':
                action = self.open_curve_fit_window
            elif text == 'Bitwise':
                action = self.open_bitwise_window
            elif text == 'Units':
                action = self.open_units_window
            elif text == 'Stats':
                action = self.open_stats_window
            elif text == 'Complex':
                action = self.open_complex_calculator_window
            elif text == 'SpecialFunc':
                action = self.open_special_functions_window
            elif text == 'SysNonlinearEq':
                action = self.open_sys_nonlinear_eq_window
            elif text == 'Optimize':
                action = self.open_optimization_window
            elif text == 'Polynomials':
                action = self.open_polynomials_window
            elif text == 'History':
                action = self.open_history_window
            elif text == 'Vars':
                action = self.open_variables_window
            elif text == 'Settings':
                action = self.open_settings_window
            elif text == 'ProbDist':
                action = self.open_prob_dist_window
            else: # Standard calculator buttons
                action = lambda t=text: self.on_button_click(t)

            button = ttk.Button(master, text=text, command=action)
            button.grid(row=r_grid, column=c_grid, columnspan=colspan, sticky="nsew", padx=2, pady=2)

            # Add tooltip to functional buttons
            tooltip_text = self.get_tooltip_for_button(text)
            if tooltip_text:
                self.tooltip.bind(button, tooltip_text)


        # Configure row/column weights for responsiveness
        max_grid_row_used = 8 # Updated due to new row of buttons
        for i in range(max_grid_row_used + 1): # Including display row 0
            master.grid_rowconfigure(i, weight=1)
        for i in range(5): # 5 columns for buttons
            master.grid_columnconfigure(i, weight=1)

    def on_button_click(self, char):
        if char == 'C':
            current_text = self.display_var.get()
            self.display_var.set(current_text[:-1])
        elif char == 'AC':
            self.display_var.set("")
        elif char == '=':
            try:
                # Replace math functions for eval
                expression = self.display_var.get().replace('^', '**')
                # Handle specific math functions that need np prefix
                expression = expression.replace('ln(', 'np.log(')
                expression = expression.replace('log(', 'np.log10(')
                expression = expression.replace('sin(', 'np.sin(')
                expression = expression.replace('cos(', 'np.cos(')
                expression = expression.replace('tan(', 'np.tan(')
                expression = expression.replace('sqrt(', 'np.sqrt(')
                expression = expression.replace('pi', str(np.pi))
                expression = expression.replace('e', str(np.e))
                # Ensure radians for trig functions if not specified, though direct eval might assume it
                # For simplicity, we'll rely on np functions' default (radians)

                # Use the eval_globals context for evaluation
                if not hasattr(self, 'eval_globals'): self._initialize_eval_globals()

                result = eval(expression, self.eval_globals, {}) # Provide globals, empty locals
                result_str = str(round(result, 10)) if isinstance(result, (int, float, complex)) else str(result)
                self.display_var.set(result_str)
                self.add_to_history(expression, result_str) # Add to history
            except Exception as e:
                self.display_var.set("Error")
                self.add_to_history(expression, "Error") # Add error to history too
        else:
            current_text = self.display_var.get()
            # Avoid multiple operators or leading operators issues (basic handling)
            if char in ['/', '*', '-', '+', '^'] and (not current_text or current_text[-1] in ['/', '*', '-', '+', '^']):
                if char == '-' and (not current_text or current_text[-1] in ['/', '*', '(', '^']): # Allow negative numbers
                     self.display_var.set(current_text + str(char))
                # else: skip adding operator if it's redundant or badly placed
            elif char == '.' and '.' in self._get_last_number(current_text):
                pass # Avoid multiple decimal points in one number
            else:
                self.display_var.set(current_text + str(char))

    def _get_last_number(self, text):
        # Helper to get the last number in the expression for decimal point validation
        for op in ['+', '-', '*', '/', '(', ')', '^']:
            text = text.replace(op, ' ')
        parts = text.split()
        return parts[-1] if parts else ""

    def open_matrix_window(self):
        self.matrix_window = tk.Toplevel(self.master)
        self.matrix_window.title("عملیات ماتریس و حل دستگاه معادلات")
        self.matrix_window.geometry("700x550") # Adjusted size for new features

        # --- Matrix Input / Coefficient Matrix ---
        input_frame = ttk.LabelFrame(self.matrix_window, text="ورودی ماتریس ها / ماتریس ضرایب (A)")
        input_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(input_frame, text="ماتریس A (هر ردیف با سمی‌کالن ';'، هر عنصر با کاما ',' جدا شود):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.matrix_a_entry = ttk.Entry(input_frame, width=40)
        self.matrix_a_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.matrix_a_entry.insert(0, "1,2;3,4") # Example

        ttk.Label(input_frame, text="ماتریس B (اختیاری، برای عملیات دو ماتریسی):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.matrix_b_entry = ttk.Entry(input_frame, width=40)
        self.matrix_b_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.matrix_b_entry.insert(0, "5,6;7,8") # Example for matrix B

        ttk.Label(input_frame, text="بردار ثابت (b) (برای حل دستگاه Ax=b، عناصر با کاما ',' جدا شوند):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.vector_b_entry = ttk.Entry(input_frame, width=40)
        self.vector_b_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.vector_b_entry.insert(0, "7,10") # Example for vector b

        input_frame.grid_columnconfigure(1, weight=1) # Make entry expand


        # --- Operations ---
        ops_frame = ttk.LabelFrame(self.matrix_window, text="عملیات")
        ops_frame.pack(padx=10, pady=5, fill="x")

        self.matrix_op_var = tk.StringVar()
        self.matrix_ops_list = [
            "جمع (A+B)", "تفریق (A-B)", "ضرب (A*B)",
            "دترمینان (A)", "معکوس (A)", "حل دستگاه (Ax=b)",
            "ترانهاده (A)", "مقادیر ویژه (A)", "بردارهای ویژه (A)",
            "تجزیه SVD (A)", "توان ماتریس (A^n)", "رتبه (A)", "نرم (A)"
        ]
        # Frame for OptionMenu and Power Entry (if needed)
        op_control_frame = ttk.Frame(ops_frame)
        op_control_frame.pack(side="left", padx=5, pady=5)

        self.op_menu = ttk.OptionMenu(op_control_frame, self.matrix_op_var, self.matrix_ops_list[0], *self.matrix_ops_list, command=self.on_matrix_op_change)
        self.op_menu.pack(side="left")

        self.power_n_label = ttk.Label(op_control_frame, text=" n:")
        self.power_n_entry = ttk.Entry(op_control_frame, width=3)

        # Hide power entry initially
        # self.power_n_label.pack_forget()
        # self.power_n_entry.pack_forget()


        calc_button = ttk.Button(ops_frame, text="محاسبه", command=self.calculate_matrix_op)
        calc_button.pack(side="left", padx=5, pady=5)

        # --- Result Display ---
        result_frame = ttk.LabelFrame(self.matrix_window, text="نتیجه")
        result_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.matrix_result_text = tk.Text(result_frame, height=15, width=60, state='disabled', font=('Arial', 12)) # Increased height
        self.matrix_result_text.pack(padx=5, pady=5, fill="both", expand=True)

    def parse_matrix_input(self, matrix_str, is_vector=False):
        try:
            if is_vector:
                return np.array(list(map(float, matrix_str.split(','))))
            else:
                rows = matrix_str.split(';')
                matrix = []
                for row in rows:
                    matrix.append(list(map(float, row.split(','))))
                return np.array(matrix)
        except Exception as e:
            error_msg = f"خطا در پارس بردار: {e}\nورودی نمونه: 1,2,3" if is_vector else f"خطا در پارس ماتریس: {e}\nورودی نمونه: 1,2;3,4"
            self._display_matrix_error(error_msg)
            return None

    def _display_matrix_error(self, message):
        self.matrix_result_text.config(state='normal')
        self.matrix_result_text.delete('1.0', tk.END)
        self.matrix_result_text.insert(tk.END, message)
        self.matrix_result_text.config(state='disabled')

    def _display_matrix_result(self, result_matrix):
        self.matrix_result_text.config(state='normal')
        self.matrix_result_text.delete('1.0', tk.END)
        if isinstance(result_matrix, np.ndarray):
            self.matrix_result_text.insert(tk.END, str(result_matrix))
        else: # For scalar results like determinant
            self.matrix_result_text.insert(tk.END, str(result_matrix))
        self.matrix_result_text.config(state='disabled')

    def on_matrix_op_change(self, selected_op):
        if selected_op == "توان ماتریس (A^n)":
            self.power_n_label.pack(side="left", padx=(5,0))
            self.power_n_entry.pack(side="left")
            self.power_n_entry.insert(0, "2") # Default power
        else:
            self.power_n_label.pack_forget()
            self.power_n_entry.pack_forget()

    def calculate_matrix_op(self):
        op = self.matrix_op_var.get()
        mat_a_str = self.matrix_a_entry.get()
        mat_b_str = self.matrix_b_entry.get()
        vec_b_str = self.vector_b_entry.get()

        mat_a = self.parse_matrix_input(mat_a_str)
        if mat_a is None: return

        mat_b = None
        if op in ["جمع (A+B)", "تفریق (A-B)", "ضرب (A*B)"]:
            if not mat_b_str:
                self._display_matrix_error("ماتریس B برای این عملیات مورد نیاز است.")
                return
            mat_b = self.parse_matrix_input(mat_b_str)
            if mat_b is None: return

        vec_b = None
        if op == "حل دستگاه (Ax=b)":
            if not vec_b_str:
                self._display_matrix_error("بردار b برای حل دستگاه مورد نیاز است.")
                return
            vec_b = self.parse_matrix_input(vec_b_str, is_vector=True)
            if vec_b is None: return


        try:
            result = None
            if op == "جمع (A+B)":
                if mat_a.shape != mat_b.shape:
                    self._display_matrix_error("برای جمع، ابعاد ماتریس ها باید یکسان باشد.")
                    return
                result = mat_a + mat_b
            elif op == "تفریق (A-B)":
                if mat_a.shape != mat_b.shape:
                    self._display_matrix_error("برای تفریق، ابعاد ماتریس ها باید یکسان باشد.")
                    return
                result = mat_a - mat_b
            elif op == "ضرب (A*B)":
                if mat_a.shape[1] != mat_b.shape[0]:
                    self._display_matrix_error("برای ضرب ماتریسی، تعداد ستون های ماتریس A باید با تعداد سطرهای ماتریس B برابر باشد.")
                    return
                result = np.dot(mat_a, mat_b)
            elif op == "دترمینان (A)":
                if mat_a.shape[0] != mat_a.shape[1]:
                    self._display_matrix_error("دترمینان فقط برای ماتریس های مربعی تعریف می شود.")
                    return
                result = np.linalg.det(mat_a)
            elif op == "معکوس (A)":
                if mat_a.shape[0] != mat_a.shape[1]:
                    self._display_matrix_error("معکوس فقط برای ماتریس های مربعی تعریف می شود.")
                    return
                try:
                    result = np.linalg.inv(mat_a)
                except np.linalg.LinAlgError:
                    self._display_matrix_error("ماتریس معکوس پذیر نیست (دترمینان صفر است) یا ماتریس مربعی نیست.")
                    return
            elif op == "حل دستگاه (Ax=b)":
                if mat_a.shape[0] != mat_a.shape[1]:
                    self._display_matrix_error("ماتریس ضرایب (A) باید مربعی باشد.")
                    return
                if mat_a.shape[0] != vec_b.shape[0]:
                    self._display_matrix_error("تعداد سطرهای ماتریس ضرایب (A) باید با تعداد عناصر بردار (b) برابر باشد.")
                    return
                try:
                    # Check for singularity before solving
                    if np.linalg.det(mat_a) == 0:
                         self._display_matrix_error("ماتریس ضرایب (A) منفرد است (دترمینان صفر)، دستگاه جواب یکتا ندارد.")
                         return
                    result = np.linalg.solve(mat_a, vec_b)
                except np.linalg.LinAlgError:
                    self._display_matrix_error("امکان حل دستگاه وجود ندارد (ممکن است ماتریس منفرد باشد).")
                    return
            elif op == "ترانهاده (A)":
                result = mat_a.T
            elif op == "مقادیر ویژه (A)":
                if mat_a.shape[0] != mat_a.shape[1]:
                    self._display_matrix_error("مقادیر ویژه فقط برای ماتریس های مربعی تعریف می شود.")
                    return
                try:
                    eigenvalues = np.linalg.eigvals(mat_a)
                    result = eigenvalues
                except np.linalg.LinAlgError:
                    self._display_matrix_error("خطا در محاسبه مقادیر ویژه.")
                    return
            elif op == "بردارهای ویژه (A)":
                if mat_a.shape[0] != mat_a.shape[1]:
                    self._display_matrix_error("بردارهای ویژه فقط برای ماتریس های مربعی تعریف می شود.")
                    return
                try:
                    eigenvalues, eigenvectors = np.linalg.eig(mat_a)
                    # Formatting result for display
                    res_str = "مقادیر ویژه:\n" + np.array2string(eigenvalues, precision=4, suppress_small=True)
                    res_str += "\n\nبردارهای ویژه (هر ستون یک بردار ویژه):\n" + np.array2string(eigenvectors, precision=4, suppress_small=True)
                    self._display_matrix_result(res_str) # Display directly as string
                    return # Avoid default result display
                except np.linalg.LinAlgError:
                    self._display_matrix_error("خطا در محاسبه بردارهای ویژه.")
                    return
            elif op == "تجزیه SVD (A)":
                try:
                    U, s, Vh = np.linalg.svd(mat_a)
                    res_str = "ماتریس U:\n" + np.array2string(U, precision=4, suppress_small=True)
                    res_str += "\n\nمقادیر منفرد (s):\n" + np.array2string(s, precision=4, suppress_small=True)
                    res_str += "\n\nماتریس Vh (ترانهاده V):\n" + np.array2string(Vh, precision=4, suppress_small=True)
                    self._display_matrix_result(res_str) # Display directly as string
                    return # Avoid default result display
                except np.linalg.LinAlgError:
                     self._display_matrix_error("خطا در تجزیه SVD.")
                     return
            elif op == "توان ماتریس (A^n)":
                if mat_a.shape[0] != mat_a.shape[1]:
                    self._display_matrix_error("توان ماتریس فقط برای ماتریس های مربعی تعریف می شود.")
                    return
                try:
                    n_str = self.power_n_entry.get()
                    if not n_str:
                        self._display_matrix_error("مقدار توان (n) را وارد کنید.")
                        return
                    n = int(n_str)
                    result = np.linalg.matrix_power(mat_a, n)
                except ValueError:
                    self._display_matrix_error("توان (n) باید یک عدد صحیح باشد.")
                    return
                except np.linalg.LinAlgError:
                    self._display_matrix_error("خطا در محاسبه توان ماتریس.")
                    return
            elif op == "رتبه (A)":
                result = np.linalg.matrix_rank(mat_a)
            elif op == "نرم (A)": # Frobenius norm by default
                result = np.linalg.norm(mat_a)


            if result is not None: # This will be skipped if custom display was called
                self._display_matrix_result(result)

        except Exception as e:
            self._display_matrix_error(f"خطا در محاسبه: {e}")


    def open_plot_window(self):
        self.plot_window = tk.Toplevel(self.master)
        self.plot_window.title("رسم نمودار دو بعدی و سه بعدی")
        self.plot_window.geometry("800x700")

        # --- Input Frame ---
        input_frame = ttk.LabelFrame(self.plot_window, text="ورودی تابع و تنظیمات نمودار")
        input_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(input_frame, text="نوع نمودار:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.plot_type_var = tk.StringVar(value="2D")
        plot_type_2d = ttk.Radiobutton(input_frame, text="دو بعدی (y = f(x))", variable=self.plot_type_var, value="2D", command=self.toggle_plot_inputs)
        plot_type_2d.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        plot_type_3d = ttk.Radiobutton(input_frame, text="سه بعدی (z = f(x, y))", variable=self.plot_type_var, value="3D", command=self.toggle_plot_inputs)
        plot_type_3d.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        # --- 2D Inputs ---
        self.frame_2d_inputs = ttk.Frame(input_frame)
        self.frame_2d_inputs.grid(row=1, column=0, columnspan=3, sticky="ew")

        ttk.Label(self.frame_2d_inputs, text="تابع f(x):").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.func_entry_2d = ttk.Entry(self.frame_2d_inputs, width=40)
        self.func_entry_2d.grid(row=0, column=1, columnspan=2, padx=5, pady=2, sticky="ew")
        self.func_entry_2d.insert(0, "np.sin(x)")

        ttk.Label(self.frame_2d_inputs, text="X از:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.x_min_entry = ttk.Entry(self.frame_2d_inputs, width=10)
        self.x_min_entry.grid(row=1, column=1, padx=5, pady=2)
        self.x_min_entry.insert(0, "-5")
        ttk.Label(self.frame_2d_inputs, text="تا:").grid(row=1, column=2, padx=(0,5), pady=2, sticky="w")
        self.x_max_entry = ttk.Entry(self.frame_2d_inputs, width=10)
        self.x_max_entry.grid(row=1, column=3, padx=5, pady=2)
        self.x_max_entry.insert(0, "5")

        # --- 3D Inputs ---
        self.frame_3d_inputs = ttk.Frame(input_frame)
        # self.frame_3d_inputs.grid(row=2, column=0, columnspan=4, sticky="ew") # managed by toggle

        ttk.Label(self.frame_3d_inputs, text="تابع f(x, y):").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.func_entry_3d = ttk.Entry(self.frame_3d_inputs, width=40)
        self.func_entry_3d.grid(row=0, column=1, columnspan=3, padx=5, pady=2, sticky="ew")
        self.func_entry_3d.insert(0, "np.sin(np.sqrt(x**2 + y**2))")

        ttk.Label(self.frame_3d_inputs, text="X از:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.x_min_3d_entry = ttk.Entry(self.frame_3d_inputs, width=8)
        self.x_min_3d_entry.grid(row=1, column=1, padx=5, pady=2)
        self.x_min_3d_entry.insert(0, "-5")
        ttk.Label(self.frame_3d_inputs, text="تا:").grid(row=1, column=2, padx=(0,5), pady=2, sticky="w")
        self.x_max_3d_entry = ttk.Entry(self.frame_3d_inputs, width=8)
        self.x_max_3d_entry.grid(row=1, column=3, padx=5, pady=2)
        self.x_max_3d_entry.insert(0, "5")

        ttk.Label(self.frame_3d_inputs, text="Y از:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.y_min_3d_entry = ttk.Entry(self.frame_3d_inputs, width=8)
        self.y_min_3d_entry.grid(row=2, column=1, padx=5, pady=2)
        self.y_min_3d_entry.insert(0, "-5")
        ttk.Label(self.frame_3d_inputs, text="تا:").grid(row=2, column=2, padx=(0,5), pady=2, sticky="w")
        self.y_max_3d_entry = ttk.Entry(self.frame_3d_inputs, width=8)
        self.y_max_3d_entry.grid(row=2, column=3, padx=5, pady=2)
        self.y_max_3d_entry.insert(0, "5")

        self.frame_2d_inputs.columnconfigure(1, weight=1)
        self.frame_3d_inputs.columnconfigure(1, weight=1)


        plot_button = ttk.Button(input_frame, text="رسم نمودار", command=self.draw_plot)
        plot_button.grid(row=3, column=0, columnspan=3, pady=10)

        # --- Plot Area ---
        self.plot_canvas_frame = ttk.Frame(self.plot_window)
        self.plot_canvas_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.figure = plt.Figure(figsize=(6, 5), dpi=100)
        self.plot_canvas = FigureCanvasTkAgg(self.figure, master=self.plot_canvas_frame)
        self.plot_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.toggle_plot_inputs() # Initial setup based on default plot type

    def toggle_plot_inputs(self):
        plot_type = self.plot_type_var.get()
        if plot_type == "2D":
            self.frame_3d_inputs.grid_remove()
            self.frame_2d_inputs.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(5,0))
        elif plot_type == "3D":
            self.frame_2d_inputs.grid_remove()
            self.frame_3d_inputs.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(5,0))

    def draw_plot(self):
        self.figure.clear()
        plot_type = self.plot_type_var.get()

        try:
            if plot_type == "2D":
                func_str = self.func_entry_2d.get()
                x_min = float(self.x_min_entry.get())
                x_max = float(self.x_max_entry.get())

                if x_min >= x_max:
                    self.display_plot_error("مقدار X_min باید کمتر از X_max باشد.")
                    return

                x_vals = np.linspace(x_min, x_max, 400)
                # IMPORTANT: Use a safe eval for user-provided functions
                # For simplicity in this example, direct eval is used, but this is a security risk.
                # In a real app, use asteval or a similar library.
                y_vals = [eval(func_str, {'np': np, 'x': val}) for val in x_vals]

                ax = self.figure.add_subplot(111)
                ax.plot(x_vals, y_vals)
                ax.set_xlabel("x")
                ax.set_ylabel("f(x)")
                ax.set_title(f"نمودار y = {func_str}")
                ax.grid(True)

            elif plot_type == "3D":
                func_str = self.func_entry_3d.get()
                x_min = float(self.x_min_3d_entry.get())
                x_max = float(self.x_max_3d_entry.get())
                y_min = float(self.y_min_3d_entry.get())
                y_max = float(self.y_max_3d_entry.get())

                if x_min >= x_max or y_min >= y_max:
                    self.display_plot_error("مقادیر min باید کمتر از مقادیر max باشند.")
                    return

                x_vals = np.linspace(x_min, x_max, 50)
                y_vals = np.linspace(y_min, y_max, 50)
                X, Y = np.meshgrid(x_vals, y_vals)

                # Z = eval(func_str, {'np': np, 'x': X, 'y': Y}) # Security risk with eval
                # Safer approach for eval: define allowed names
                allowed_names = {"np": np, "x": X, "y": Y}
                # Add common math functions from numpy to allowed_names
                for name in dir(np):
                    if callable(getattr(np, name)):
                        allowed_names[name] = getattr(np, name)

                Z = eval(func_str, {"__builtins__": {}}, allowed_names)


                ax = self.figure.add_subplot(111, projection='3d')
                ax.plot_surface(X, Y, Z, cmap='viridis')
                ax.set_xlabel("x")
                ax.set_ylabel("y")
                ax.set_zlabel("f(x, y)")
                ax.set_title(f"نمودار z = {func_str}")

            self.plot_canvas.draw()

        except Exception as e:
            self.display_plot_error(f"خطا در رسم نمودار: {e}")

    def display_plot_error(self, message):
        # Simple error display on the plot itself or a status bar
        # For now, clearing and showing text
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.text(0.5, 0.5, message, ha='center', va='center', color='red', fontsize=12, wrap=True)
        self.plot_canvas.draw()

    def open_solve_equation_window(self):
        self.solve_eq_window = tk.Toplevel(self.master)
        self.solve_eq_window.title("حل معادله")
        self.solve_eq_window.geometry("500x400")

        # --- Input Frame ---
        input_frame = ttk.LabelFrame(self.solve_eq_window, text="ورودی معادله و تنظیمات")
        input_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(input_frame, text="معادله (f(x) = 0):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.eq_entry = ttk.Entry(input_frame, width=40)
        self.eq_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.eq_entry.insert(0, "x**2 - 4") # Example: x^2 - 4 = 0

        ttk.Label(input_frame, text="نوع معادله:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.eq_type_var = tk.StringVar(value="algebraic_simple")
        eq_type_alg_simple = ttk.Radiobutton(input_frame, text="جبری ساده (خطی/درجه دو)", variable=self.eq_type_var, value="algebraic_simple", command=self.toggle_solver_inputs)
        eq_type_alg_simple.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        eq_type_nonlinear = ttk.Radiobutton(input_frame, text="غیرخطی (عددی)", variable=self.eq_type_var, value="nonlinear_numerical", command=self.toggle_solver_inputs)
        eq_type_nonlinear.grid(row=1, column=2, padx=5, pady=5, sticky="w")


        # --- Solver Specific Inputs ---
        self.solver_inputs_frame = ttk.Frame(input_frame)
        self.solver_inputs_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=5)

        # For non-linear numerical solver
        self.initial_guess_label = ttk.Label(self.solver_inputs_frame, text="حدس اولیه (x0):")
        self.initial_guess_entry = ttk.Entry(self.solver_inputs_frame, width=10)
        self.initial_guess_entry.insert(0, "1.0")


        input_frame.grid_columnconfigure(1, weight=1)

        solve_button = ttk.Button(input_frame, text="حل معادله", command=self.solve_equation_action)
        solve_button.grid(row=3, column=0, columnspan=3, pady=10)

        # --- Result Display ---
        result_frame = ttk.LabelFrame(self.solve_eq_window, text="نتیجه حل")
        result_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.eq_result_text = tk.Text(result_frame, height=8, width=50, state='disabled', font=('Arial', 12))
        self.eq_result_text.pack(padx=5, pady=5, fill="both", expand=True)

        self.toggle_solver_inputs() # Initial call

    def toggle_solver_inputs(self):
        solver_type = self.eq_type_var.get()
        # Clear previous specific inputs
        for widget in self.solver_inputs_frame.winfo_children():
            widget.grid_remove()

        if solver_type == "nonlinear_numerical":
            self.initial_guess_label.grid(row=0, column=0, padx=5, pady=2, sticky="w")
            self.initial_guess_entry.grid(row=0, column=1, padx=5, pady=2, sticky="w")
        # Add more conditions for other solver types if needed (e.g., system of equations)


    def _display_eq_result(self, message):
        self.eq_result_text.config(state='normal')
        self.eq_result_text.delete('1.0', tk.END)
        self.eq_result_text.insert(tk.END, message)
        self.eq_result_text.config(state='disabled')

    def solve_equation_action(self):
        eq_str = self.eq_entry.get()
        solver_type = self.eq_type_var.get()

        if not eq_str:
            self._display_eq_result("لطفاً معادله را وارد کنید.")
            return

        try:
            if solver_type == "algebraic_simple":
                try:
                    import sympy
                    x_sym = sympy.Symbol('x')

                    # Prepare the equation string for sympy
                    # Replace common function names that users might type without "np."
                    # This is a simplified approach; a more robust parser would be ideal.
                    sympy_eq_str = eq_str.replace('^', '**') # Python power to sympy power

                    # Define a mapping for common functions to their sympy equivalents
                    func_map = {
                        'sin': 'sin', 'cos': 'cos', 'tan': 'tan',
                        'exp': 'exp', 'ln': 'log', # sympy's log is natural log
                        'log10': 'log(_,10)', # sympy's log(expr, base)
                        'sqrt': 'sqrt',
                        'pi': 'pi', 'e': 'E' # Sympy constants
                    }
                    # For functions like log, which might be log(x) or log(x,base)
                    # we need careful replacement.
                    # For "log(...)" not preceded by "np." or "log10", assume base 10.
                    # This uses a placeholder approach that is basic.

                    temp_sympy_eq_str = sympy_eq_str
                    for py_name, sp_name in func_map.items():
                        if sp_name == 'log(_,10)': # Handle log10 specifically
                             # Replace "log(" not part of "log10("
                            temp_sympy_eq_str = re.sub(r'(?<!log10)log\(', 'log_base10_placeholder(', temp_sympy_eq_str)
                        else:
                            temp_sympy_eq_str = temp_sympy_eq_str.replace(py_name, sp_name)

                    # Finalize log10 placeholder
                    sympy_eq_str = temp_sympy_eq_str.replace('log_base10_placeholder(', f'log({x_sym},10)')


                    # Create a dictionary of allowed sympy functions for sympify
                    # This helps control what sympify can evaluate from the string.
                    sympy_locals = {'x': x_sym, 'Symbol': sympy.Symbol, 'S': sympy.S}
                    for name in ['sin', 'cos', 'tan', 'exp', 'log', 'sqrt', 'pi', 'E', 'ln', 'asin', 'acos', 'atan']:
                        if hasattr(sympy, name):
                            sympy_locals[name] = getattr(sympy, name)

                    # Sympify the string to a sympy expression.
                    # The equation is assumed to be in the form f(x) = 0, so user enters f(x).
                    equation = sympy.sympify(sympy_eq_str, locals=sympy_locals)

                    # Solve the equation for x.
                    solutions = sympy.solve(equation, x_sym)

                    if solutions:
                        solutions_str_list = []
                        for sol in solutions:
                            # Attempt to evaluate to a float if possible, otherwise pretty print
                            try:
                                sol_evalf = sol.evalf(n=10) # Evaluate with some precision
                                if sol_evalf.is_real:
                                    solutions_str_list.append(f"{float(sol_evalf):.6g}")
                                elif sol_evalf.is_complex:
                                    c_sol = complex(sol_evalf)
                                    solutions_str_list.append(f"{c_sol.real:.4g}{c_sol.imag:+.4g}j")
                                else: # Fallback for other symbolic forms
                                    solutions_str_list.append(sympy.pretty(sol))
                            except Exception: # If evalf fails or leads to issues
                                solutions_str_list.append(sympy.pretty(sol))
                        self._display_eq_result("ریشه‌ها (حل سمبلیک با SymPy):\n" + "\n".join(solutions_str_list))
                    else:
                        self._display_eq_result("ریشه‌ای با SymPy یافت نشد یا معادله را نمی‌توان به صورت سمبلیک حل کرد (ممکن است معادله فراتر از توانایی حل‌کننده جبری باشد یا هیچ ریشه‌ای نداشته باشد).")

                except ImportError:
                    self._display_eq_result("خطا: کتابخانه SymPy برای حل جبری مورد نیاز است. لطفاً آن را نصب کنید (pip install sympy).")
                except (sympy.SympifyError, TypeError, SyntaxError) as e_symp:
                    self._display_eq_result(f"خطا در تجزیه معادله برای SymPy: {e_symp}\nاز 'x' به عنوان متغیر و فرمت صحیح توابع (مانند sin(x)) استفاده کنید. مطمئن شوید معادله به فرم f(x) است.")
                except Exception as e_solve:
                    self._display_eq_result(f"خطا در حل سمبلیک معادله با SymPy: {e_solve}")

            elif solver_type == "nonlinear_numerical":
                from scipy.optimize import root_scalar
                initial_guess_str = self.initial_guess_entry.get()
                if not initial_guess_str:
                    self._display_eq_result("لطفاً حدس اولیه (x0) را وارد کنید.")
                    return
                x0 = float(initial_guess_str)

                try:
                    # Create a lambda function from the equation string.
                    # Ensure common numpy functions are available if used in equation.
                    # User must use 'x' as the variable.
                    # Example: "np.sin(x) - 0.5"
                    func = lambda x_val: eval(eq_str, {"np": np, "x": x_val,
                                                      "sin": np.sin, "cos": np.cos, "tan": np.tan,
                                                      "log": np.log, "log10": np.log10, "exp": np.exp,
                                                      "sqrt": np.sqrt, "pi": np.pi, "e": np.e})
                    func(x0) # Test the function with the initial guess
                except Exception as e:
                    self._display_eq_result(f"خطا در تعریف تابع از معادله: {e}\nمطمئن شوید از 'x' به عنوان متغیر استفاده کرده‌اید و توابع مانند np.sin(x) باشند.")
                    return

                sol = None
                try:
                    # Try a few robust methods from root_scalar
                    # Newton (actually secant if fprime not given)
                    sol = root_scalar(func, x0=x0, method='newton', maxiter=500)
                    if not sol.converged: # Try another method if newton fails
                        # Brentq requires a bracket [a,b] where f(a) and f(b) have opposite signs.
                        # We can try to create a small bracket around x0.
                        delta = abs(x0 * 0.5) if x0 != 0 else 0.5
                        a, b = x0 - delta, x0 + delta
                        # Check if function values at bracket ends have opposite signs
                        try:
                            fa, fb = func(a), func(b)
                            if fa * fb < 0:
                                sol = root_scalar(func, bracket=[a, b], method='brentq', maxiter=500)
                            else: # If not, try to widen the bracket or just report newton's failure
                                if not sol.converged: # if newton didnt converge and bracket also not good
                                     self._display_eq_result(f"روش Newton همگرا نشد و بازه مناسب برای Brentq یافت نشد.\nآخرین نتیجه Newton (غیرهمگرا): x={sol.root:.8f}, وضعیت: {sol.flag}")
                                     return
                        except Exception: # If func fails at bracket points
                            if not sol.converged:
                                self._display_eq_result(f"روش Newton همگرا نشد و خطا در ایجاد بازه برای Brentq.\nآخرین نتیجه Newton (غیرهمگرا): x={sol.root:.8f}, وضعیت: {sol.flag}")
                                return
                except Exception as e_solve:
                    self._display_eq_result(f"خطا در طول حل عددی: {e_solve}")
                    return

                if sol and sol.converged:
                    self._display_eq_result(f"ریشه پیدا شده (عددی):\nx = {sol.root:.8f}\nتعداد مراحل: {sol.iterations}\nوضعیت: {sol.flag}")
                elif sol: # sol object exists but not converged
                     self._display_eq_result(f"حل ممکن است همگرا نشده باشد یا دقت پایین باشد:\nx = {sol.root:.8f}\nوضعیت: {sol.flag}\nامتحان با حدس اولیه دیگر یا روش دیگر ممکن است کمک کند.")
                else: # No solution object was even created (should be caught by earlier error handling)
                    self._display_eq_result("حل عددی با روش‌های امتحان شده به نتیجه نرسید.")

        except Exception as e:
            self._display_eq_result(f"خطای کلی در پردازش: {e}")

    def open_calculus_window(self):
        self.calculus_window = tk.Toplevel(self.master)
        self.calculus_window.title("محاسبات دیفرانسیل و انتگرال")
        self.calculus_window.geometry("600x450")

        # --- Input Frame ---
        input_frame = ttk.LabelFrame(self.calculus_window, text="ورودی تابع و تنظیمات")
        input_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(input_frame, text="تابع f(x):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.calc_func_entry = ttk.Entry(input_frame, width=45)
        self.calc_func_entry.grid(row=0, column=1, columnspan=3, padx=5, pady=5, sticky="ew")
        self.calc_func_entry.insert(0, "np.sin(x)")

        ttk.Label(input_frame, text="عملیات:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.calc_op_var = tk.StringVar(value="derivative")
        calc_op_deriv = ttk.Radiobutton(input_frame, text="مشتق در نقطه", variable=self.calc_op_var, value="derivative", command=self.toggle_calculus_inputs)
        calc_op_deriv.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        calc_op_integral = ttk.Radiobutton(input_frame, text="انتگرال معین", variable=self.calc_op_var, value="definite_integral", command=self.toggle_calculus_inputs)
        calc_op_integral.grid(row=1, column=2, padx=5, pady=5, sticky="w")

        calc_op_indef_integral = ttk.Radiobutton(input_frame, text="انتگرال نامعین (SymPy)", variable=self.calc_op_var, value="indefinite_integral", command=self.toggle_calculus_inputs)
        calc_op_indef_integral.grid(row=1, column=3, padx=5, pady=5, sticky="w")

        calc_op_area = ttk.Radiobutton(input_frame, text="مساحت", variable=self.calc_op_var, value="area", command=self.toggle_calculus_inputs)
        calc_op_area.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        calc_op_volume = ttk.Radiobutton(input_frame, text="حجم دوران", variable=self.calc_op_var, value="volume", command=self.toggle_calculus_inputs)
        calc_op_volume.grid(row=2, column=2, padx=5, pady=5, sticky="w")


        # --- Operation Specific Inputs ---
        self.calculus_inputs_frame = ttk.Frame(input_frame)
        self.calculus_inputs_frame.grid(row=3, column=0, columnspan=4, sticky="ew", pady=5) # Ensure this frame spans enough columns

        # For Derivative
        self.deriv_point_label = ttk.Label(self.calculus_inputs_frame, text="نقطه x0 برای مشتق:")
        self.deriv_point_entry = ttk.Entry(self.calculus_inputs_frame, width=10)
        self.deriv_point_entry.insert(0, "0")
        self.deriv_order_label = ttk.Label(self.calculus_inputs_frame, text="مرتبه مشتق (n):")
        self.deriv_order_entry = ttk.Entry(self.calculus_inputs_frame, width=5)
        self.deriv_order_entry.insert(0, "1")


        # For Integral
        self.integral_a_label = ttk.Label(self.calculus_inputs_frame, text="حد پایین انتگرال (a):")
        self.integral_a_entry = ttk.Entry(self.calculus_inputs_frame, width=10)
        self.integral_a_entry.insert(0, "0")
        self.integral_b_label = ttk.Label(self.calculus_inputs_frame, text="حد بالای انتگرال (b):")
        self.integral_b_entry = ttk.Entry(self.calculus_inputs_frame, width=10)
        self.integral_b_entry.insert(0, "np.pi")

        # For Area/Volume
        self.func_g_label = ttk.Label(self.calculus_inputs_frame, text="تابع دوم g(x) (اختیاری):")
        self.func_g_entry = ttk.Entry(self.calculus_inputs_frame, width=30)
        self.area_type_label = ttk.Label(self.calculus_inputs_frame, text="نوع مساحت:")
        self.area_type_var = tk.StringVar(value="under_f")
        self.area_under_f_radio = ttk.Radiobutton(self.calculus_inputs_frame, text="زیر f(x)", variable=self.area_type_var, value="under_f")
        self.area_between_fg_radio = ttk.Radiobutton(self.calculus_inputs_frame, text="بین f(x) و g(x)", variable=self.area_type_var, value="between_fg")

        self.volume_axis_label = ttk.Label(self.calculus_inputs_frame, text="دوران حول محور:")
        self.volume_axis_var = tk.StringVar(value="x_axis") # Default to x-axis
        self.volume_x_axis_radio = ttk.Radiobutton(self.calculus_inputs_frame, text="محور x (دیسک/واشر)", variable=self.volume_axis_var, value="x_axis")
        self.volume_y_axis_radio = ttk.Radiobutton(self.calculus_inputs_frame, text="محور y (پوسته)", variable=self.volume_axis_var, value="y_axis")


        input_frame.grid_columnconfigure(1, weight=1)
        # Adjust row for calc_button based on new radio buttons for area/volume
        calc_button = ttk.Button(input_frame, text="محاسبه", command=self.perform_calculus_action)
        calc_button.grid(row=4, column=0, columnspan=4, pady=10) # Moved to row 4

        # --- Result Display ---
        result_frame = ttk.LabelFrame(self.calculus_window, text="نتیجه محاسبه")
        result_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.calculus_result_text = tk.Text(result_frame, height=8, width=60, state='disabled', font=('Arial', 12))
        self.calculus_result_text.pack(padx=5, pady=5, fill="both", expand=True)

        self.toggle_calculus_inputs() # Initial call

    def toggle_calculus_inputs(self):
        op_type = self.calc_op_var.get()
        for widget in self.calculus_inputs_frame.winfo_children():
            widget.grid_remove() # Hide all first

        if op_type == "derivative":
            self.deriv_point_label.grid(row=0, column=0, padx=5, pady=2, sticky="w")
            self.deriv_point_entry.grid(row=0, column=1, padx=5, pady=2, sticky="w")
            self.deriv_order_label.grid(row=0, column=2, padx=5, pady=2, sticky="w")
            self.deriv_order_entry.grid(row=0, column=3, padx=5, pady=2, sticky="w")
        elif op_type == "definite_integral":
            self.integral_a_label.grid(row=0, column=0, padx=5, pady=2, sticky="w")
            self.integral_a_entry.grid(row=0, column=1, padx=5, pady=2, sticky="w")
            self.integral_b_label.grid(row=0, column=2, padx=5, pady=2, sticky="w")
            self.integral_b_entry.grid(row=0, column=3, padx=5, pady=2, sticky="w")
        elif op_type == "indefinite_integral":
            # No specific inputs other than the function itself
            pass
        elif op_type == "area":
            self.integral_a_label.grid(row=0, column=0, padx=5, pady=2, sticky="w") # Re-use a and b labels/entries
            self.integral_a_entry.grid(row=0, column=1, padx=5, pady=2, sticky="w")
            self.integral_b_label.grid(row=0, column=2, padx=5, pady=2, sticky="w")
            self.integral_b_entry.grid(row=0, column=3, padx=5, pady=2, sticky="w")

            self.area_type_label.grid(row=1, column=0, padx=5, pady=2, sticky="w")
            self.area_under_f_radio.grid(row=1, column=1, padx=5, pady=2, sticky="w")
            self.area_between_fg_radio.grid(row=1, column=2, padx=5, pady=2, sticky="w")

            self.func_g_label.grid(row=2, column=0, padx=5, pady=2, sticky="w") # g(x) for area between curves
            self.func_g_entry.grid(row=2, column=1, columnspan=3, padx=5, pady=2, sticky="ew")
            self.func_g_entry.insert(0, "x") # Example for g(x)

        elif op_type == "volume":
            self.integral_a_label.grid(row=0, column=0, padx=5, pady=2, sticky="w") # Re-use a and b
            self.integral_a_entry.grid(row=0, column=1, padx=5, pady=2, sticky="w")
            self.integral_b_label.grid(row=0, column=2, padx=5, pady=2, sticky="w")
            self.integral_b_entry.grid(row=0, column=3, padx=5, pady=2, sticky="w")

            self.volume_axis_label.grid(row=1, column=0, padx=5, pady=2, sticky="w")
            self.volume_x_axis_radio.grid(row=1, column=1, padx=5, pady=2, sticky="w")
            self.volume_y_axis_radio.grid(row=1, column=2, padx=5, pady=2, sticky="w")

            self.func_g_label.grid(row=2, column=0, padx=5, pady=2, sticky="w") # g(x) for volume between curves (washer/shell method)
            self.func_g_entry.grid(row=2, column=1, columnspan=3, padx=5, pady=2, sticky="ew")
            self.func_g_entry.insert(0, "0") # Example for g(x)


    def _display_calculus_result(self, message):
        self.calculus_result_text.config(state='normal')
        self.calculus_result_text.delete('1.0', tk.END)
        self.calculus_result_text.insert(tk.END, message)
        self.calculus_result_text.config(state='disabled')

    def perform_calculus_action(self):
        func_str = self.calc_func_entry.get()
        op_type = self.calc_op_var.get()

        if not func_str:
            self._display_calculus_result("لطفاً تابع f(x) را وارد کنید.")
            return

        try:
            # Create a lambda function from the function string
            # User must use 'x' as the variable.
            calc_func = lambda x_val: eval(func_str, {"np": np, "x": x_val,
                                                   "sin": np.sin, "cos": np.cos, "tan": np.tan,
                                                   "log": np.log, "log10": np.log10, "exp": np.exp,
                                                   "sqrt": np.sqrt, "pi": np.pi, "e": np.e})
            # Test function with a dummy value (e.g., 0 or 1) to catch early syntax errors
            try:
                calc_func(1.0) # Test with 1.0
            except Exception as e_test:
                 self._display_calculus_result(f"خطا در تعریف تابع: {e_test}\nمطمئن شوید از 'x' به عنوان متغیر و فرمت صحیح توابع (مانند np.sin(x)) استفاده کرده اید.")
                 return


            if op_type == "derivative":
                from scipy.misc import derivative # Note: derivative is in scipy.misc, might need to ensure scipy version or use alternative if deprecated.
                                                  # For newer scipy, consider numdifftools or implement finite difference.
                                                  # Let's assume scipy.misc.derivative is available for now.

                point_str = self.deriv_point_entry.get()
                order_str = self.deriv_order_entry.get()
                if not point_str or not order_str:
                    self._display_calculus_result("لطفاً نقطه و مرتبه مشتق را وارد کنید.")
                    return

                x0 = eval(point_str, {"np": np, "pi": np.pi, "e": np.e}) # Allow pi, e in point
                n_order = int(order_str)
                dx_val = 1e-6 # Step size, can be adjusted

                # scipy.misc.derivative can be sensitive.
                # It calculates the n-th derivative of a function at a point.
                deriv_val = derivative(calc_func, x0, dx=dx_val, n=n_order, order=n_order*2+1) # 'order' here is number of points for stencil
                self._display_calculus_result(f"مشتق مرتبه {n_order} تابع در x={x0:.4f}:\nنتیجه = {deriv_val:.8f}")

            elif op_type == "definite_integral":
                from scipy.integrate import quad

                a_str = self.integral_a_entry.get()
                b_str = self.integral_b_entry.get()
                if not a_str or not b_str:
                    self._display_calculus_result("لطفاً حدود انتگرال (a و b) را وارد کنید.")
                    return

                # Allow np constants like np.pi in integral limits
                a_val = eval(a_str, {"np": np, "pi": np.pi, "e": np.e})
                b_val = eval(b_str, {"np": np, "pi": np.pi, "e": np.e})

                if a_val >= b_val:
                    self._display_calculus_result("حد پایین انتگرال (a) باید کمتر از حد بالا (b) باشد.")
                    return

                integral_val, error_est = quad(calc_func, a_val, b_val)
                self._display_calculus_result(f"انتگرال معین تابع از {a_val:.4f} تا {b_val:.4f}:\nنتیجه = {integral_val:.8f}\nتخمین خطا = {error_est:.2e}")

            elif op_type == "indefinite_integral":
                try:
                    import sympy
                    x_sym = sympy.Symbol('x')
                    # Convert common numpy functions to sympy, if present in func_str
                    # This is a basic conversion, more complex functions might need explicit handling
                    sympy_func_str = func_str.replace('np.sin', 'sin')\
                                           .replace('np.cos', 'cos')\
                                           .replace('np.tan', 'tan')\
                                           .replace('np.exp', 'exp')\
                                           .replace('np.log10', 'log') # sympy's log is natural log, log(expr, base) for other bases
                                           .replace('np.log', 'ln') # sympy's ln or log is natural log
                                           .replace('np.sqrt', 'sqrt')\
                                           .replace('pi', 'pi') # sympy has its own pi
                                           .replace('e', 'E') # sympy has E for Napier's constant

                    # For log10, SymPy uses log(expr, 10). We need to be careful if "log(" was meant as log10 or ln.
                    # Assuming "log(" from user was log10 and "ln(" was natural log.
                    # SymPy's default log is natural log.
                    if "log10(" in func_str: # if user typed log10 explicitly
                        sympy_func_str = sympy_func_str.replace('log(x, 10)', 'log(x,10)') # ensure no space if user types "log(x, 10)"
                    elif "log(" in func_str and "log10(" not in func_str : # if user typed "log(" and it wasn't log10
                         # This is tricky. np.log is natural, np.log10 is base 10.
                         # Our main calc display uses log for log10 and ln for natural.
                         # Let's assume if user typed 'log(' in calculus, they meant log10.
                         # And if they typed 'ln(', they meant natural log.
                         # Sympy: log(x) is ln(x), log(x,10) is log10(x)
                         # So 'log(' in input string becomes 'log(?,10)' for sympy
                         # And 'ln(' in input string becomes 'log(?)' for sympy.
                         # Current replacements: np.log10 -> log (which is ln in sympy) -> WRONG for sympy
                         # np.log -> ln (which is ln in sympy) -> CORRECT for sympy

                        # Let's refine the replacements for sympy:
                        # User's "log(x)" (meant as log10) -> sympy's "log(x,10)"
                        # User's "ln(x)" (meant as ln) -> sympy's "log(x)" or "ln(x)"

                        # Re-doing sympy_func_str carefully:
                        temp_str = func_str.replace('np.pi', 'pi').replace('np.e', 'E') # constants first
                        temp_str = temp_str.replace('np.sqrt', 'sqrt')
                        temp_str = temp_str.replace('np.exp', 'exp')
                        # Trig functions
                        temp_str = temp_str.replace('np.sin', 'sin')
                        temp_str = temp_str.replace('np.cos', 'cos')
                        temp_str = temp_str.replace('np.tan', 'tan')
                        # Logarithms:
                        # If user writes "log(x)" assume base 10 for consistency with main calculator display
                        # If user writes "ln(x)" assume natural log
                        # If user writes "np.log(x)" it's natural log
                        # If user writes "np.log10(x)" it's base 10 log

                        # 1. Replace specific np versions first
                        temp_str = temp_str.replace('np.log10', 'log_base10_placeholder') # temp placeholder
                        temp_str = temp_str.replace('np.log', 'ln') # np.log is natural log -> sympy ln

                        # 2. Replace generic log/ln if not already np.log/np.log10
                        # If "log(" still exists, it means user typed "log(" not "np.log10(" or "np.log("
                        # We assume user's "log(" is base 10.
                        import re
                        temp_str = re.sub(r'(?<!np\.)log\(', r'log_base10_placeholder(', temp_str)
                        # User's "ln(" becomes sympy's "ln(" (or "log(")
                        temp_str = re.sub(r'(?<!np\.)ln\(', r'ln(', temp_str)

                        # 3. Finalize placeholders
                        sympy_func_str = temp_str.replace('log_base10_placeholder', 'log(_,10)').replace('_',str(x_sym)) # Sympy log(expr,base)
                        # For ln, sympy's ln() or log() is fine.
                        # If an 'x' is not part of a function call, it needs to be sympy.Symbol('x')
                        # This simple replacement is fragile. A proper parser is better.

                    expression = sympy.sympify(sympy_func_str, locals={'x': x_sym, 'sin': sympy.sin, 'cos': sympy.cos, 'tan': sympy.tan, 'exp': sympy.exp, 'ln': sympy.ln, 'log': sympy.log, 'sqrt': sympy.sqrt, 'pi': sympy.pi, 'E': sympy.E})
                    indefinite_integral = sympy.integrate(expression, x_sym)
                    self._display_calculus_result(f"انتگرال نامعین:\n{sympy.pretty(indefinite_integral)} + C")

                except ImportError:
                    self._display_calculus_result("خطا: کتابخانه SymPy برای محاسبه انتگرال نامعین مورد نیاز است.\nلطفاً آن را نصب کنید (pip install sympy).")
                except (sympy.SympifyError, TypeError, SyntaxError) as e_symp:
                    self._display_calculus_result(f"خطا در تجزیه تابع برای SymPy: {e_symp}\nمطمئن شوید فرمت تابع صحیح است و از متغیر 'x' استفاده شده.\nمثال: x**2 + sin(x)")
                except Exception as e_int:
                    self._display_calculus_result(f"خطا در محاسبه انتگرال نامعین با SymPy: {e_int}")

            elif op_type == "area":
                from scipy.integrate import quad
                a_str = self.integral_a_entry.get()
                b_str = self.integral_b_entry.get()
                area_type = self.area_type_var.get()

                if not a_str or not b_str:
                    self._display_calculus_result("لطفاً حدود انتگرال (a و b) را وارد کنید.")
                    return
                a_val = eval(a_str, {"np": np, "pi": np.pi, "e": np.e})
                b_val = eval(b_str, {"np": np, "pi": np.pi, "e": np.e})
                if a_val >= b_val:
                    self._display_calculus_result("حد پایین (a) باید کمتر از حد بالا (b) باشد.")
                    return

                if area_type == "under_f":
                    # Area = integral |f(x)| dx. For simplicity, assume f(x) >= 0 or user considers sign.
                    # More robustly: integral(abs(f(x)), a, b)
                    integrand = lambda x_val: abs(calc_func(x_val))
                    area_val, error_est = quad(integrand, a_val, b_val)
                    self._display_calculus_result(f"مساحت زیر نمودار |f(x)| از {a_val:.4f} تا {b_val:.4f}:\nنتیجه = {area_val:.8f}\nتخمین خطا = {error_est:.2e}")

                elif area_type == "between_fg":
                    func_g_str = self.func_g_entry.get()
                    if not func_g_str:
                        self._display_calculus_result("لطفاً تابع دوم g(x) را برای محاسبه مساحت بین دو نمودار وارد کنید.")
                        return
                    try:
                        g_func = lambda x_val: eval(func_g_str, {"np": np, "x": x_val, "sin": np.sin, "cos": np.cos, "tan": np.tan, "log": np.log, "log10": np.log10, "exp": np.exp, "sqrt": np.sqrt, "pi": np.pi, "e": np.e})
                        g_func(a_val) # Test g_func
                    except Exception as e_g:
                        self._display_calculus_result(f"خطا در تعریف تابع g(x): {e_g}")
                        return

                    integrand = lambda x_val: abs(calc_func(x_val) - g_func(x_val))
                    area_val, error_est = quad(integrand, a_val, b_val)
                    self._display_calculus_result(f"مساحت بین f(x) و g(x) از {a_val:.4f} تا {b_val:.4f}:\nنتیجه = {area_val:.8f}\nتخمین خطا = {error_est:.2e}")

            elif op_type == "volume":
                from scipy.integrate import quad
                a_str = self.integral_a_entry.get()
                b_str = self.integral_b_entry.get()
                axis_of_rotation = self.volume_axis_var.get() # Currently only x_axis

                if not a_str or not b_str:
                    self._display_calculus_result("لطفاً حدود انتگرال (a و b) را وارد کنید.")
                    return
                a_val = eval(a_str, {"np": np, "pi": np.pi, "e": np.e})
                b_val = eval(b_str, {"np": np, "pi": np.pi, "e": np.e})
                if a_val >= b_val:
                    self._display_calculus_result("حد پایین (a) باید کمتر از حد بالا (b) باشد.")
                    return

                if axis_of_rotation == "x_axis":
                    func_g_str = self.func_g_entry.get()
                    g_func_provided = bool(func_g_str)
                    g_func = None
                    if g_func_provided:
                        try:
                            g_func = lambda x_val: eval(func_g_str, {"np": np, "x": x_val, "sin": np.sin, "cos": np.cos, "tan": np.tan, "log": np.log, "log10": np.log10, "exp": np.exp, "sqrt": np.sqrt, "pi": np.pi, "e": np.e})
                            g_func(a_val) # Test g_func
                        except Exception as e_g:
                            self._display_calculus_result(f"خطا در تعریف تابع g(x) برای حجم: {e_g}")
                            return

                    if g_func: # Washer method: pi * integral (f(x)^2 - g(x)^2) dx
                        # Assuming f(x) is outer radius, g(x) is inner. User needs to ensure f(x)^2 >= g(x)^2 or use abs.
                        # For simplicity, pi * integral | f(x)^2 - g(x)^2 | dx
                        integrand = lambda x_val: np.pi * abs(calc_func(x_val)**2 - g_func(x_val)**2)
                        volume_val, error_est = quad(integrand, a_val, b_val)
                        self._display_calculus_result(f"حجم جسم حاصل از دوران ناحیه بین f(x) و g(x) حول محور x:\nنتیجه = {volume_val:.8f}\nتخمین خطا = {error_est:.2e}")
                    else: # Disk method: pi * integral f(x)^2 dx
                        integrand = lambda x_val: np.pi * (calc_func(x_val)**2)
                        volume_val, error_est = quad(integrand, a_val, b_val)
                        self._display_calculus_result(f"حجم جسم حاصل از دوران f(x) حول محور x (روش دیسک):\nنتیجه = {volume_val:.8f}\nتخمین خطا = {error_est:.2e}")

                elif axis_of_rotation == "y_axis": # Cylindrical shells method
                    if a_val < 0:
                        self._display_calculus_result("خطا: برای روش پوسته‌های استوانه‌ای حول محور y، حدود انتگرال [a,b] باید غیرمنفی باشند (a >= 0).")
                        return

                    func_g_str = self.func_g_entry.get()
                    g_func_provided = bool(func_g_str and func_g_str.strip() != "0") # Check if g(x) is meaningfully provided
                    g_func = None
                    if g_func_provided:
                        try:
                            g_func = lambda x_val: eval(func_g_str, {"np": np, "x": x_val, "sin": np.sin, "cos": np.cos, "tan": np.tan, "log": np.log, "log10": np.log10, "exp": np.exp, "sqrt": np.sqrt, "pi": np.pi, "e": np.e})
                            g_func(a_val) # Test
                        except Exception as e_g:
                            self._display_calculus_result(f"خطا در تعریف تابع g(x) برای حجم: {e_g}")
                            return

                    if g_func: # Volume of region between f(x) and g(x) rotated around y-axis
                        # V = 2π ∫[a,b] x * |f(x) - g(x)| dx
                        integrand = lambda x_val: 2 * np.pi * x_val * abs(calc_func(x_val) - g_func(x_val))
                        volume_val, error_est = quad(integrand, a_val, b_val)
                        self._display_calculus_result(f"حجم جسم حاصل از دوران ناحیه بین f(x) و g(x) حول محور y (روش پوسته):\nنتیجه = {volume_val:.8f}\nتخمین خطا = {error_est:.2e}")
                    else: # Volume of region under f(x) rotated around y-axis
                        # V = 2π ∫[a,b] x * f(x) dx  (assuming f(x) >= 0)
                        # More generally, if f(x) can be negative, it's 2π ∫[a,b] x * |f(x)| dx for the area between f(x) and x-axis
                        integrand = lambda x_val: 2 * np.pi * x_val * abs(calc_func(x_val))
                        volume_val, error_est = quad(integrand, a_val, b_val)
                        self._display_calculus_result(f"حجم جسم حاصل از دوران f(x) حول محور y (روش پوسته):\nنتیجه = {volume_val:.8f}\nتخمین خطا = {error_est:.2e}")


        except Exception as e:
            self._display_calculus_result(f"خطای کلی: {e}")

    # Placeholder for Interpolation Window
    def open_interpolation_window(self):
        self.interp_window = tk.Toplevel(self.master)
        self.interp_window.title("درون یابی (Interpolation)")
        self.interp_window.geometry("600x500")

        # --- Input Data Frame ---
        data_frame = ttk.LabelFrame(self.interp_window, text="ورود نقاط داده (xi, yi)")
        data_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(data_frame, text="نقاط x (با کاما جدا شوند):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.interp_x_entries = ttk.Entry(data_frame, width=40)
        self.interp_x_entries.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.interp_x_entries.insert(0, "0, 1, 2, 3, 4")

        ttk.Label(data_frame, text="نقاط y (با کاما جدا شوند):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.interp_y_entries = ttk.Entry(data_frame, width=40)
        self.interp_y_entries.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.interp_y_entries.insert(0, "0, 0.8, 0.9, 0.1, -0.8")

        data_frame.grid_columnconfigure(1, weight=1)

        # --- Interpolation Settings Frame ---
        settings_frame = ttk.LabelFrame(self.interp_window, text="تنظیمات درون یابی")
        settings_frame.pack(padx=10, pady=5, fill="x")

        ttk.Label(settings_frame, text="نوع درون یابی:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.interp_kind_var = tk.StringVar(value="linear")
        interp_kinds = ["linear", "quadratic", "cubic", "nearest", "previous", "next"] # slinear, zero also possible
        # For polynomial of specific order, we'd use a different approach or allow order input
        self.interp_kind_menu = ttk.OptionMenu(settings_frame, self.interp_kind_var, interp_kinds[0], *interp_kinds)
        self.interp_kind_menu.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(settings_frame, text="نقطه x برای درون یابی:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.interp_x_new_entry = ttk.Entry(settings_frame, width=10)
        self.interp_x_new_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.interp_x_new_entry.insert(0, "2.5")

        interp_button = ttk.Button(settings_frame, text="محاسبه مقدار درون یابی شده", command=self.perform_interpolation)
        interp_button.grid(row=1, column=2, padx=10, pady=5)

        # --- Result Display ---
        result_frame = ttk.LabelFrame(self.interp_window, text="نتیجه درون یابی")
        result_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.interp_result_text = tk.Text(result_frame, height=8, width=60, state='disabled', font=('Arial', 12))
        self.interp_result_text.pack(padx=5, pady=5, fill="both", expand=True)

        # Optional: Plot button
        plot_interp_button = ttk.Button(self.interp_window, text="رسم نمودار داده و درون یابی", command=self.plot_interpolation)
        plot_interp_button.pack(pady=5)
        self.interp_plot_fig = None # To store figure for plotting window if needed


    def _display_interp_result(self, message, clear=True):
        self.interp_result_text.config(state='normal')
        if clear:
            self.interp_result_text.delete('1.0', tk.END)
        self.interp_result_text.insert(tk.END, message + "\n")
        self.interp_result_text.config(state='disabled')

    def parse_data_points(self, x_str, y_str):
        try:
            x_points = np.array(list(map(float, x_str.split(','))))
            y_points = np.array(list(map(float, y_str.split(','))))
            if len(x_points) != len(y_points):
                self._display_interp_result("خطا: تعداد نقاط x و y باید برابر باشند.")
                return None, None
            if len(x_points) < 2:
                self._display_interp_result("خطا: حداقل دو نقطه داده برای درون یابی نیاز است.")
                return None, None
            # Sort points by x for interpolation
            sorted_indices = np.argsort(x_points)
            return x_points[sorted_indices], y_points[sorted_indices]
        except ValueError:
            self._display_interp_result("خطا: نقاط داده باید اعداد معتبر باشند و با کاما از هم جدا شوند.")
            return None, None

    def perform_interpolation(self):
        x_str = self.interp_x_entries.get()
        y_str = self.interp_y_entries.get()
        x_new_str = self.interp_x_new_entry.get()
        kind = self.interp_kind_var.get()

        if not x_str or not y_str or not x_new_str:
            self._display_interp_result("خطا: لطفاً تمام فیلدهای نقاط داده و نقطه جدید را پر کنید.")
            return

        x_known, y_known = self.parse_data_points(x_str, y_str)
        if x_known is None: return

        try:
            x_new = float(x_new_str)
        except ValueError:
            self._display_interp_result("خطا: نقطه x جدید باید یک عدد معتبر باشد.")
            return

        from scipy.interpolate import interp1d

        # Check if kind requires minimum number of points
        min_points_for_kind = {
            "linear": 2, "nearest": 2, "zero": 2, "slinear": 2,
            "quadratic": 3, "cubic": 4, "previous": 2, "next": 2
        }
        if len(x_known) < min_points_for_kind.get(kind, 2): # Default to 2 if kind not in map
            self._display_interp_result(f"خطا: برای درون یابی '{kind}' حداقل {min_points_for_kind.get(kind, 2)} نقطه داده نیاز است.")
            return

        try:
            # fill_value="extrapolate" allows extrapolation outside the range of known x values.
            # Otherwise, it raises an error or fills with specified values.
            interp_func = interp1d(x_known, y_known, kind=kind, fill_value="extrapolate", bounds_error=False)
            y_new = interp_func(x_new)

            result_msg = f"مقدار درون یابی شده در x = {x_new} (نوع: {kind}):\ny = {y_new:.8f}"
            if not (np.min(x_known) <= x_new <= np.max(x_known)):
                result_msg += "\n(توجه: نقطه x جدید خارج از محدوده داده‌های اصلی است؛ نتیجه برون‌یابی شده است.)"
            self._display_interp_result(result_msg)

        except ValueError as ve: # Handles issues like x_known not being strictly increasing if not sorted, or insufficient points for kind
            self._display_interp_result(f"خطا در ایجاد تابع درون یابی: {ve}\nممکن است نقاط x یکتا نباشند یا تعداد نقاط برای نوع '{kind}' کافی نباشد.")
        except Exception as e:
            self._display_interp_result(f"خطای کلی در درون یابی: {e}")

    def plot_interpolation(self):
        x_str = self.interp_x_entries.get()
        y_str = self.interp_y_entries.get()
        kind = self.interp_kind_var.get()

        x_known, y_known = self.parse_data_points(x_str, y_str)
        if x_known is None:
            self._display_interp_result("ابتدا داده‌های معتبر وارد کنید.", clear=False)
            return

        from scipy.interpolate import interp1d

        min_points_for_kind = {"linear": 2, "quadratic": 3, "cubic": 4, "nearest": 2, "previous": 2, "next": 2}
        if len(x_known) < min_points_for_kind.get(kind, 2):
            self._display_interp_result(f"خطا: برای رسم درون یابی '{kind}' حداقل {min_points_for_kind.get(kind, 2)} نقطه داده نیاز است.", clear=False)
            return

        try:
            interp_func = interp1d(x_known, y_known, kind=kind, fill_value="extrapolate", bounds_error=False)

            # Create a new plotting window or use an existing one
            if not hasattr(self, 'interp_plot_window') or not self.interp_plot_window.winfo_exists():
                self.interp_plot_window = tk.Toplevel(self.interp_window)
                self.interp_plot_window.title(f"نمودار درون یابی ({kind})")
                self.interp_plot_window.geometry("700x600")
                self.interp_plot_fig = plt.Figure(figsize=(6,5), dpi=100)
                canvas = FigureCanvasTkAgg(self.interp_plot_fig, master=self.interp_plot_window)
                canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

            self.interp_plot_fig.clear()
            ax = self.interp_plot_fig.add_subplot(111)

            x_dense = np.linspace(np.min(x_known), np.max(x_known), 500)
            y_dense_interp = interp_func(x_dense)

            ax.plot(x_known, y_known, 'o', label='نقاط داده اصلی', markersize=8)
            ax.plot(x_dense, y_dense_interp, '-', label=f'درون یابی ({kind})')

            # Optionally, plot the new interpolated point if available
            try:
                x_new_val = float(self.interp_x_new_entry.get())
                y_new_val = interp_func(x_new_val)
                ax.plot(x_new_val, y_new_val, 'X', color='red', label=f'نقطه درون‌یابی شده ({x_new_val:.2f}, {y_new_val:.2f})', markersize=10)
            except ValueError:
                pass # x_new_entry might not be a valid float

            ax.set_xlabel("x")
            ax.set_ylabel("y")
            ax.set_title(f"نمودار درون یابی - نوع: {kind}")
            ax.legend()
            ax.grid(True)
            self.interp_plot_fig.canvas.draw_idle()
            self._display_interp_result(f"نمودار درون یابی '{kind}' رسم شد.", clear=False)

        except Exception as e:
            self._display_interp_result(f"خطا در رسم نمودار درون یابی: {e}", clear=False)


    # Placeholder for Curve Fitting Window
    def open_curve_fit_window(self):
        self.curve_fit_window = tk.Toplevel(self.master)
        self.curve_fit_window.title("برازش منحنی (Curve Fitting)")
        self.curve_fit_window.geometry("700x650") # Increased height for plot area

        # --- Input Data Frame ---
        data_frame = ttk.LabelFrame(self.curve_fit_window, text="ورود نقاط داده (xi, yi)")
        data_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(data_frame, text="نقاط x (با کاما جدا شوند):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.fit_x_entries = ttk.Entry(data_frame, width=40)
        self.fit_x_entries.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.fit_x_entries.insert(0, "0, 1, 2, 3, 4, 5")

        ttk.Label(data_frame, text="نقاط y (با کاما جدا شوند):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.fit_y_entries = ttk.Entry(data_frame, width=40)
        self.fit_y_entries.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.fit_y_entries.insert(0, "0.1, 0.9, 2.2, 2.8, 4.1, 4.9") # Example data for linear-like fit

        data_frame.grid_columnconfigure(1, weight=1)

        # --- Fitting Settings Frame ---
        settings_frame = ttk.LabelFrame(self.curve_fit_window, text="تنظیمات برازش منحنی")
        settings_frame.pack(padx=10, pady=5, fill="x")

        ttk.Label(settings_frame, text="مدل تابع برای برازش:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.fit_model_var = tk.StringVar(value="linear")
        fit_models = {
            "خطی (ax + b)": "linear",
            "نمایی (a * exp(b*x))": "exponential",
            "توانی (a * x^b)": "power",
            "چندجمله‌ای درجه ۲ (ax^2+bx+c)": "poly2",
            "چندجمله‌ای درجه ۳ (ax^3+bx^2+cx+d)": "poly3",
            "لگاریتمی (a * ln(x) + b)": "logarithmic" # Requires x > 0
        }
        self.fit_model_menu = ttk.OptionMenu(settings_frame, self.fit_model_var, list(fit_models.keys())[0], *fit_models.keys())
        self.fit_model_menu.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Store the model mapping
        self.fit_models_map = fit_models

        fit_button = ttk.Button(settings_frame, text="انجام برازش و نمایش پارامترها", command=self.perform_curve_fitting)
        fit_button.grid(row=0, column=2, padx=10, pady=5)
        settings_frame.grid_columnconfigure(1, weight=1)


        # --- Result Display ---
        result_frame = ttk.LabelFrame(self.curve_fit_window, text="نتایج برازش (پارامترها و نمودار)")
        result_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.fit_result_text = tk.Text(result_frame, height=6, width=70, state='disabled', font=('Arial', 11))
        self.fit_result_text.pack(padx=5, pady=5, fill="x")

        # --- Plot Area for Curve Fitting ---
        self.fit_plot_canvas_frame = ttk.Frame(result_frame)
        self.fit_plot_canvas_frame.pack(padx=5, pady=5, fill="both", expand=True)

        self.fit_figure = plt.Figure(figsize=(6, 4), dpi=100)
        self.fit_plot_canvas = FigureCanvasTkAgg(self.fit_figure, master=self.fit_plot_canvas_frame)
        self.fit_plot_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.fit_ax = None # To store the axes object

    def _display_fit_result(self, message, clear=True):
        self.fit_result_text.config(state='normal')
        if clear:
            self.fit_result_text.delete('1.0', tk.END)
        self.fit_result_text.insert(tk.END, message + "\n")
        self.fit_result_text.config(state='disabled')

    # --- Define model functions for curve_fit ---
    def linear_func(self, x, a, b): return a * x + b
    def exp_func(self, x, a, b): return a * np.exp(b * x)
    def power_func(self, x, a, b): return a * np.power(x, b) # Requires x > 0 for non-integer b
    def poly2_func(self, x, a, b, c): return a * x**2 + b * x + c
    def poly3_func(self, x, a, b, c, d): return a * x**3 + b * x**2 + c * x + d
    def log_func(self, x, a, b): # Requires x > 0
        # np.log is natural log. If base 10 is desired, use np.log10
        return a * np.log(x) + b


    def perform_curve_fitting(self):
        x_str = self.fit_x_entries.get()
        y_str = self.fit_y_entries.get()
        selected_model_display_name = self.fit_model_var.get()
        model_key = self.fit_models_map[selected_model_display_name]

        if not x_str or not y_str:
            self._display_fit_result("خطا: لطفاً نقاط داده x و y را وارد کنید.")
            return

        x_data, y_data = self.parse_data_points(x_str, y_str) # Re-use from interpolation
        if x_data is None or len(x_data) < 2 : # Need at least 2 points, more for higher order polys
             if x_data is not None and len(x_data) < 2: # parse_data_points already handles len < 2 for interp, but let's be explicit
                 self._display_fit_result("خطا: حداقل دو نقطه داده برای برازش نیاز است.")
             # else parse_data_points already showed error
             return


        model_func = None
        param_names = []
        initial_params = None # Optional initial guesses for parameters

        if model_key == "linear":
            model_func = self.linear_func
            param_names = ['a (شیب)', 'b (عرض از مبدا)']
        elif model_key == "exponential":
            model_func = self.exp_func
            param_names = ['a', 'b']
            # For exponential, good initial guess for 'b' can be tricky.
            # If data has y > 0, can try log-linear trick for initial guess, but curve_fit often handles it.
            if np.any(y_data <= 0): # exp_func expects y > 0 if a > 0
                self._display_fit_result("هشدار: برای مدل نمایی، مقادیر y باید مثبت باشند. ممکن است برازش با خطا مواجه شود.")
        elif model_key == "power":
            model_func = self.power_func
            param_names = ['a', 'b']
            if np.any(x_data <= 0) or np.any(y_data <= 0):
                self._display_fit_result("هشدار: برای مدل توانی (a*x^b)، مقادیر x و y باید مثبت باشند.")
                # curve_fit might fail if x contains zero or negative with non-integer b
        elif model_key == "poly2":
            model_func = self.poly2_func
            param_names = ['a (ضریب x^2)', 'b (ضریب x)', 'c (ثابت)']
            if len(x_data) < 3:
                 self._display_fit_result("خطا: برای چندجمله‌ای درجه ۲ حداقل ۳ نقطه نیاز است.")
                 return
        elif model_key == "poly3":
            model_func = self.poly3_func
            param_names = ['a (ضریب x^3)', 'b (ضریب x^2)', 'c (ضریب x)', 'd (ثابت)']
            if len(x_data) < 4:
                 self._display_fit_result("خطا: برای چندجمله‌ای درجه ۳ حداقل ۴ نقطه نیاز است.")
                 return
        elif model_key == "logarithmic":
            model_func = self.log_func
            param_names = ['a', 'b']
            if np.any(x_data <= 0):
                self._display_fit_result("خطا: برای مدل لگاریتمی (a*ln(x)+b)، تمام مقادیر x باید بزرگتر از صفر باشند.")
                return
        else:
            self._display_fit_result(f"خطا: مدل '{selected_model_display_name}' هنوز پیاده سازی نشده است.")
            return

        from scipy.optimize import curve_fit
        try:
            # For power and log functions, ensure data is positive if needed
            if model_key in ["power", "logarithmic"] and np.any(x_data <= 0):
                 # This check is somewhat redundant due to earlier specific checks, but good for safety
                 self._display_fit_result("خطا: مقادیر x برای این مدل باید مثبت باشند.")
                 return
            if model_key == "power" and np.any(y_data <=0): # Power model a*x^b typically assumes y>0 if a>0
                 # This is a soft warning as curve_fit might still work
                 self._display_fit_result("هشدار: مقادیر y برای مدل توانی معمولا مثبت هستند.")


            popt, pcov = curve_fit(model_func, x_data, y_data, p0=initial_params, maxfev=5000) # popt: optimal parameters
            perr = np.sqrt(np.diag(pcov)) # Standard deviation errors on parameters

            result_message = f"پارامترهای بهینه برای مدل '{selected_model_display_name}':\n"
            for name, val, err in zip(param_names, popt, perr):
                result_message += f"  {name}: {val:.4f} ± {err:.4f}\n"

            # Calculate R-squared for goodness of fit (optional, but informative)
            residuals = y_data - model_func(x_data, *popt)
            ss_res = np.sum(residuals**2)
            ss_tot = np.sum((y_data - np.mean(y_data))**2)
            if ss_tot == 0: # Avoid division by zero if all y_data are same
                r_squared = 1.0 if ss_res < 1e-9 else 0.0
            else:
                r_squared = 1 - (ss_res / ss_tot)
            result_message += f"ضریب تعیین (R-squared): {r_squared:.4f}\n"

            self._display_fit_result(result_message)

            # Plotting the fit
            if self.fit_ax is None or not self.fit_plot_canvas_frame.winfo_exists(): # If axes not created or window closed
                self.fit_figure.clear() # Clear previous plot on the figure
                self.fit_ax = self.fit_figure.add_subplot(111)
            else:
                self.fit_ax.clear() # Clear previous plot on existing axes

            self.fit_ax.plot(x_data, y_data, 'o', label='نقاط داده اصلی')

            # Generate smooth curve for plotting the fitted function
            x_fit_plot = np.linspace(min(x_data), max(x_data), 200)
            y_fit_plot = model_func(x_fit_plot, *popt)
            self.fit_ax.plot(x_fit_plot, y_fit_plot, '-', label=f'منحنی برازش شده ({selected_model_display_name})')

            self.fit_ax.set_xlabel("x")
            self.fit_ax.set_ylabel("y")
            self.fit_ax.set_title(f"برازش منحنی: {selected_model_display_name}")
            self.fit_ax.legend()
            self.fit_ax.grid(True)
            self.fit_figure.canvas.draw_idle()

        except RuntimeError:
            self._display_fit_result("خطا: برازش منحنی با موفقیت انجام نشد. ممکن است داده‌ها با مدل همخوانی نداشته باشند یا حدس اولیه (در صورت نیاز) نامناسب باشد.")
        except ValueError as ve:
             self._display_fit_result(f"خطای مقدار در برازش: {ve}")
        except Exception as e:
            self._display_fit_result(f"خطای کلی در برازش منحنی: {e}")

    def open_bitwise_window(self):
        self.bitwise_window = tk.Toplevel(self.master)
        self.bitwise_window.title("عملیات بیتی و منطقی")
        self.bitwise_window.geometry("550x400")

        # --- Input Frame ---
        input_frame = ttk.LabelFrame(self.bitwise_window, text="ورودی‌ها و مبنا")
        input_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(input_frame, text="عدد اول (Num1):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.bitwise_num1_entry = ttk.Entry(input_frame, width=30)
        self.bitwise_num1_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.bitwise_num1_entry.insert(0, "10") # Decimal default

        ttk.Label(input_frame, text="عدد دوم (Num2, برای AND/OR/XOR):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.bitwise_num2_entry = ttk.Entry(input_frame, width=30)
        self.bitwise_num2_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.bitwise_num2_entry.insert(0, "12") # Decimal default

        input_frame.grid_columnconfigure(1, weight=1)

        base_frame = ttk.Frame(input_frame)
        base_frame.grid(row=0, column=2, rowspan=2, padx=10, pady=5, sticky="ns")
        ttk.Label(base_frame, text="مبنای ورودی/خروجی:").pack(anchor="w")
        self.bitwise_base_var = tk.StringVar(value="10")
        bases = [("دودویی (2)", "2"), ("هشتی (8)", "8"), ("ده‌دهی (10)", "10"), ("شانزدهی (16)", "16")]
        for text, val in bases:
            rb = ttk.Radiobutton(base_frame, text=text, variable=self.bitwise_base_var, value=val, command=self.convert_bitwise_inputs_on_base_change)
            rb.pack(anchor="w", pady=2)


        # --- Operations Frame ---
        ops_frame = ttk.LabelFrame(self.bitwise_window, text="عملیات")
        ops_frame.pack(padx=10, pady=5, fill="x")

        # Operations will be buttons calling a common handler
        bitwise_ops = [
            ("Num1 AND Num2", "AND"), ("Num1 OR Num2", "OR"), ("Num1 XOR Num2", "XOR"),
            ("NOT Num1", "NOT"), ("Num1 << (Shift Left)", "LSHIFT"), ("Num1 >> (Shift Right)", "RSHIFT")
        ]

        row, col = 0, 0
        for text, op_key in bitwise_ops:
            btn = ttk.Button(ops_frame, text=text, command=lambda k=op_key: self.perform_bitwise_operation(k))
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            col += 1
            if col > 1: # Two buttons per row
                col = 0
                row += 1

        ttk.Label(ops_frame, text="مقدار شیفت (برای LSHIFT/RSHIFT):").grid(row=row, column=0, padx=5, pady=5, sticky="w")
        self.shift_amount_entry = ttk.Entry(ops_frame, width=5)
        self.shift_amount_entry.grid(row=row, column=1, padx=5, pady=5, sticky="w")
        self.shift_amount_entry.insert(0,"1")

        for i in range(col): ops_frame.grid_columnconfigure(i, weight=1)


        # --- Result Display ---
        result_frame = ttk.LabelFrame(self.bitwise_window, text="نتیجه (در مبنای انتخابی)")
        result_frame.pack(padx=10, pady=10, fill="both", expand=True)
        self.bitwise_result_text = tk.Text(result_frame, height=5, width=50, state='disabled', font=('Arial', 12))
        self.bitwise_result_text.pack(padx=5, pady=5, fill="both", expand=True)

    def _display_bitwise_result(self, message):
        self.bitwise_result_text.config(state='normal')
        self.bitwise_result_text.delete('1.0', tk.END)
        self.bitwise_result_text.insert(tk.END, message)
        self.bitwise_result_text.config(state='disabled')

    def get_int_from_bitwise_entry(self, entry_widget, base):
        val_str = entry_widget.get()
        if not val_str: return None, "ورودی خالی است."
        try:
            return int(val_str, base), None
        except ValueError:
            return None, f"مقدار '{val_str}' در مبنای {base} معتبر نیست."

    def format_int_to_base(self, value, base):
        if base == 2: return bin(value)
        if base == 8: return oct(value)
        if base == 10: return str(value)
        if base == 16: return hex(value)
        return str(value) # Should not happen

    def convert_bitwise_inputs_on_base_change(self):
        # This is a bit tricky. When base changes, we should try to re-interpret current inputs
        # OR clear them, OR try to convert them. For now, let's just note that user needs to be careful.
        # A more robust solution would store the "true" integer value and re-display in new base.
        # For simplicity, this function is a placeholder or could trigger re-validation/display.
        # self._display_bitwise_result("مبنا تغییر کرد. مقادیر ورودی را بررسی کنید.")
        # Let's try to convert the displayed numbers if possible
        current_base_str = self.bitwise_base_var.get()
        if not hasattr(self, '_previous_bitwise_base'): self._previous_bitwise_base = 10 # Assume initial is 10

        try:
            prev_base = int(self._previous_bitwise_base)
            current_base = int(current_base_str)

            num1_val_str = self.bitwise_num1_entry.get()
            if num1_val_str:
                num1_int, _ = self.get_int_from_bitwise_entry(self.bitwise_num1_entry, prev_base)
                if num1_int is not None:
                    self.bitwise_num1_entry.delete(0, tk.END)
                    self.bitwise_num1_entry.insert(0, self.format_int_to_base(num1_int, current_base).split('0b')[-1].split('0o')[-1].split('0x')[-1] if current_base !=10 else str(num1_int))


            num2_val_str = self.bitwise_num2_entry.get()
            if num2_val_str:
                num2_int, _ = self.get_int_from_bitwise_entry(self.bitwise_num2_entry, prev_base)
                if num2_int is not None:
                    self.bitwise_num2_entry.delete(0, tk.END)
                    self.bitwise_num2_entry.insert(0, self.format_int_to_base(num2_int, current_base).split('0b')[-1].split('0o')[-1].split('0x')[-1] if current_base !=10 else str(num2_int))

            self._previous_bitwise_base = current_base
        except Exception: # If conversion fails, user has to manually fix inputs
            self._display_bitwise_result("خطا در تبدیل خودکار مبنا. لطفاً ورودی‌ها را دستی تنظیم کنید.")
            self._previous_bitwise_base = int(current_base_str) # Update base anyway


    def perform_bitwise_operation(self, op_key):
        base = int(self.bitwise_base_var.get())

        num1, err1 = self.get_int_from_bitwise_entry(self.bitwise_num1_entry, base)
        if err1: self._display_bitwise_result(f"عدد اول: {err1}"); return

        result_val = None

        if op_key in ["AND", "OR", "XOR"]:
            num2, err2 = self.get_int_from_bitwise_entry(self.bitwise_num2_entry, base)
            if err2: self._display_bitwise_result(f"عدد دوم: {err2}"); return
            if op_key == "AND": result_val = num1 & num2
            elif op_key == "OR": result_val = num1 | num2
            elif op_key == "XOR": result_val = num1 ^ num2
        elif op_key == "NOT":
            # Python's ~ operator gives two's complement. For logical NOT, it depends on bit width.
            # For simplicity, we'll show Python's bitwise NOT.
            # A true logical NOT would be (2**bit_width - 1) ^ num1 if positive context.
            # Let's assume standard bitwise complement for now.
            result_val = ~num1
        elif op_key in ["LSHIFT", "RSHIFT"]:
            try:
                shift_amount = int(self.shift_amount_entry.get())
                if shift_amount < 0:
                    self._display_bitwise_result("مقدار شیفت باید غیرمنفی باشد."); return
            except ValueError:
                self._display_bitwise_result("مقدار شیفت باید عدد صحیح باشد."); return

            if op_key == "LSHIFT": result_val = num1 << shift_amount
            elif op_key == "RSHIFT": result_val = num1 >> shift_amount # Arithmetic right shift in Python

        if result_val is not None:
            # For bases 2, 8, 16, Python's bin(), oct(), hex() add "0b", "0o", "0x" prefixes.
            # We might want to strip them for cleaner display in the entry.
            formatted_res = self.format_int_to_base(result_val, base)
            display_res = formatted_res
            if base == 2: display_res = formatted_res.replace('0b', '')
            elif base == 8: display_res = formatted_res.replace('0o', '')
            elif base == 16: display_res = formatted_res.replace('0x', '')
            if result_val < 0 and base != 10: # Add note for negative numbers in non-decimal bases
                display_res += f" (نمایش مبنای ۲ برای اعداد منفی: {bin(result_val)})"

            self._display_bitwise_result(f"نتیجه: {display_res}")
        else:
            self._display_bitwise_result("عملیات نامعتبر انتخاب شده یا خطایی رخ داده است.")


    # Placeholder for Unit Conversion Window
    def open_units_window(self):
        self.unit_conv_window = tk.Toplevel(self.master)
        self.unit_conv_window.title("تبدیل واحد (Unit Conversion)")
        self.unit_conv_window.geometry("650x500")

        # --- Category and Unit Selection Frame ---
        selection_frame = ttk.LabelFrame(self.unit_conv_window, text="انتخاب نوع واحد و واحدها")
        selection_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(selection_frame, text="دسته بندی واحد:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.unit_category_var = tk.StringVar()

        # Define unit categories and their units with conversion factors relative to a base unit
        self.unit_data = {
            "طول": {
                "متر (m)": 1.0, "کیلومتر (km)": 1000.0, "سانتی‌متر (cm)": 0.01, "میلی‌متر (mm)": 0.001,
                "اینچ (in)": 0.0254, "فوت (ft)": 0.3048, "یارد (yd)": 0.9144, "مایل (mi)": 1609.34
            },
            "جرم": {
                "کیلوگرم (kg)": 1.0, "گرم (g)": 0.001, "میلی‌گرم (mg)": 1e-6, "تن (tonne)": 1000.0,
                "پوند (lb)": 0.453592, "اونس (oz)": 0.0283495
            },
            "دما": { # Temperature is special due to offsets, not just factors
                "سانتی‌گراد (°C)": "C", "فارنهایت (°F)": "F", "کلوین (K)": "K"
            },
            "زمان": {
                "ثانیه (s)": 1.0, "دقیقه (min)": 60.0, "ساعت (hr)": 3600.0,
                "روز (day)": 86400.0, "میلی‌ثانیه (ms)": 0.001
            },
            "مساحت": {
                "متر مربع (m²)": 1.0, "کیلومتر مربع (km²)": 1e6, "هکتار (ha)": 10000.0,
                "فوت مربع (ft²)": 0.092903, "اینچ مربع (in²)": 0.00064516
            },
            "حجم": {
                "متر مکعب (m³)": 1.0, "لیتر (L)": 0.001, "میلی‌لیتر (mL)": 1e-6,
                "فوت مکعب (ft³)": 0.0283168, "اینچ مکعب (in³)": 1.6387e-5, "گالن آمریکایی (US gal)": 0.00378541
            },
            "سرعت": {
                "متر بر ثانیه (m/s)": 1.0, "کیلومتر بر ساعت (km/h)": 1/3.6,
                "مایل بر ساعت (mph)": 0.44704, "فوت بر ثانیه (ft/s)": 0.3048
            },
            "فشار": {
                "پاسکال (Pa)": 1.0, "کیلوپاسکال (kPa)": 1000.0, "بار (bar)": 100000.0,
                "اتمسفر استاندارد (atm)": 101325.0, "میلی‌متر جیوه (mmHg)": 133.322, "پوند بر اینچ مربع (psi)": 6894.76
            },
            "انرژی/کار": {
                "ژول (J)": 1.0, "کیلوژول (kJ)": 1000.0, "کالری (cal)": 4.184, "کیلوکالری (kcal)": 4184.0,
                "وات‌ساعت (Wh)": 3600.0, "کیلووات‌ساعت (kWh)": 3.6e6, "الکترون‌ولت (eV)": 1.60218e-19
            },
            "توان": {
                "وات (W)": 1.0, "کیلووات (kW)": 1000.0, "اسب بخار (hp)": 745.7
            }
        }
        categories = list(self.unit_data.keys())
        # Ensure a default category is selected if the list is not empty
        default_category = categories[0] if categories else ""
        self.unit_category_menu = ttk.OptionMenu(selection_frame, self.unit_category_var, default_category, *categories, command=self.update_unit_menus)
        self.unit_category_menu.grid(row=0, column=1, columnspan=3, padx=5, pady=5, sticky="ew")

        ttk.Label(selection_frame, text="از واحد:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.from_unit_var = tk.StringVar()
        self.from_unit_menu = ttk.OptionMenu(selection_frame, self.from_unit_var, "")
        self.from_unit_menu.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(selection_frame, text="به واحد:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.to_unit_var = tk.StringVar()
        self.to_unit_menu = ttk.OptionMenu(selection_frame, self.to_unit_var, "")
        self.to_unit_menu.grid(row=1, column=3, padx=5, pady=5, sticky="ew")

        selection_frame.grid_columnconfigure(1, weight=1)
        selection_frame.grid_columnconfigure(3, weight=1)

        # Initialize unit menus for the first category
        self.update_unit_menus(categories[0])


        # --- Input and Output Frame ---
        io_frame = ttk.LabelFrame(self.unit_conv_window, text="مقدار و نتیجه")
        io_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(io_frame, text="مقدار برای تبدیل:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.unit_input_value_entry = ttk.Entry(io_frame, width=20)
        self.unit_input_value_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        convert_button = ttk.Button(io_frame, text="تبدیل", command=self.perform_unit_conversion)
        convert_button.grid(row=0, column=2, padx=10, pady=5)

        ttk.Label(io_frame, text="نتیجه تبدیل:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.unit_result_var = tk.StringVar(value="نتیجه در اینجا نمایش داده می‌شود.")
        unit_result_label = ttk.Label(io_frame, textvariable=self.unit_result_var, font=('Arial', 12), foreground="blue")
        unit_result_label.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="ew")

        io_frame.grid_columnconfigure(1, weight=1)

    def update_unit_menus(self, selected_category):
        units = list(self.unit_data[selected_category].keys())

        # Update "From Unit" menu
        self.from_unit_var.set(units[0] if units else "")
        menu = self.from_unit_menu["menu"]
        menu.delete(0, "end")
        for unit in units:
            menu.add_command(label=unit, command=lambda u=unit: self.from_unit_var.set(u))

        # Update "To Unit" menu
        self.to_unit_var.set(units[1] if len(units)>1 else (units[0] if units else ""))
        menu = self.to_unit_menu["menu"]
        menu.delete(0, "end")
        for unit in units:
            menu.add_command(label=unit, command=lambda u=unit: self.to_unit_var.set(u))

        self.unit_result_var.set("نتیجه در اینجا نمایش داده می‌شود.") # Clear previous result

    def convert_temperature(self, value, from_unit_key, to_unit_key):
        # from_unit_key, to_unit_key are 'C', 'F', 'K'
        val = float(value)
        res = 0.0
        if from_unit_key == 'C':
            if to_unit_key == 'F': res = (val * 9/5) + 32
            elif to_unit_key == 'K': res = val + 273.15
            elif to_unit_key == 'C': res = val
        elif from_unit_key == 'F':
            if to_unit_key == 'C': res = (val - 32) * 5/9
            elif to_unit_key == 'K': res = (val - 32) * 5/9 + 273.15
            elif to_unit_key == 'F': res = val
        elif from_unit_key == 'K':
            if to_unit_key == 'C': res = val - 273.15
            elif to_unit_key == 'F': res = (val - 273.15) * 9/5 + 32
            elif to_unit_key == 'K': res = val
        else: return None # Should not happen
        return res


    def perform_unit_conversion(self):
        category = self.unit_category_var.get()
        from_unit_display_name = self.from_unit_var.get()
        to_unit_display_name = self.to_unit_var.get()

        try:
            input_value = float(self.unit_input_value_entry.get())
        except ValueError:
            self.unit_result_var.set("خطا: مقدار ورودی باید یک عدد باشد.")
            return

        if not from_unit_display_name or not to_unit_display_name:
            self.unit_result_var.set("خطا: لطفاً واحدهای مبدا و مقصد را انتخاب کنید.")
            return

        category_units = self.unit_data[category]

        if category == "دما":
            # Temperature conversion uses specific formulas
            from_unit_key = category_units[from_unit_display_name] # 'C', 'F', or 'K'
            to_unit_key = category_units[to_unit_display_name]
            converted_value = self.convert_temperature(input_value, from_unit_key, to_unit_key)
            if converted_value is None:
                 self.unit_result_var.set("خطا در تبدیل دما.")
                 return
        else:
            # Factor-based conversion
            from_factor = category_units[from_unit_display_name]
            to_factor = category_units[to_unit_display_name]

            # Convert input value to base unit, then to target unit
            value_in_base_unit = input_value * from_factor
            converted_value = value_in_base_unit / to_factor

        self.unit_result_var.set(f"{converted_value:.6g} {to_unit_display_name.split('(')[0].strip()}")


    # Placeholder for Statistics Window
    def open_stats_window(self):
        self.stats_window = tk.Toplevel(self.master)
        self.stats_window.title("محاسبات آماری پایه")
        self.stats_window.geometry("500x400")

        # --- Input Data Frame ---
        input_frame = ttk.LabelFrame(self.stats_window, text="ورود داده‌ها")
        input_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(input_frame, text="داده‌ها (با کاما جدا شوند):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.stats_data_entry = ttk.Entry(input_frame, width=50)
        self.stats_data_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.stats_data_entry.insert(0, "1, 2, 3, 4, 5, 5, 6, 7, 8, 9") # Example data

        input_frame.grid_columnconfigure(1, weight=1)

        calc_stats_button = ttk.Button(input_frame, text="محاسبه آمار", command=self.calculate_basic_stats)
        calc_stats_button.grid(row=1, column=0, columnspan=2, pady=10)

        # --- Result Display ---
        result_frame = ttk.LabelFrame(self.stats_window, text="نتایج آماری")
        result_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.stats_result_text = tk.Text(result_frame, height=10, width=60, state='disabled', font=('Arial', 11))
        self.stats_result_text.pack(padx=5, pady=5, fill="both", expand=True)

    def _display_stats_result(self, message, clear=True):
        self.stats_result_text.config(state='normal')
        if clear:
            self.stats_result_text.delete('1.0', tk.END)
        self.stats_result_text.insert(tk.END, message + "\n")
        self.stats_result_text.config(state='disabled')

    def parse_stats_data(self, data_str):
        try:
            data_points = np.array(list(map(float, data_str.split(','))))
            if len(data_points) == 0:
                self._display_stats_result("خطا: حداقل یک نقطه داده برای محاسبات آماری نیاز است.")
                return None
            return data_points
        except ValueError:
            self._display_stats_result("خطا: داده‌ها باید اعداد معتبر باشند و با کاما از هم جدا شوند.")
            return None

    def calculate_basic_stats(self):
        data_str = self.stats_data_entry.get()
        if not data_str:
            self._display_stats_result("خطا: لطفاً داده‌ها را وارد کنید.")
            return

        data = self.parse_stats_data(data_str)
        if data is None:
            return

        results = []
        results.append(f"تعداد داده‌ها: {len(data)}")
        results.append(f"میانگین (Mean): {np.mean(data):.4f}")
        results.append(f"میانه (Median): {np.median(data):.4f}")

        try: # Mode calculation can be tricky, especially with multiple modes or non-integer data
            from scipy.stats import mode
            mode_res = mode(data, keepdims=False) # Using keepdims=False for newer scipy versions
            if np.isscalar(mode_res.mode): # Single mode
                 results.append(f"مد (Mode): {mode_res.mode:.4f} (تعداد تکرار: {mode_res.count})")
            else: # Handle multiple modes if array is returned (older scipy or multiple modes)
                 modes_str = ", ".join([f"{m:.4f}" for m in mode_res.mode])
                 counts_str = ", ".join([f"{c}" for c in mode_res.count]) if hasattr(mode_res, 'count') and not np.isscalar(mode_res.count) else str(mode_res.count)
                 results.append(f"مد (Mode(s)): {modes_str} (تعداد تکرار: {counts_str})")

        except ImportError:
            results.append("مد (Mode): برای محاسبه مد، کتابخانه SciPy مورد نیاز است (scipy.stats.mode).")
        except Exception as e_mode: # Catch other potential errors from mode calculation
            results.append(f"مد (Mode): خطا در محاسبه مد - {e_mode}")

        results.append(f"واریانس (Variance - ddof=0): {np.var(data):.4f}") # Population variance
        results.append(f"واریانس نمونه (Variance - ddof=1): {np.var(data, ddof=1):.4f}") # Sample variance
        results.append(f"انحراف معیار (Std Dev - ddof=0): {np.std(data):.4f}") # Population std dev
        results.append(f"انحراف معیار نمونه (Std Dev - ddof=1): {np.std(data, ddof=1):.4f}") # Sample std dev
        results.append(f"حداقل (Minimum): {np.min(data):.4f}")
        results.append(f"حداکثر (Maximum): {np.max(data):.4f}")
        results.append(f"دامنه (Range): {(np.max(data) - np.min(data)):.4f}")
        results.append(f"مجموع (Sum): {np.sum(data):.4f}")

        self._display_stats_result("\n".join(results))

    def open_complex_calculator_window(self):
        self.complex_window = tk.Toplevel(self.master)
        self.complex_window.title("محاسبات اعداد مختلط")
        self.complex_window.geometry("600x450")

        # --- Input Frame ---
        input_frame = ttk.LabelFrame(self.complex_window, text="ورودی اعداد مختلط")
        input_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(input_frame, text="عدد اول (Num1):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.complex_num1_entry = ttk.Entry(input_frame, width=35)
        self.complex_num1_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.complex_num1_entry.insert(0, "3+4j")

        ttk.Label(input_frame, text="عدد دوم (Num2, برای +,-,*,/,pow):").grid(row=1, column=0, padx=5, pady=5, sticky="w") # Corrected label for pow
        self.complex_num2_entry = ttk.Entry(input_frame, width=35)
        self.complex_num2_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.complex_num2_entry.insert(0, "1-2j")

        input_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(input_frame, text="نمایش نتیجه:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.complex_display_mode_var = tk.StringVar(value="rect") # rect or polar
        rect_radio = ttk.Radiobutton(input_frame, text="دکارتی (a+bj)", variable=self.complex_display_mode_var, value="rect")
        rect_radio.grid(row=0, column=3, padx=5, pady=2, sticky="w")
        polar_radio = ttk.Radiobutton(input_frame, text="قطبی (r∠θ°)", variable=self.complex_display_mode_var, value="polar")
        polar_radio.grid(row=1, column=3, padx=5, pady=2, sticky="w")


        # --- Operations Frame ---
        ops_frame = ttk.LabelFrame(self.complex_window, text="عملیات")
        ops_frame.pack(padx=10, pady=5, fill="x")

        complex_ops = [
            ("Num1 + Num2", "+"), ("Num1 - Num2", "-"),
            ("Num1 * Num2", "*"), ("Num1 / Num2", "/"),
            ("قدرمطلق Num1", "abs"), ("فاز Num1 (°)", "phase"),
            ("مزدوج Num1", "conj"), ("معکوس Num1", "inv"),
            ("sqrt(Num1)", "sqrt"), ("ln(Num1)", "ln"),
            ("exp(Num1)", "exp"), ("Num1 ^ Num2", "pow") # Simplified label
        ]

        row, col = 0, 0
        for text, op_key in complex_ops:
            btn = ttk.Button(ops_frame, text=text, command=lambda k=op_key: self.perform_complex_operation(k))
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            col += 1
            if col > 2: # Three buttons per row
                col = 0
                row += 1
        for i in range(3): ops_frame.grid_columnconfigure(i, weight=1)


        # --- Result Display ---
        result_frame = ttk.LabelFrame(self.complex_window, text="نتیجه")
        result_frame.pack(padx=10, pady=10, fill="both", expand=True)
        self.complex_result_text = tk.Text(result_frame, height=5, width=60, state='disabled', font=('Arial', 12))
        self.complex_result_text.pack(padx=5, pady=5, fill="both", expand=True)

    def _display_complex_result(self, message):
        self.complex_result_text.config(state='normal')
        self.complex_result_text.delete('1.0', tk.END)
        self.complex_result_text.insert(tk.END, message)
        self.complex_result_text.config(state='disabled')

    def parse_complex_from_entry(self, entry_widget):
        val_str = entry_widget.get().strip().lower() # convert to lower for 'j' or 'i'
        if not val_str: return None, "ورودی خالی است."
        try:
            # Python's complex() constructor handles "a+bj" format well.
            # For polar input like "r<angle_deg" or "r∠angle_deg"
            if '<' in val_str or '∠' in val_str:
                 val_str_processed = val_str.replace('∠', '<')
                 parts = val_str_processed.split('<')
                 if len(parts) != 2:
                     raise ValueError("فرمت قطبی نامعتبر است. باید به صورت r<angle یا r∠angle باشد.")
                 r = float(parts[0])
                 angle_deg = float(parts[1])
                 angle_rad = np.deg2rad(angle_deg)
                 return cmath.rect(r, angle_rad), None # cmath needed here
            return complex(val_str.replace("i","j")), None # Allow 'i' as well as 'j'
        except ValueError:
            return None, f"مقدار '{val_str}' به عنوان عدد مختلط معتبر نیست (مثال: 3+4j یا 5∠30)."
        except Exception as e: # Catch any other parsing error
            return None, f"خطا در پارس عدد مختلط: {e}"

    def format_complex_number(self, c_num, mode="rect"):
        # cmath may not be imported globally, ensure it is for polar
        import cmath
        if mode == "rect":
            return f"{c_num.real:.4f} {'+' if c_num.imag >= 0 else '-'} {abs(c_num.imag):.4f}j"
        elif mode == "polar":
            r, phi_rad = cmath.polar(c_num)
            phi_deg = np.rad2deg(phi_rad)
            return f"{r:.4f} ∠ {phi_deg:.2f}°"
        return str(c_num) # Fallback

    def perform_complex_operation(self, op_key):
        import cmath # Use cmath for complex versions of math functions

        num1_c, err1 = self.parse_complex_from_entry(self.complex_num1_entry)
        if err1: self._display_complex_result(f"عدد اول: {err1}"); return

        result_c = None
        display_mode = self.complex_display_mode_var.get()

        if op_key in ["+", "-", "*", "/", "pow"]:
            num2_c, err2 = self.parse_complex_from_entry(self.complex_num2_entry)
            if err2: self._display_complex_result(f"عدد دوم: {err2}"); return

            if op_key == "+": result_c = num1_c + num2_c
            elif op_key == "-": result_c = num1_c - num2_c
            elif op_key == "*": result_c = num1_c * num2_c
            elif op_key == "/":
                if num2_c == 0: self._display_complex_result("خطا: تقسیم بر صفر."); return
                result_c = num1_c / num2_c
            elif op_key == "pow": result_c = num1_c ** num2_c

        elif op_key == "abs": result_c = abs(num1_c) # This will be a float
        elif op_key == "phase": result_c = np.rad2deg(cmath.phase(num1_c)) # This will be a float (degrees)
        elif op_key == "conj": result_c = num1_c.conjugate()
        elif op_key == "inv":
            if num1_c == 0: self._display_complex_result("خطا: معکوس صفر تعریف نشده."); return
            result_c = 1 / num1_c
        elif op_key == "sqrt": result_c = cmath.sqrt(num1_c)
        elif op_key == "ln":
            if num1_c == 0: self._display_complex_result("خطا: لگاریتم صفر تعریف نشده."); return
            result_c = cmath.log(num1_c) # Natural log
        elif op_key == "exp": result_c = cmath.exp(num1_c)

        if result_c is not None:
            if isinstance(result_c, complex):
                self._display_complex_result(f"نتیجه: {self.format_complex_number(result_c, display_mode)}")
            else: # For abs, phase which return float
                self._display_complex_result(f"نتیجه: {result_c:.4f}")
        # else: # This case should ideally be caught by specific error messages or if op_key is invalid
            # self._display_complex_result("عملیات نامعتبر یا خطایی رخ داده است.")


    def open_special_functions_window(self):
        self.spec_func_window = tk.Toplevel(self.master)
        self.spec_func_window.title("توابع خاص ریاضی (SciPy.special)")
        self.spec_func_window.geometry("700x550") # Adjusted size

        # --- Function Selection Frame ---
        selection_frame = ttk.LabelFrame(self.spec_func_window, text="انتخاب تابع و ورود پارامترها")
        selection_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(selection_frame, text="انتخاب تابع:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.spec_func_var = tk.StringVar()

        # Define special functions and their required parameters (name in UI: (actual_scipy_func_name, [param_names_list], [param_defaults_list]))
        self.special_functions_map = {
            "تابع گاما (Gamma Γ(x))": ("gamma", ["x"], ["1.5"]),
            "تابع لگاریتم گاما (Log-Gamma ln(Γ(x)))": ("gammaln", ["x"], ["1.5"]),
            "تابع خطا (Error Function erf(x))": ("erf", ["x"], ["0.5"]),
            "تابع خطای مکمل (Complementary erf erfc(x))": ("erfc", ["x"], ["0.5"]),
            "تابع بسل نوع اول (Bessel Jν(x))": ("jv", ["ν (order)", "x"], ["0", "1.0"]), #jv(order, x)
            "تابع بسل نوع دوم (Bessel Yν(x))": ("yv", ["ν (order)", "x"], ["0", "1.0"]), #yv(order, x)
            "تابع زتای ریمان (Riemann Zeta ζ(x))": ("zeta", ["x", "q (اختیاری, برای Hurwitz zeta)"], ["2.0", ""]), # zeta(x, q)
            "چندجمله‌ای لژاندر (Pn(x))": ("eval_legendre", ["n (degree)", "x"], ["2", "0.5"]), # eval_legendre(degree, x)
            "چندجمله‌ای هرمیت (Hn(x) - فیزیکدانان)": ("eval_hermite", ["n (degree)", "x"], ["2", "0.5"]),
            "تابع بیضوی کامل نوع اول (K(m))": ("ellipk", ["m (parameter)"], ["0.5"]), # ellipk(m)
            "تابع بیضوی کامل نوع دوم (E(m))": ("ellipe", ["m (parameter)"], ["0.5"]), # ellipe(m)
            # Add more as needed: beta, psi, airy, etc.
        }
        func_display_names = list(self.special_functions_map.keys())
        self.spec_func_menu = ttk.OptionMenu(selection_frame, self.spec_func_var, func_display_names[0], *func_display_names, command=self.update_spec_func_params_ui)
        self.spec_func_menu.grid(row=0, column=1, columnspan=3, padx=5, pady=5, sticky="ew")
        selection_frame.grid_columnconfigure(1, weight=1)

        # --- Parameter Input Frame (Dynamically populated) ---
        self.spec_func_params_frame = ttk.Frame(selection_frame)
        self.spec_func_params_frame.grid(row=1, column=0, columnspan=4, padx=5, pady=10, sticky="ew")
        self.spec_func_param_entries = [] # To store Entry widgets for parameters

        # Initialize params UI for the first function
        self.update_spec_func_params_ui(func_display_names[0])

        # --- Calculation Button ---
        calc_button = ttk.Button(selection_frame, text="محاسبه تابع", command=self.perform_special_function_calc)
        calc_button.grid(row=2, column=0, columnspan=4, pady=10)


        # --- Result Display ---
        result_frame = ttk.LabelFrame(self.spec_func_window, text="نتیجه محاسبه تابع خاص")
        result_frame.pack(padx=10, pady=10, fill="both", expand=True)
        self.spec_func_result_text = tk.Text(result_frame, height=8, width=70, state='disabled', font=('Arial', 12))
        self.spec_func_result_text.pack(padx=5, pady=5, fill="both", expand=True)

    def update_spec_func_params_ui(self, selected_func_display_name):
        # Clear previous parameter entries
        for widget in self.spec_func_params_frame.winfo_children():
            widget.destroy()
        self.spec_func_param_entries.clear()

        func_key = selected_func_display_name
        if func_key not in self.special_functions_map: return

        _, param_names, param_defaults = self.special_functions_map[func_key]

        for i, (p_name, p_default) in enumerate(zip(param_names, param_defaults)):
            ttk.Label(self.spec_func_params_frame, text=f"{p_name}:").grid(row=i, column=0, padx=5, pady=3, sticky="w")
            entry = ttk.Entry(self.spec_func_params_frame, width=15)
            entry.grid(row=i, column=1, padx=5, pady=3, sticky="ew")
            if p_default:
                entry.insert(0, p_default)
            self.spec_func_param_entries.append(entry)

        self.spec_func_params_frame.grid_columnconfigure(1, weight=1)
        self._display_spec_func_result("پارامترها را وارد کرده و محاسبه را بزنید.", clear=True)


    def _display_spec_func_result(self, message, clear=True):
        self.spec_func_result_text.config(state='normal')
        if clear:
            self.spec_func_result_text.delete('1.0', tk.END)
        self.spec_func_result_text.insert(tk.END, message + "\n")
        self.spec_func_result_text.config(state='disabled')

    def perform_special_function_calc(self):
        selected_func_display_name = self.spec_func_var.get()
        if not selected_func_display_name or selected_func_display_name not in self.special_functions_map:
            self._display_spec_func_result("خطا: لطفاً یک تابع خاص را انتخاب کنید.")
            return

        func_scipy_name, param_names, _ = self.special_functions_map[selected_func_display_name]

        params_values = []
        try:
            for i, entry_widget in enumerate(self.spec_func_param_entries):
                val_str = entry_widget.get().strip()
                # For Hurwitz zeta, the second param 'q' is optional.
                # If empty and param is optional (e.g. 'q' for zeta), we might skip it or pass None.
                if func_scipy_name == "zeta" and i == 1 and not val_str: # Optional q for zeta
                    params_values.append(None) # Will be filtered out later if function doesn't take None
                    continue
                if not val_str and not (func_scipy_name == "zeta" and i == 1) : # Check if required param is empty
                     self._display_spec_func_result(f"خطا: پارامتر '{param_names[i]}' نمی‌تواند خالی باشد.")
                     return
                params_values.append(float(val_str))
        except ValueError as ve:
            self._display_spec_func_result(f"خطا در تبدیل پارامتر به عدد: {ve}")
            return

        try:
            from scipy import special
            if not hasattr(special, func_scipy_name):
                self._display_spec_func_result(f"خطا: تابع '{func_scipy_name}' در scipy.special یافت نشد.")
                return

            scipy_func = getattr(special, func_scipy_name)

            # Filter out None parameters (like optional q for zeta if not provided)
            actual_params = [p for p in params_values if p is not None]

            # For functions like jv, yv, order of parameters matters.
            # Our param_names list order should match scipy's function signature.
            result = scipy_func(*actual_params)

            self._display_spec_func_result(f"نتیجه {selected_func_display_name} با پارامترهای {actual_params}:\n{result:.8g}", clear=True)

        except ImportError:
            self._display_spec_func_result("خطا: کتابخانه SciPy (scipy.special) برای این محاسبه مورد نیاز است.")
        except Exception as e:
            self._display_spec_func_result(f"خطا در محاسبه تابع خاص: {e}")

    def open_sys_nonlinear_eq_window(self):
        self.sys_eq_window = tk.Toplevel(self.master)
        self.sys_eq_window.title("حل دستگاه معادلات غیرخطی")
        self.sys_eq_window.geometry("750x650") # Slightly wider for better layout

        # --- Number of Variables/Equations Selection ---
        num_vars_frame = ttk.LabelFrame(self.sys_eq_window, text="تعداد متغیرها/معادلات")
        num_vars_frame.pack(padx=10, pady=5, fill="x")

        ttk.Label(num_vars_frame, text="تعداد متغیرها (n):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.sys_eq_num_vars_var = tk.IntVar(value=2) # Default to 2 variables
        self.sys_eq_num_vars_spinbox = ttk.Spinbox(num_vars_frame, from_=1, to=10, textvariable=self.sys_eq_num_vars_var, width=5, command=self.update_sys_eq_entries_ui)
        self.sys_eq_num_vars_spinbox.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # --- Equations and Guesses Input (Dynamically created) ---
        self.sys_eq_entries_frame = ttk.Frame(self.sys_eq_window)
        self.sys_eq_entries_frame.pack(padx=10, pady=5, fill="x")

        self.sys_eq_equation_entries = [] # List of Entry widgets for equations
        self.sys_eq_guess_entries = []    # List of Entry widgets for initial guesses

        self.update_sys_eq_entries_ui() # Initial call to create entries for default num_vars

        # --- Solve Button ---
        solve_button = ttk.Button(self.sys_eq_window, text="حل دستگاه معادلات", command=self.solve_system_nonlinear_equations)
        solve_button.pack(pady=15)

        # --- Result Display ---
        result_frame = ttk.LabelFrame(self.sys_eq_window, text="نتیجه حل")
        result_frame.pack(padx=10, pady=10, fill="both", expand=True)
        self.sys_eq_result_text = tk.Text(result_frame, height=10, width=80, state='disabled', font=('Arial', 11))
        self.sys_eq_result_text.pack(padx=5, pady=5, fill="both", expand=True)

    def update_sys_eq_entries_ui(self):
        # Clear previous entries
        for widget in self.sys_eq_entries_frame.winfo_children():
            widget.destroy()
        self.sys_eq_equation_entries.clear()
        self.sys_eq_guess_entries.clear()

        try:
            num_vars = self.sys_eq_num_vars_var.get()
            if num_vars < 1:
                self.sys_eq_num_vars_var.set(1)
                num_vars = 1
        except tk.TclError: # If spinbox is empty or invalid during typing
            num_vars = 1 # Default to 1 if there's an issue
            self.sys_eq_num_vars_var.set(1)


        eq_input_frame = ttk.LabelFrame(self.sys_eq_entries_frame, text="معادلات (f_i(x1,..,xn)=0)")
        eq_input_frame.pack(side=tk.LEFT, padx=5, pady=5, fill="y", expand=False)

        guess_input_frame = ttk.LabelFrame(self.sys_eq_entries_frame, text="حدس‌های اولیه (xi_0)")
        guess_input_frame.pack(side=tk.LEFT, padx=5, pady=5, fill="y", expand=False)

        # Default examples for 2 variables
        default_eqs = ["x1**2 + x2**2 - 4", "x1*x2 - 1", "x1**3 - x2", "x1*sin(x2) - x3", "x1+x2+x3-1"]
        default_guesses = ["1.0", "1.0", "0.5", "0.5", "0.3"]


        for i in range(num_vars):
            # Equation Entry
            ttk.Label(eq_input_frame, text=f"f{i+1}({', '.join([f'x{j+1}' for j in range(num_vars)])}) =").grid(row=i, column=0, padx=5, pady=3, sticky="w")
            eq_entry = ttk.Entry(eq_input_frame, width=35, font=('Arial', 9))
            eq_entry.grid(row=i, column=1, padx=5, pady=3, sticky="ew")
            if i < len(default_eqs): eq_entry.insert(0, default_eqs[i])
            self.sys_eq_equation_entries.append(eq_entry)

            # Guess Entry
            ttk.Label(guess_input_frame, text=f"x{i+1}_0:").grid(row=i, column=0, padx=5, pady=3, sticky="w")
            guess_entry = ttk.Entry(guess_input_frame, width=10, font=('Arial', 9))
            guess_entry.grid(row=i, column=1, padx=5, pady=3, sticky="ew")
            if i < len(default_guesses): guess_entry.insert(0, default_guesses[i])
            self.sys_eq_guess_entries.append(guess_entry)

        eq_input_frame.grid_columnconfigure(1, weight=1)
        guess_input_frame.grid_columnconfigure(1, weight=1)
        self._display_sys_eq_result("تعداد متغیرها را انتخاب، معادلات و حدس‌های اولیه را وارد کنید.", clear=True)


    def _display_sys_eq_result(self, message, clear=True):
        self.sys_eq_result_text.config(state='normal')
        if clear:
            self.sys_eq_result_text.delete('1.0', tk.END)
        self.sys_eq_result_text.insert(tk.END, message + "\n")
        self.sys_eq_result_text.config(state='disabled')

    def solve_system_nonlinear_equations(self):
        num_vars = self.sys_eq_num_vars_var.get()
        eq_strs = []
        for entry in self.sys_eq_equation_entries:
            eq_str = entry.get().strip()
            if eq_str: # Only consider non-empty equation strings
                eq_strs.append(eq_str)

        initial_guesses_str = []
        for entry in self.sys_eq_guess_entries:
            guess_str = entry.get().strip()
            if guess_str: # Only consider non-empty guess strings
                initial_guesses_str.append(guess_str)

        if len(eq_strs) != num_vars or len(initial_guesses_str) != num_vars:
            self._display_sys_eq_result(f"خطا: باید دقیقاً {num_vars} معادله و {num_vars} حدس اولیه وارد شود.")
            return
        if num_vars == 0 : # Should be caught by spinbox from_=1
             self._display_sys_eq_result(f"خطا: تعداد متغیرها باید حداقل ۱ باشد.")
             return

        try:
            initial_guesses = np.array(list(map(float, initial_guesses_str)))
        except ValueError:
            self._display_sys_eq_result("خطا: حدس‌های اولیه باید اعداد معتبر باشند.")
            return

        var_names = [f'x{i+1}' for i in range(num_vars)]

        def system_functions(vars_tuple):
            # vars_tuple will be (x1, x2, ..., xn)
            # We need to create a local scope for eval that includes these variable names
            # and numpy functions.
            local_scope = {"np": np, "sin": np.sin, "cos": np.cos, "tan": np.tan,
                           "exp": np.exp, "log": np.log, "log10": np.log10, "sqrt": np.sqrt,
                           "pi": np.pi, "e": np.e}
            for i, var_name in enumerate(var_names):
                local_scope[var_name] = vars_tuple[i]

            eval_results = []
            for i, eq_str in enumerate(eq_strs):
                try:
                    eval_results.append(eval(eq_str, {"__builtins__": {}}, local_scope))
                except Exception as e_eval:
                    # This error will be caught by the outer try-except,
                    # but it's good to know where it might originate.
                    raise ValueError(f"خطا در ارزیابی معادله {i+1} ('{eq_str}'): {e_eval}")
            return eval_results

        from scipy.optimize import root

        try:
            # Test the system_functions with initial guesses to catch early eval errors
            initial_eval_test = system_functions(initial_guesses)
            self._display_sys_eq_result(f"تست ارزیابی اولیه با حدس‌ها: {initial_eval_test}", clear=True)

            solution = root(system_functions, initial_guesses, method='hybr') # 'hybr' is often a good default

            if solution.success:
                res_str = "ریشه‌های پیدا شده:\n"
                for i, var_name in enumerate(var_names):
                    res_str += f"  {var_name} = {solution.x[i]:.6f}\n"
                res_str += f"\nپیام حل کننده: {solution.message}"
                res_str += f"\nتعداد ارزیابی‌های تابع: {solution.nfev}"
                self._display_sys_eq_result(res_str, clear=False) # Append to initial eval test
            else:
                self._display_sys_eq_result(f"حل کننده با موفقیت همگرا نشد.\nپیام: {solution.message}\nآخرین مقادیر x: {solution.x}", clear=False)

        except ValueError as ve: # Catch eval errors from system_functions
             self._display_sys_eq_result(f"خطا در تعریف دستگاه معادلات: {ve}")
        except ImportError:
            self._display_sys_eq_result("خطا: کتابخانه SciPy (scipy.optimize.root) برای این محاسبه مورد نیاز است.")
        except Exception as e:
            self._display_sys_eq_result(f"خطای کلی در حل دستگاه: {e}")


    def open_optimization_window(self):
        self.opt_window = tk.Toplevel(self.master)
        self.opt_window.title("بهینه‌سازی (Optimization)")
        self.opt_window.geometry("700x600")

        # --- Info and Instructions ---
        info_frame = ttk.LabelFrame(self.opt_window, text="راهنما")
        info_frame.pack(padx=10, pady=5, fill="x")
        info_text_opt = """\
        - تابع هدف خود را برای مینیمم‌سازی وارد کنید.
        - برای بهینه‌سازی تک متغیره (scalar):
            - تابع f(x) را وارد کنید.
            - بازه جستجو [a, b] را مشخص کنید (اختیاری اما توصیه می‌شود).
        - برای بهینه‌سازی چند متغیره:
            - تابع f(x1, x2, ..., xn) را وارد کنید.
            - حدس‌های اولیه برای x1, x2, ... را با کاما جدا کنید.
        - از متغیرهای x یا x1, x2, ... استفاده کنید.
        """
        ttk.Label(info_frame, text=info_text_opt, justify=tk.LEFT).pack(padx=5, pady=5, anchor="w")

        # --- Optimization Type ---
        type_frame = ttk.LabelFrame(self.opt_window, text="نوع بهینه‌سازی")
        type_frame.pack(padx=10, pady=5, fill="x")
        self.opt_type_var = tk.StringVar(value="scalar")
        scalar_rb = ttk.Radiobutton(type_frame, text="تک متغیره (Scalar)", variable=self.opt_type_var, value="scalar", command=self.update_optimization_inputs)
        scalar_rb.grid(row=0, column=0, padx=5, pady=2, sticky="w")
        multivar_rb = ttk.Radiobutton(type_frame, text="چند متغیره (Multivariate)", variable=self.opt_type_var, value="multivariate", command=self.update_optimization_inputs)
        multivar_rb.grid(row=0, column=1, padx=5, pady=2, sticky="w")


        # --- Function and Parameters Input ---
        self.opt_input_frame = ttk.Frame(self.opt_window) # Will hold specific inputs
        self.opt_input_frame.pack(padx=10, pady=5, fill="x")

        # Common: Function Entry
        ttk.Label(self.opt_input_frame, text="تابع هدف f(...):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.opt_func_entry = ttk.Entry(self.opt_input_frame, width=50)
        self.opt_func_entry.grid(row=0, column=1, columnspan=3, padx=5, pady=5, sticky="ew")
        self.opt_func_entry.insert(0, "(x-2)**2 + 5") # Example for scalar

        # Scalar Specific Inputs
        self.opt_scalar_bounds_label = ttk.Label(self.opt_input_frame, text="بازه جستجو [a, b] (اختیاری, مثال: 0,5):")
        self.opt_scalar_bounds_entry = ttk.Entry(self.opt_input_frame, width=20)
        self.opt_scalar_method_label = ttk.Label(self.opt_input_frame, text="متد (scalar):")
        self.opt_scalar_method_var = tk.StringVar(value="Brent")
        self.opt_scalar_methods = ["Brent", "Bounded", "Golden"] # From minimize_scalar
        self.opt_scalar_method_menu = ttk.OptionMenu(self.opt_input_frame, self.opt_scalar_method_var, self.opt_scalar_methods[0], *self.opt_scalar_methods)

        # Multivariate Specific Inputs
        self.opt_multi_guesses_label = ttk.Label(self.opt_input_frame, text="حدس‌های اولیه (x1_0, x2_0, ...):")
        self.opt_multi_guesses_entry = ttk.Entry(self.opt_input_frame, width=40)
        self.opt_multi_method_label = ttk.Label(self.opt_input_frame, text="متد (multivariate):")
        self.opt_multi_method_var = tk.StringVar(value="Nelder-Mead")
        self.opt_multi_methods = ["Nelder-Mead", "Powell", "CG", "BFGS", "L-BFGS-B", "TNC", "SLSQP"] # From minimize
        self.opt_multi_method_menu = ttk.OptionMenu(self.opt_input_frame, self.opt_multi_method_var, self.opt_multi_methods[0], *self.opt_multi_methods)
        self.opt_multi_bounds_label = ttk.Label(self.opt_input_frame, text="کران‌ها (اختیاری, مثال: (0,None);(None,10)):") # For methods like L-BFGS-B, TNC, SLSQP
        self.opt_multi_bounds_entry = ttk.Entry(self.opt_input_frame, width=40)


        self.opt_input_frame.grid_columnconfigure(1, weight=1)
        self.update_optimization_inputs() # Initial call to set up UI

        # --- Solve Button ---
        solve_button = ttk.Button(self.opt_window, text="بهینه‌سازی (مینیمم‌سازی)", command=self.perform_optimization)
        solve_button.pack(pady=10)

        # --- Result Display ---
        result_frame = ttk.LabelFrame(self.opt_window, text="نتیجه بهینه‌سازی")
        result_frame.pack(padx=10, pady=10, fill="both", expand=True)
        self.opt_result_text = tk.Text(result_frame, height=10, width=80, state='disabled', font=('Arial', 11))
        self.opt_result_text.pack(padx=5, pady=5, fill="both", expand=True)

    def update_optimization_inputs(self):
        opt_type = self.opt_type_var.get()

        # Clear previous specific inputs (except the common function entry)
        # Iterate over children of opt_input_frame, skipping the first row (func entry)
        for widget in self.opt_input_frame.winfo_children():
            if widget not in [self.opt_func_entry.master.grid_slaves(row=0, column=0)[0], self.opt_func_entry]: # Check label and entry
                 # A bit complex to check if widget is the label or entry of the func_entry row.
                 # Simpler: just check grid_info, if row > 0, then hide/remove.
                 info = widget.grid_info()
                 if info and info['row'] > 0:
                    widget.grid_remove()


        if opt_type == "scalar":
            self.opt_func_entry.delete(0, tk.END)
            self.opt_func_entry.insert(0, "(x-2)**2 + 5") # Example for scalar
            self.opt_scalar_bounds_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
            self.opt_scalar_bounds_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
            self.opt_scalar_bounds_entry.delete(0, tk.END)
            self.opt_scalar_bounds_entry.insert(0, "0, 10") # Example bounds
            self.opt_scalar_method_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
            self.opt_scalar_method_menu.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        elif opt_type == "multivariate":
            self.opt_func_entry.delete(0, tk.END)
            self.opt_func_entry.insert(0, "(x1-1)**2 + (x2-2.5)**2") # Example for multivariate
            self.opt_multi_guesses_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
            self.opt_multi_guesses_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
            self.opt_multi_guesses_entry.delete(0, tk.END)
            self.opt_multi_guesses_entry.insert(0, "0, 0") # Example guesses
            self.opt_multi_method_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
            self.opt_multi_method_menu.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
            self.opt_multi_bounds_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
            self.opt_multi_bounds_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
            self.opt_multi_bounds_entry.delete(0, tk.END)
            self.opt_multi_bounds_entry.insert(0, "(0,None);(-1,1)") # Example bounds for 2 vars


    def _display_opt_result(self, message, clear=True):
        self.opt_result_text.config(state='normal')
        if clear:
            self.opt_result_text.delete('1.0', tk.END)
        self.opt_result_text.insert(tk.END, message + "\n")
        self.opt_result_text.config(state='disabled')

    def parse_optimization_bounds(self, bounds_str, num_vars=None):
        if not bounds_str: return None
        try:
            # Expected format for multivariate: (min1,max1);(min2,max2);...
            # For scalar: min,max
            if num_vars is None: # Scalar
                parts = list(map(lambda x: None if x.strip().lower() == 'none' else float(x), bounds_str.split(',')))
                if len(parts) != 2: raise ValueError("بازه باید دو مقدار جدا شده با کاما باشد (a,b).")
                return tuple(parts)
            else: # Multivariate
                bound_pairs_str = bounds_str.split(';')
                if len(bound_pairs_str) != num_vars:
                    raise ValueError(f"تعداد کران‌ها ({len(bound_pairs_str)}) باید با تعداد متغیرها ({num_vars}) برابر باشد.")
                bounds = []
                for pair_str in bound_pairs_str:
                    pair_str = pair_str.strip()
                    if not pair_str.startswith("(") or not pair_str.endswith(")"):
                        raise ValueError("هر کران باید به فرم (min,max) باشد.")
                    parts = list(map(lambda x: None if x.strip().lower() == 'none' else float(x), pair_str[1:-1].split(',')))
                    if len(parts) != 2:
                        raise ValueError("هر کران باید دو مقدار (min,max) داشته باشد.")
                    bounds.append(tuple(parts))
                return bounds
        except Exception as e:
            raise ValueError(f"خطا در پارس کران‌ها: {e}. فرمت صحیح برای چندمتغیره: (min1,max1);(min2,max2) و برای تک‌متغیره: min,max")


    def perform_optimization(self):
        func_str = self.opt_func_entry.get().strip()
        opt_type = self.opt_type_var.get()

        if not func_str:
            self._display_opt_result("خطا: لطفاً تابع هدف را وارد کنید.")
            return

        from scipy.optimize import minimize_scalar, minimize

        try:
            if opt_type == "scalar":
                objective_func = lambda x: eval(func_str, {"np": np, "x": x, "sin": np.sin, "cos": np.cos, "tan": np.tan, "exp": np.exp, "log": np.log, "sqrt": np.sqrt, "pi": np.pi, "e": np.e})
                objective_func(0) # Test function with a dummy value

                bounds_str = self.opt_scalar_bounds_entry.get().strip()
                bounds = None
                if bounds_str:
                    bounds = self.parse_optimization_bounds(bounds_str) # Returns (a,b) or raises error

                method = self.opt_scalar_method_var.get()

                # For 'Bounded' method, bounds are mandatory.
                if method.lower() == 'bounded' and not bounds:
                    self._display_opt_result("خطا: برای متد 'Bounded' در بهینه‌سازی تک‌متغیره، بازه جستجو الزامی است.")
                    return

                result = minimize_scalar(objective_func, bounds=bounds, method=method.lower())

                if result.success:
                    self._display_opt_result(f"بهینه‌سازی تک متغیره موفقیت آمیز (متد: {method}):\n"
                                           f"  نقطه مینیمم (x): {result.x:.6f}\n"
                                           f"  مقدار تابع در مینیمم (f(x)): {result.fun:.6f}\n"
                                           f"  تعداد ارزیابی‌های تابع: {result.nfev}")
                else:
                    self._display_opt_result(f"بهینه‌سازی تک متغیره ناموفق (متد: {method}).\nپیام: {result.message}")

            elif opt_type == "multivariate":
                guesses_str = self.opt_multi_guesses_entry.get().strip()
                if not guesses_str:
                    self._display_opt_result("خطا: لطفاً حدس‌های اولیه برای بهینه‌سازی چندمتغیره را وارد کنید.")
                    return

                initial_guesses = np.array(list(map(float, guesses_str.split(','))))
                num_vars = len(initial_guesses)
                var_names = [f'x{i+1}' for i in range(num_vars)]

                def multivariate_objective_func(vars_array):
                    local_scope = {"np": np, "sin": np.sin, "cos": np.cos, "tan": np.tan,
                                   "exp": np.exp, "log": np.log, "sqrt": np.sqrt, "pi": np.pi, "e": np.e}
                    for i, var_name in enumerate(var_names):
                        local_scope[var_name] = vars_array[i]
                    try:
                        return eval(func_str, {"__builtins__": {}}, local_scope)
                    except Exception as e_eval:
                        raise ValueError(f"خطا در ارزیابی تابع هدف چندمتغیره: {e_eval}")

                multivariate_objective_func(initial_guesses) # Test function

                method = self.opt_multi_method_var.get()
                bounds_str = self.opt_multi_bounds_entry.get().strip()
                bounds = None
                if bounds_str:
                    bounds = self.parse_optimization_bounds(bounds_str, num_vars=num_vars)

                # Some methods require bounds (e.g., L-BFGS-B, TNC, SLSQP if bounds are relevant)
                # Other methods like Nelder-Mead, Powell, CG, BFGS don't strictly use box bounds in the same way.
                # SLSQP can also handle constraints, not just bounds.

                result = minimize(multivariate_objective_func, initial_guesses, method=method, bounds=bounds)

                if result.success:
                    res_str = f"بهینه‌سازی چند متغیره موفقیت آمیز (متد: {method}):\n"
                    res_str += "  نقطه مینیمم (x):\n"
                    for i, var_name in enumerate(var_names):
                        res_str += f"    {var_name} = {result.x[i]:.6f}\n"
                    res_str += f"  مقدار تابع در مینیمم (f(x)): {result.fun:.6f}\n"
                    res_str += f"  پیام: {result.message}\n"
                    if hasattr(result, 'nfev'): res_str += f"  تعداد ارزیابی‌های تابع: {result.nfev}\n"
                    if hasattr(result, 'nit'): res_str += f"  تعداد تکرارها: {result.nit}\n"
                    self._display_opt_result(res_str)
                else:
                    self._display_opt_result(f"بهینه‌سازی چند متغیره ناموفق (متد: {method}).\nپیام: {result.message}\nآخرین مقادیر x: {result.x}")

        except ValueError as ve: # Catches errors from parsing bounds or initial guesses or eval
             self._display_opt_result(f"خطای مقدار: {ve}")
        except ImportError:
            self._display_opt_result("خطا: کتابخانه SciPy (scipy.optimize) برای این محاسبه مورد نیاز است.")
        except Exception as e:
            self._display_opt_result(f"خطای کلی در بهینه‌سازی: {e}")

    def open_polynomials_window(self):
        self.poly_window = tk.Toplevel(self.master)
        self.poly_window.title("عملیات چندجمله‌ای‌ها")
        self.poly_window.geometry("650x500")

        # --- Polynomial Input Frame ---
        input_frame = ttk.LabelFrame(self.poly_window, text="ورود چندجمله‌ای‌ها (ضرایب از توان بالا به پایین)")
        input_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(input_frame, text="چندجمله‌ای اول P1 (ضرایب با کاما):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.poly1_coeffs_entry = ttk.Entry(input_frame, width=40)
        self.poly1_coeffs_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.poly1_coeffs_entry.insert(0, "1, 0, -4") # Represents x^2 - 4

        ttk.Label(input_frame, text="چندجمله‌ای دوم P2 (اختیاری):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.poly2_coeffs_entry = ttk.Entry(input_frame, width=40)
        self.poly2_coeffs_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.poly2_coeffs_entry.insert(0, "1, 2") # Represents x + 2

        input_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(input_frame, text="مقدار x (برای ارزیابی P1):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.poly_eval_x_entry = ttk.Entry(input_frame, width=10)
        self.poly_eval_x_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.poly_eval_x_entry.insert(0,"3")


        # --- Operations Frame ---
        ops_frame = ttk.LabelFrame(self.poly_window, text="عملیات")
        ops_frame.pack(padx=10, pady=5, fill="x")

        poly_ops = [
            ("P1 + P2", "add"), ("P1 - P2", "sub"), ("P1 * P2", "mul"),
            ("P1 / P2 (تقسیم)", "div"), ("ریشه‌های P1", "roots"),
            ("مشتق P1", "deriv"), ("انتگرال P1 (بدون ثابت)", "integ"),
            ("ارزیابی P1 در x", "eval")
        ]

        row, col = 0, 0
        for text, op_key in poly_ops:
            btn = ttk.Button(ops_frame, text=text, command=lambda k=op_key: self.perform_polynomial_operation(k))
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            col += 1
            if col > 3: # Four buttons per row
                col = 0
                row += 1
        for i in range(4): ops_frame.grid_columnconfigure(i, weight=1)

        # --- Result Display ---
        result_frame = ttk.LabelFrame(self.poly_window, text="نتیجه عملیات چندجمله‌ای")
        result_frame.pack(padx=10, pady=10, fill="both", expand=True)
        self.poly_result_text = tk.Text(result_frame, height=10, width=70, state='disabled', font=('Arial', 11))
        self.poly_result_text.pack(padx=5, pady=5, fill="both", expand=True)

    def _display_poly_result(self, message, clear=True):
        self.poly_result_text.config(state='normal')
        if clear:
            self.poly_result_text.delete('1.0', tk.END)
        self.poly_result_text.insert(tk.END, message + "\n")
        self.poly_result_text.config(state='disabled')

    def parse_coeffs_to_poly1d(self, coeffs_str, poly_name="چندجمله‌ای"):
        if not coeffs_str: return None, f"ضرایب {poly_name} وارد نشده است."
        try:
            coeffs = np.array(list(map(float, coeffs_str.split(','))))
            if len(coeffs) == 0: return None, f"ضرایب {poly_name} نمی‌تواند خالی باشد."
            return np.poly1d(coeffs), None
        except ValueError:
            return None, f"خطا در پارس ضرایب {poly_name}. باید اعداد جدا شده با کاما باشند."

    def format_poly1d_to_string(self, p, var='x'):
        # Custom formatting for better display than default np.poly1d.__str__
        terms = []
        coeffs = p.coeffs
        degree = p.order
        for i, c in enumerate(coeffs):
            power = degree - i
            if abs(c) < 1e-9: continue # Skip zero terms

            term_str = ""
            # Coefficient
            if abs(c - 1.0) < 1e-9 and power != 0: # Coeff is 1 (and not constant term)
                term_str = "" if not terms else "+ " # Add plus if not first term
            elif abs(c + 1.0) < 1e-9 and power != 0: # Coeff is -1
                 term_str = "- " if not terms else " - "
            else: # General coefficient
                term_str = f"{c:+.2f} " if terms else f"{c:.2f} " # Add sign if not first term

            # Variable and power
            if power > 1: term_str += f"{var}^{power}"
            elif power == 1: term_str += f"{var}"
            elif power == 0 and (abs(c - 1.0) >= 1e-9 and abs(c + 1.0) >= 1e-9): # Constant term, ensure coeff is shown
                 pass # Coeff already added
            elif power == 0 and (abs(c-1.0) < 1e-9 or abs(c+1.0) < 1e-9): # Coeff is 1 or -1, but it's a constant
                 if abs(c-1.0) < 1e-9: term_str = "+ 1.00" if terms else "1.00"
                 if abs(c+1.0) < 1e-9: term_str = "- 1.00" if terms else "-1.00"

            terms.append(term_str.strip())

        if not terms: return "0"
        # Join terms, ensure first term doesn't have leading "+" if it's positive
        full_str = " ".join(terms)
        if full_str.startswith("+ "): full_str = full_str[2:]
        return full_str.replace("  ", " ").strip()


    def perform_polynomial_operation(self, op_key):
        p1, err1 = self.parse_coeffs_to_poly1d(self.poly1_coeffs_entry.get(), "P1")
        if err1: self._display_poly_result(err1); return

        result_poly = None
        result_scalar = None
        result_roots = None
        op_description = ""

        if op_key in ["add", "sub", "mul", "div"]:
            p2, err2 = self.parse_coeffs_to_poly1d(self.poly2_coeffs_entry.get(), "P2")
            if err2: self._display_poly_result(err2); return

            if op_key == "add": result_poly = p1 + p2; op_description = "P1 + P2"
            elif op_key == "sub": result_poly = p1 - p2; op_description = "P1 - P2"
            elif op_key == "mul": result_poly = p1 * p2; op_description = "P1 * P2"
            elif op_key == "div":
                quotient, remainder = np.polydiv(p1, p2)
                # np.polydiv returns arrays, convert back to poly1d for consistent formatting
                q_poly = np.poly1d(quotient)
                r_poly = np.poly1d(remainder)
                self._display_poly_result(f"تقسیم P1 بر P2:\n  خارج قسمت: {self.format_poly1d_to_string(q_poly)}\n  باقیمانده: {self.format_poly1d_to_string(r_poly)}")
                return
        elif op_key == "roots":
            if p1.order == 0: # Constant polynomial
                self._display_poly_result("چندجمله‌ای ثابت ریشه ندارد (مگر اینکه صفر باشد).")
                return
            result_roots = p1.roots
            op_description = "ریشه‌های P1"
        elif op_key == "deriv":
            result_poly = p1.deriv()
            op_description = "مشتق P1"
        elif op_key == "integ":
            result_poly = p1.integ() # k=0 (constant of integration) by default
            op_description = "انتگرال P1 (ثابت=0)"
        elif op_key == "eval":
            try:
                x_val_str = self.poly_eval_x_entry.get()
                if not x_val_str: self._display_poly_result("خطا: مقدار x برای ارزیابی وارد نشده."); return
                x_val = float(x_val_str)
                result_scalar = p1(x_val)
                op_description = f"مقدار P1 در x = {x_val}"
            except ValueError:
                self._display_poly_result("خطا: مقدار x برای ارزیابی باید عدد باشد."); return

        # Display results
        if result_poly is not None:
            self._display_poly_result(f"نتیجه {op_description}:\n  {self.format_poly1d_to_string(result_poly)}")
        elif result_roots is not None:
            roots_str = ", ".join([f"{r:.4f}" if np.isreal(r) else f"({r.real:.4f}{r.imag:+.4f}j)" for r in result_roots])
            self._display_poly_result(f"نتیجه {op_description}:\n  {roots_str if roots_str else 'ریشه‌ای یافت نشد (ممکن است چندجمله‌ای ثابت غیرصفر باشد)'}")
        elif result_scalar is not None:
            self._display_poly_result(f"نتیجه {op_description}:\n  {result_scalar:.6g}")
        # else: # Should be caught by specific messages or if op_key is invalid
            # self._display_poly_result("عملیات چندجمله‌ای نامعتبر.")


    def open_history_window(self):
        self.history_window = tk.Toplevel(self.master)
        self.history_window.title("تاریخچه محاسبات اصلی")
        self.history_window.geometry("450x500") # Adjusted size

        history_frame = ttk.LabelFrame(self.history_window, text="آخرین محاسبات (جدیدترین در بالا)")
        history_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.history_listbox = tk.Listbox(history_frame, font=('Arial', 10), height=20, selectmode=tk.SINGLE)
        self.history_listbox.pack(side=tk.LEFT, fill="both", expand=True, padx=(0,5))

        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")
        self.history_listbox.config(yscrollcommand=scrollbar.set)

        # Ensure calculation_history and eval_globals are initialized
        if not hasattr(self, 'calculation_history'):
            self.calculation_history = []
        if not hasattr(self, 'eval_globals'): # This check is crucial
            self._initialize_eval_globals()


        self.history_listbox.delete(0, tk.END) # Clear before repopulating
        for item in reversed(self.calculation_history): # Display newest first by iterating reversed
            self.history_listbox.insert(tk.END, item) # Insert at END, effectively reversing again to original order in listbox
                                                    # To show newest at top, insert at 0: self.history_listbox.insert(0, item)
        # Corrected population to show newest at top of listbox
        self.history_listbox.delete(0, tk.END)
        for item in reversed(self.calculation_history):
            self.history_listbox.insert(0, item)


        button_frame = ttk.Frame(self.history_window)
        button_frame.pack(pady=10)

        use_expr_button = ttk.Button(button_frame, text="استفاده از عبارت", command=lambda: self.use_history_item(part="expression"))
        use_expr_button.pack(side=tk.LEFT, padx=5)

        use_result_button = ttk.Button(button_frame, text="استفاده از نتیجه", command=lambda: self.use_history_item(part="result"))
        use_result_button.pack(side=tk.LEFT, padx=5)

        clear_button = ttk.Button(button_frame, text="پاک کردن تاریخچه", command=self.clear_history)
        clear_button.pack(side=tk.LEFT, padx=5)

    def _initialize_eval_globals(self): # Renamed from _update_main_eval_context for clarity of first-time setup
        # This method should be called ONCE at __init__ and then selectively updated by _update_main_eval_context
        # For now, _update_main_eval_context will just call this if eval_globals doesn't exist.
        # A more robust way is to have this truly initialize, and _update_main_eval_context merge user vars.

        # Define the core global context for eval. User variables will be added to this.
        try:
            from scipy import special as sp_special_init # Alias to avoid conflict
            gamma_func_init = sp_special_init.gamma
        except ImportError:
            gamma_func_init = lambda x_gamma: np.nan

        self.base_eval_globals = { # Store base functions separately
            "np": np, "cmath": cmath,
            "sin": np.sin, "cos": np.cos, "tan": np.tan,
            "asin": np.arcsin, "acos": np.arccos, "atan": np.arctan, "atan2": np.arctan2,
            "sinh": np.sinh, "cosh": np.cosh, "tanh": np.tanh,
            "asinh": np.arcsinh, "acosh": np.arccosh, "atanh": np.arctanh,
            "ln": np.log, "log": np.log10, "log2": np.log2,
            "exp": np.exp, "sqrt": np.sqrt, "cbrt": np.cbrt,
            "abs": abs,
            "factorial": lambda n_fact: float(math.factorial(int(n_fact))) if isinstance(n_fact, (int, float)) and n_fact >=0 and float(n_fact).is_integer() else np.nan,
            "gamma": gamma_func_init,
            "pi": np.pi, "e": np.e, "j": 1j,
            "inf": np.inf, "nan": np.nan,
            "deg2rad": np.deg2rad, "rad2deg": np.rad2deg,
            "power": np.power, "hypot": np.hypot,
        }
        self.eval_globals = self.base_eval_globals.copy() # Start with base
        if hasattr(self, 'user_variables'): # Then add user vars if they already exist (e.g. loading from save)
            self.eval_globals.update(self.user_variables)


    def add_to_history(self, expression, result_str):
        if not hasattr(self, 'calculation_history'): # Should be initialized in __init__
            self.calculation_history = []
        # Ensure eval_globals is available for other parts of the code that might need it implicitly
        if not hasattr(self, 'eval_globals'):
            self._initialize_eval_globals()

        history_entry_str = f"{expression} = {result_str}"
        self.calculation_history.append(history_entry_str)
        if len(self.calculation_history) > 50:
            self.calculation_history.pop(0)

        if hasattr(self, 'history_listbox') and self.history_listbox.winfo_exists():
            self.history_listbox.insert(0, history_entry_str)
            if self.history_listbox.size() > 50:
                self.history_listbox.delete(tk.END)

    def use_history_item(self, part="expression"):
        if not hasattr(self, 'history_listbox') or not self.history_listbox.winfo_exists(): return
        try:
            selected_indices = self.history_listbox.curselection()
            if not selected_indices: return
            selected_listbox_index = selected_indices[0]

            # Listbox is displayed newest first (index 0 is newest). calculation_history stores oldest first.
            actual_history_index = len(self.calculation_history) - 1 - selected_listbox_index
            if actual_history_index < 0 or actual_history_index >= len(self.calculation_history): # Bounds check
                return

            history_entry = self.calculation_history[actual_history_index]

            expr_part, result_part = history_entry.split(" = ", 1)

            if part == "expression":
                self.display_var.set(expr_part)
            elif part == "result":
                self.display_var.set(result_part)
            self.history_window.destroy()
        except IndexError:
            pass
        except ValueError:
            messagebox.showerror("خطا", "فرمت تاریخچه نامعتبر است.", parent=self.history_window)


    def clear_history(self):
        if messagebox.askyesno("تایید", "آیا از پاک کردن کل تاریخچه مطمئن هستید؟", parent=self.history_window if hasattr(self, 'history_window') and self.history_window.winfo_exists() else self.master):
            self.calculation_history = []
            if hasattr(self, 'history_listbox') and self.history_listbox.winfo_exists():
                self.history_listbox.delete(0, tk.END)
            # No need for a success messagebox here, the listbox clearing is enough feedback.


    def open_variables_window(self):
        self.vars_window = tk.Toplevel(self.master)
        self.vars_window.title("متغیرهای کاربر")
        self.vars_window.geometry("450x400") # Adjusted size

        if not hasattr(self, 'user_variables'): # Should be initialized in __init__
            self.user_variables = {}
        if not hasattr(self, 'eval_globals'):
            self._initialize_eval_globals()


        # --- Variable Management Frame ---
        var_man_frame = ttk.LabelFrame(self.vars_window, text="مدیریت متغیرها")
        var_man_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(var_man_frame, text="نام متغیر:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.var_name_entry = ttk.Entry(var_man_frame, width=18)
        self.var_name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(var_man_frame, text="مقدار (عبارت عددی):").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.var_value_entry = ttk.Entry(var_man_frame, width=18)
        self.var_value_entry.grid(row=0, column=3, padx=5, pady=5)

        set_var_button = ttk.Button(var_man_frame, text="ذخیره/به‌روزرسانی متغیر", command=self.set_user_variable)
        set_var_button.grid(row=1, column=0, columnspan=2, pady=(10,5), sticky="ew")

        use_var_name_button = ttk.Button(var_man_frame, text="استفاده از نام در نمایشگر اصلی", command=self.use_variable_name_in_display)
        use_var_name_button.grid(row=1, column=2, columnspan=2, pady=(10,5), sticky="ew")


        # --- List of Variables ---
        var_list_frame = ttk.LabelFrame(self.vars_window, text="متغیرهای ذخیره شده (برای ویرایش/حذف دوبار کلیک کنید)")
        var_list_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.vars_listbox = tk.Listbox(var_list_frame, font=('Arial', 10), selectmode=tk.SINGLE)
        self.vars_listbox.pack(side=tk.LEFT, fill="both", expand=True, padx=(0,5))

        vars_scrollbar = ttk.Scrollbar(var_list_frame, orient="vertical", command=self.vars_listbox.yview)
        vars_scrollbar.pack(side=tk.RIGHT, fill="y")
        self.vars_listbox.config(yscrollcommand=vars_scrollbar.set)
        self.vars_listbox.bind("<Double-1>", self.load_var_for_editing) # Load on double-click

        # --- Action buttons for listbox selection ---
        list_action_frame = ttk.Frame(self.vars_window)
        list_action_frame.pack(pady=5)

        load_to_display_button = ttk.Button(list_action_frame, text="بارگذاری مقدار در نمایشگر", command=self.load_selected_var_value_to_display)
        load_to_display_button.pack(side=tk.LEFT, padx=5)

        delete_var_button = ttk.Button(list_action_frame, text="حذف متغیر انتخاب شده", command=self.delete_user_variable)
        delete_var_button.pack(side=tk.LEFT, padx=5)

        self.refresh_variables_listbox()

    def refresh_variables_listbox(self):
        if hasattr(self, 'vars_listbox') and self.vars_listbox.winfo_exists():
            self.vars_listbox.delete(0, tk.END)
            if hasattr(self, 'user_variables'):
                for name in sorted(self.user_variables.keys()): # Display sorted
                    value = self.user_variables[name]
                    self.vars_listbox.insert(tk.END, f"{name} = {value}")

    def set_user_variable(self):
        name = self.var_name_entry.get().strip()
        value_str = self.var_value_entry.get().strip()

        if not name:
            messagebox.showerror("خطا", "نام متغیر نمی‌تواند خالی باشد.", parent=self.vars_window)
            return
        if not name.isidentifier() or keyword.iskeyword(name):
            messagebox.showerror("خطا", "نام متغیر معتبر نیست (باید شناسه پایتون باشد و کلمه کلیدی نباشد).", parent=self.vars_window)
            return

        if not hasattr(self, 'eval_globals'): self._initialize_eval_globals() # Ensure base_eval_globals is set

        # Check against base_eval_globals to prevent overwriting core functions/constants
        if name in self.base_eval_globals:
             if not messagebox.askyesno("هشدار", f"نام '{name}' با یک تابع یا ثابت داخلی همنام است. آیا از بازنویسی آن مطمئن هستید؟ (توصیه نمی‌شود)", parent=self.vars_window):
                 return

        if not value_str:
            messagebox.showerror("خطا", "مقدار متغیر نمی‌تواند خالی باشد.", parent=self.vars_window)
            return

        try:
            # Evaluate the value_str using a context that includes existing user variables AND base functions
            # This allows variables to be defined in terms of other variables or constants like pi
            current_eval_context = self.base_eval_globals.copy()
            current_eval_context.update(self.user_variables) # Add current user vars for evaluation

            value = eval(value_str, current_eval_context, {})

            self.user_variables[name] = value
            self.refresh_variables_listbox()
            self.var_name_entry.delete(0, tk.END)
            self.var_value_entry.delete(0, tk.END)
            self._update_main_eval_context_with_user_vars() # Update the main eval context
        except Exception as e:
            messagebox.showerror("خطا", f"مقدار متغیر نامعتبر است یا در ارزیابی آن خطا رخ داده: {e}", parent=self.vars_window)

    def use_variable_name_in_display(self):
        name_to_use = ""
        if self.var_name_entry.get().strip(): # Prioritize name from entry box
            name_to_use = self.var_name_entry.get().strip()
        elif hasattr(self, 'vars_listbox') and self.vars_listbox.winfo_exists(): # Else, try listbox selection
            try:
                selected_index = self.vars_listbox.curselection()[0]
                var_entry_str = self.vars_listbox.get(selected_index)
                name_to_use = var_entry_str.split(" = ")[0].strip()
            except IndexError:
                messagebox.showwarning("هشدار", "لطفاً نام متغیری را برای استفاده وارد یا انتخاب کنید.", parent=self.vars_window)
                return
        else: # Should not happen if window is open
            messagebox.showwarning("هشدار", "لطفاً نام متغیری را برای استفاده وارد یا انتخاب کنید.", parent=self.vars_window)
            return

        if name_to_use.isidentifier() and not keyword.iskeyword(name_to_use):
            current_display = self.display_var.get()
            self.display_var.set(current_display + name_to_use)
        else:
            messagebox.showerror("خطا", "نام متغیر برای استفاده در عبارت معتبر نیست.", parent=self.vars_window)


    def load_var_for_editing(self, event=None):
        if not hasattr(self, 'vars_listbox') or not self.vars_listbox.winfo_exists(): return
        try:
            selected_index = self.vars_listbox.curselection()[0]
            var_entry_str = self.vars_listbox.get(selected_index)
            name, value_str = var_entry_str.split(" = ", 1)
            self.var_name_entry.delete(0, tk.END)
            self.var_name_entry.insert(0, name.strip())
            self.var_value_entry.delete(0, tk.END)
            self.var_value_entry.insert(0, value_str.strip())
        except IndexError:
            pass
        except ValueError:
            messagebox.showerror("خطا", "فرمت متغیر در لیست نامعتبر است.", parent=self.vars_window)


    def load_selected_var_value_to_display(self):
        if not hasattr(self, 'vars_listbox') or not self.vars_listbox.winfo_exists(): return
        try:
            selected_indices = self.vars_listbox.curselection()
            if not selected_indices:
                messagebox.showwarning("هشدار", "لطفاً یک متغیر از لیست برای بارگذاری مقدار انتخاب کنید.", parent=self.vars_window)
                return
            selected_index = selected_indices[0]
            var_entry_str = self.vars_listbox.get(selected_index)
            _, value_str = var_entry_str.split(" = ", 1)
            self.display_var.set(value_str.strip())
            self.vars_window.destroy()
        except IndexError: # Should be caught by selected_indices check
            pass
        except ValueError:
             messagebox.showerror("خطا", "فرمت متغیر در لیست نامعتبر است.", parent=self.vars_window)


    def delete_user_variable(self):
        if not hasattr(self, 'vars_listbox') or not self.vars_listbox.winfo_exists(): return
        try:
            selected_indices = self.vars_listbox.curselection()
            if not selected_indices:
                 messagebox.showwarning("هشدار", "لطفاً یک متغیر برای حذف انتخاب کنید.", parent=self.vars_window)
                 return
            selected_index = selected_indices[0]
            var_entry_str = self.vars_listbox.get(selected_index)
            name_to_delete = var_entry_str.split(" = ")[0].strip()

            if name_to_delete in self.user_variables:
                if messagebox.askyesno("تایید حذف", f"آیا از حذف متغیر '{name_to_delete}' مطمئن هستید؟", parent=self.vars_window):
                    del self.user_variables[name_to_delete]
                    self.refresh_variables_listbox()
                    self._update_main_eval_context_with_user_vars()
        except IndexError:
            pass
        except ValueError:
            messagebox.showerror("خطا", "فرمت متغیر در لیست برای حذف نامعتبر است.", parent=self.vars_window)


    def _update_main_eval_context_with_user_vars(self):
        if not hasattr(self, 'base_eval_globals'):
            self._initialize_eval_globals()

        self.eval_globals = self.base_eval_globals.copy()
        if hasattr(self, 'user_variables'):
            self.eval_globals.update(self.user_variables)

    def open_prob_dist_window(self):
        self.prob_dist_window = tk.Toplevel(self.master)
        self.prob_dist_window.title("توابع توزیع احتمال (SciPy.stats)")
        self.prob_dist_window.geometry("650x500")

        info_frame = ttk.LabelFrame(self.prob_dist_window, text="انتخاب توزیع و پارامترها")
        info_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(info_frame, text="توزیع:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.dist_name_var = tk.StringVar()

        self.dist_map = {
            "نرمال (Normal)": ("norm", ["میانگین (μ)", "انحراف معیار (σ)"], ["0", "1"], ['loc', 'scale']),
            "دوجمله‌ای (Binomial)": ("binom", ["تعداد آزمایش‌ها (n)", "احتمال موفقیت (p)"], ["10", "0.5"], ['n', 'p']),
            "پواسون (Poisson)": ("poisson", ["نرخ (λ یا mu)"], ["1"], ['mu']),
            "نمایی (Exponential)": ("expon", ["نرخ (λ)", "مکان (loc, اختیاری)"], ["1.0", "0"], ['scale', 'loc']),
            "t-student": ("t", ["درجات آزادی (df)", "مکان (loc, اختیاری)", "مقیاس (scale, اختیاری)"], ["10", "0", "1"], ['df', 'loc', 'scale']),
            "کای-دو (Chi-squared χ²)": ("chi2", ["درجات آزادی (df)", "مکان (loc, اختیاری)", "مقیاس (scale, اختیاری)"], ["5", "0", "1"], ['df', 'loc', 'scale']),
            "F (فیشر)": ("f", ["df صورت (dfn)", "df مخرج (dfd)", "مکان (loc, اختیاری)", "مقیاس (scale, اختیاری)"], ["5", "10", "0", "1"], ['dfn', 'dfd', 'loc', 'scale'])
        }
        dist_display_names = list(self.dist_map.keys())
        self.dist_menu = ttk.OptionMenu(info_frame, self.dist_name_var, dist_display_names[0], *dist_display_names, command=self.update_dist_params_ui)
        self.dist_menu.grid(row=0, column=1, columnspan=3, padx=5, pady=5, sticky="ew")
        info_frame.grid_columnconfigure(1, weight=1)

        self.dist_params_frame = ttk.Frame(info_frame)
        self.dist_params_frame.grid(row=1, column=0, columnspan=4, pady=10, sticky="ew")
        self.dist_param_entries = {}

        calc_type_frame = ttk.LabelFrame(self.prob_dist_window, text="نوع محاسبه و مقدار ورودی")
        calc_type_frame.pack(padx=10, pady=5, fill="x")

        ttk.Label(calc_type_frame, text="نوع محاسبه:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.dist_func_type_var = tk.StringVar(value="pdf")
        pdf_radio = ttk.Radiobutton(calc_type_frame, text="PDF/PMF", variable=self.dist_func_type_var, value="pdf")
        pdf_radio.grid(row=0, column=1, padx=5, pady=2, sticky="w")
        cdf_radio = ttk.Radiobutton(calc_type_frame, text="CDF", variable=self.dist_func_type_var, value="cdf")
        cdf_radio.grid(row=0, column=2, padx=5, pady=2, sticky="w")
        ppf_radio = ttk.Radiobutton(calc_type_frame, text="PPF (چندک)", variable=self.dist_func_type_var, value="ppf")
        ppf_radio.grid(row=0, column=3, padx=5, pady=2, sticky="w")

        ttk.Label(calc_type_frame, text="مقدار x (یا k یا q برای PPF [0,1]):").grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        self.dist_x_entry = ttk.Entry(calc_type_frame, width=15)
        self.dist_x_entry.grid(row=1, column=2, columnspan=2, padx=5, pady=5, sticky="ew")
        self.dist_x_entry.insert(0, "0.5")

        calc_button = ttk.Button(calc_type_frame, text="محاسبه", command=self.calculate_dist_function_value)
        calc_button.grid(row=2, column=0, columnspan=4, pady=10)

        result_frame = ttk.LabelFrame(self.prob_dist_window, text="نتیجه")
        result_frame.pack(padx=10, pady=10, fill="both", expand=True)
        self.dist_result_text = tk.Text(result_frame, height=8, width=70, state='disabled', font=('Arial', 11))
        self.dist_result_text.pack(fill="both", expand=True, padx=5, pady=5)

        if dist_display_names: # Ensure list is not empty
            self.update_dist_params_ui(dist_display_names[0])
        else: # Fallback if dist_map is empty for some reason
             self._display_dist_result("خطا: هیچ توزیعی تعریف نشده است.")


    def update_dist_params_ui(self, selected_dist_display_name):
        for widget in self.dist_params_frame.winfo_children():
            widget.destroy()
        self.dist_param_entries.clear()

        dist_scipy_name, param_display_list, param_defaults, param_internal_names = self.dist_map.get(selected_dist_display_name, (None, [], [], []))
        if not dist_scipy_name: return

        for i, (p_disp_name, p_default) in enumerate(zip(param_display_list, param_defaults)):
            ttk.Label(self.dist_params_frame, text=f"{p_disp_name}:").grid(row=i, column=0, padx=5, pady=3, sticky="w")
            entry = ttk.Entry(self.dist_params_frame, width=12)
            entry.grid(row=i, column=1, padx=5, pady=3, sticky="ew")
            if p_default: entry.insert(0, p_default)
            self.dist_param_entries[param_internal_names[i]] = entry

        self.dist_params_frame.grid_columnconfigure(1, weight=1)
        self._display_dist_result("پارامترهای توزیع را تنظیم و نوع محاسبه را انتخاب کنید.", clear=True)


    def _display_dist_result(self, message, clear=True):
        if not hasattr(self, 'dist_result_text') or not self.dist_result_text.winfo_exists(): return
        self.dist_result_text.config(state='normal')
        if clear: self.dist_result_text.delete('1.0', tk.END)
        self.dist_result_text.insert(tk.END, message + "\n")
        self.dist_result_text.config(state='disabled')

    def calculate_dist_function_value(self):
        from scipy import stats

        selected_dist_display_name = self.dist_name_var.get()
        dist_scipy_name, _, _, param_internal_names = self.dist_map.get(selected_dist_display_name, (None, [], [], []))

        if not dist_scipy_name:
            self._display_dist_result("خطا: توزیع انتخاب نشده یا نامعتبر است.")
            return

        func_type = self.dist_func_type_var.get()

        try:
            x_q_val_str = self.dist_x_entry.get()
            if not x_q_val_str:
                self._display_dist_result(f"خطا: مقدار x (یا k یا q برای {func_type.upper()}) را وارد کنید.")
                return
            x_q_val = float(x_q_val_str)

            if func_type == "ppf" and not (0 <= x_q_val <= 1):
                 self._display_dist_result("خطا: برای PPF، مقدار ورودی (q) باید یک احتمال بین 0 و 1 باشد.")
                 return

            scipy_params = {}
            for internal_name in param_internal_names: # Iterate using internal names to fetch from dict
                entry_widget = self.dist_param_entries.get(internal_name)
                if entry_widget:
                    val_str = entry_widget.get().strip()
                    if val_str:
                        if dist_scipy_name == "binom" and internal_name == "n":
                            scipy_params[internal_name] = int(float(val_str))
                        elif dist_scipy_name in ["poisson", "binom"] and internal_name in ['mu', 'p'] and func_type != 'ppf': # x_q_val is k for discrete
                            pass # x_q_val will be converted to int later for these
                        else:
                            scipy_params[internal_name] = float(val_str)

            # Parameter validation
            if dist_scipy_name == "norm" and scipy_params.get('scale', 1) <= 0:
                self._display_dist_result("خطا: انحراف معیار (scale) برای توزیع نرمال باید مثبت باشد."); return
            if dist_scipy_name == "binom":
                if not (0 <= scipy_params.get('p', 0.5) <= 1): self._display_dist_result("خطا: احتمال (p) برای دوجمله‌ای باید بین 0 و 1 باشد."); return
                if scipy_params.get('n', 0) < 0: self._display_dist_result("خطا: تعداد آزمایش‌ها (n) برای دوجمله‌ای باید غیرمنفی باشد."); return
                if func_type != "ppf": x_q_val = int(round(x_q_val)) # k must be integer
            if dist_scipy_name == "poisson":
                if scipy_params.get('mu', 1) < 0: self._display_dist_result("خطا: نرخ (mu) برای پواسون باید غیرمنفی باشد."); return
                if func_type != "ppf": x_q_val = int(round(x_q_val)) # k must be integer
            if dist_scipy_name == "expon":
                # scale = 1/lambda. If user provides lambda, convert to scale.
                # Assuming the entry "نرخ (λ)" corresponds to 'scale' after 1/lambda transformation.
                # If the 'scale' param is directly taken from entry, it must be > 0.
                if 'scale' in scipy_params and scipy_params['scale'] <= 0:
                     self._display_dist_result("خطا: مقیاس (scale = 1/λ) برای توزیع نمایی باید مثبت باشد."); return
            if dist_scipy_name in ["t", "chi2", "f"]:
                if 'df' in scipy_params and scipy_params['df'] <= 0: self._display_dist_result("خطا: درجات آزادی (df) باید مثبت باشد."); return
                if 'dfn' in scipy_params and scipy_params['dfn'] <= 0: self._display_dist_result("خطا: dfn باید مثبت باشد."); return
                if 'dfd' in scipy_params and scipy_params['dfd'] <= 0: self._display_dist_result("خطا: dfd باید مثبت باشد."); return

            dist_instance = getattr(stats, dist_scipy_name)(**scipy_params)

            result_val = None
            func_name_display = func_type.upper()
            if func_type == "pdf":
                result_val = dist_instance.pmf(x_q_val) if dist_scipy_name in ["binom", "poisson"] else dist_instance.pdf(x_q_val)
                func_name_display = "PMF" if dist_scipy_name in ["binom", "poisson"] else "PDF"
            elif func_type == "cdf":
                result_val = dist_instance.cdf(x_q_val)
            elif func_type == "ppf":
                result_val = dist_instance.ppf(x_q_val)

            param_str_parts = [f"{k}={v}" for k,v in scipy_params.items()]
            self._display_dist_result(f"نتیجه {func_name_display} برای {selected_dist_display_name} در {x_q_val} (با پارامترهای: {', '.join(param_str_parts)}):\nمقدار = {result_val:.7g}")

        except ImportError:
            self._display_dist_result("خطا: کتابخانه SciPy (scipy.stats) برای این محاسبه مورد نیاز است.")
        except ValueError as ve:
            self._display_dist_result(f"خطای مقدار ورودی یا پارامتر: {ve}")
        except KeyError as ke:
            self._display_dist_result(f"خطا: پارامتر '{ke}' برای توزیع یا محاسبه یافت نشد/نامعتبر است.")
        except Exception as e:
            self._display_dist_result(f"خطای کلی: {e}")


    def open_settings_window(self):
        self.settings_window = tk.Toplevel(self.master)
        self.settings_window.title("تنظیمات ماشین حساب")
        self.settings_window.geometry("450x250") # Adjusted size

        # --- Settings Frame ---
        settings_frame = ttk.LabelFrame(self.settings_window, text="تنظیمات عمومی")
        settings_frame.pack(padx=10, pady=10, fill="x", expand=True)

        # Decimal Precision Setting
        ttk.Label(settings_frame, text="ارقام اعشار نمایشگر اصلی:").grid(row=0, column=0, padx=5, pady=10, sticky="w")
        if not hasattr(self, 'decimal_precision'):
            self.decimal_precision = 10
        self.precision_var = tk.IntVar(value=self.decimal_precision)
        # Using a Combobox for precision for better UX than Spinbox for discrete choices.
        self.precision_combo = ttk.Combobox(settings_frame, textvariable=self.precision_var,
                                            values=list(range(2, 16)), width=5, state="readonly")
        self.precision_combo.grid(row=0, column=1, padx=5, pady=10, sticky="w")
        self.precision_combo.set(self.decimal_precision) # Set current value


        # Angle Mode Setting
        ttk.Label(settings_frame, text="حالت زاویه (sin, cos, tan):").grid(row=1, column=0, padx=5, pady=10, sticky="w")
        if not hasattr(self, 'angle_mode'):
            self.angle_mode = "radians"
        self.angle_mode_var = tk.StringVar(value=self.angle_mode)

        angle_options_frame = ttk.Frame(settings_frame)
        angle_options_frame.grid(row=1, column=1, sticky="w")
        deg_radio = ttk.Radiobutton(angle_options_frame, text="درجه (Deg)", variable=self.angle_mode_var, value="degrees")
        deg_radio.pack(side=tk.LEFT, padx=(0,10))
        rad_radio = ttk.Radiobutton(angle_options_frame, text="رادیان (Rad)", variable=self.angle_mode_var, value="radians")
        rad_radio.pack(side=tk.LEFT)

        # Apply Button within the settings window
        apply_button = ttk.Button(settings_frame, text="اعمال تنظیمات", command=self.apply_settings_from_window)
        apply_button.grid(row=3, column=0, columnspan=2, pady=20)

        # Load current settings into UI elements when window opens
        self.precision_var.set(self.decimal_precision)
        self.angle_mode_var.set(self.angle_mode)


    def apply_settings_from_window(self):
        # Decimal Precision
        try:
            new_precision = self.precision_var.get() # Comes from IntVar, should be int
            if 2 <= new_precision <= 15:
                self.decimal_precision = new_precision
            else: # Should not happen with Combobox if values are restricted, but good for Spinbox
                messagebox.showwarning("مقدار نامعتبر", "تعداد ارقام اعشار باید بین ۲ و ۱۵ باشد.", parent=self.settings_window)
                self.precision_var.set(self.decimal_precision)
        except tk.TclError:
             messagebox.showerror("خطا", "مقدار نامعتبر برای ارقام اعشار.", parent=self.settings_window)
             self.precision_var.set(self.decimal_precision)

        # Angle Mode
        new_angle_mode = self.angle_mode_var.get()
        self.angle_mode = new_angle_mode

        # Update how basic calculator buttons for sin, cos, tan behave
        # This will modify the expression string that gets evaluated

        # The eval_globals already contains np.sin, np.cos, np.tan which expect radians.
        # If we want the direct sin, cos, tan buttons to respect degree mode,
        # the on_button_click method needs to be aware of self.angle_mode when 'sin', 'cos', 'tan' chars are processed.
        # For example, if char is 'sin' and mode is 'degrees', it should insert "sind(" or "sin(deg2rad("
        # This is now handled in the modified on_button_click.

        messagebox.showinfo("اعمال شد", "تنظیمات با موفقیت اعمال شدند.", parent=self.settings_window)
        if hasattr(self, 'settings_window') and self.settings_window.winfo_exists():
            self.settings_window.destroy()

    # Modified on_button_click to handle angle_mode for direct sin, cos, tan button presses
    def on_button_click(self, char): # Overriding the original on_button_click
        current_text = self.display_var.get()

        if char == 'C':
            self.display_var.set(current_text[:-1])
        elif char == 'AC':
            self.display_var.set("")
        elif char == '=':
            expression_to_eval = current_text # The expression is already built
            # The eval context (self.eval_globals) handles np.sin etc as radian-based
            try:
                if not hasattr(self, 'eval_globals'): self._initialize_eval_globals()

                # Important: The expression string from display_var might already contain deg2rad()
                # if user used sin/cos/tan buttons in degree mode.
                # So, direct eval should work as intended.
                result = eval(expression_to_eval, self.eval_globals, {})

                # Use self.decimal_precision for rounding the final result
                precision = getattr(self, 'decimal_precision', 10) # Default to 10 if not set
                if isinstance(result, (int, float)):
                    result_str = f"{result:.{precision}g}" # Use g for general format, respecting precision
                elif isinstance(result, complex):
                    real_part = f"{result.real:.{precision}g}"
                    imag_part = f"{result.imag:.{precision}g}"
                    result_str = f"{real_part}{'+' if result.imag >= 0 else ''}{imag_part}j"
                else:
                    result_str = str(result) # For non-numeric results (e.g. arrays from some operations)

                self.display_var.set(result_str)
                self.add_to_history(expression_to_eval, result_str)
            except Exception as e:
                self.display_var.set("Error")
                self.add_to_history(expression_to_eval, "Error: " + str(e))

        # Handle direct button presses for sin, cos, tan considering angle_mode
        elif char in ['sin', 'cos', 'tan']:
            # Ensure angle_mode is initialized
            current_angle_mode = getattr(self, 'angle_mode', 'radians') # Default to radians
            if current_angle_mode == 'degrees':
                # Wrap the function call with deg2rad for evaluation
                # e.g., if display is "30" and user presses "sin", text becomes "sin(deg2rad(30"
                # if display is "my_var" and user presses "sin", text becomes "sin(deg2rad(my_var"
                # This assumes that the argument to sin/cos/tan will be processed by deg2rad
                self.display_var.set(current_text + f"{char}(deg2rad(")
            else: # Radians mode
                self.display_var.set(current_text + f"{char}(")

        # Handle other function buttons that need an opening parenthesis
        elif char in ['ln', 'log', 'sqrt', 'asin', 'acos', 'atan', 'sinh', 'cosh', 'tanh', 'asinh', 'acosh', 'atanh', 'gamma', 'factorial']:
            self.display_var.set(current_text + f"{char}(")

        # Handle operators and numbers
        else:
            if char in ['/', '*', '-', '+', '^'] and (not current_text or current_text[-1] in ['/', '*', '-', '+', '^']):
                if char == '-' and (not current_text or current_text[-1] in ['/', '*', '(', '^']):
                     self.display_var.set(current_text + str(char))
            elif char == '.' and '.' in self._get_last_number(current_text):
                pass
            else:
                self.display_var.set(current_text + str(char))


if __name__ == '__main__':
    # Ensure cmath and other necessary modules are imported at the top level of the script
    import math, cmath, keyword, sys # Added sys for checking modules
    from tkinter import messagebox # For popups in variable management
    try:
        from scipy import special
    except ImportError:
        print("SciPy.special not installed, some special functions (like gamma) might not be available or will return NaN.")
        class DummySpecialModule:
            def __init__(self):
                self.gamma = lambda x_gamma: np.nan
        special = DummySpecialModule()


    root = tk.Tk()
    app = EngineeringCalculator(root)
    root.mainloop()
