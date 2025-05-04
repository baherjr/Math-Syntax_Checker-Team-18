import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk


class MathSyntaxChecker:
    def __init__(self):
        self.stack = []
        self.valid_operators = {'+', '-', '*', '/', '^'}
        self.opening_brackets = {'(', '[', '{'}
        self.closing_brackets = {')', ']', '}'}
        self.bracket_pairs = {')': '(', ']': '[', '}': '{'}
        self.valid_functions = {'sin', 'cos', 'tan', 'log', 'ln', 'sqrt', 'abs', 'exp', 'floor', 'ceil', 'round'}

    def is_number(self, token):
        try:
            float(token)
            return True
        except ValueError:
            return False

    def is_variable(self, token):
        if not token[0].isalpha() and token[0] != '_':
            return False
        for char in token[1:]:
            if not (char.isalnum() or char == '_'):
                return False
        if token in self.valid_functions:
            return False
        return True

    def is_function(self, token):
        return token in self.valid_functions

    def tokenize(self, expression):
        tokens = []
        i = 0
        while i < len(expression):
            char = expression[i]
            if char.isspace():
                i += 1
                continue

            # Handle negative numbers: check if this is a minus sign that could be for a negative number
            if char == '-' and (i == 0 or expression[i - 1] in self.valid_operators or
                                expression[i - 1] in self.opening_brackets or
                                (i > 0 and tokens and tokens[-1] in self.valid_operators) or
                                (i > 0 and tokens and tokens[-1] in self.opening_brackets)):

                # Look ahead to see if this is part of a double negative
                if i + 1 < len(expression) and expression[i + 1] == '-':
                    # This is the first of a double negative
                    tokens.append(char)
                    i += 1
                    continue

                # This is potentially a negative number
                j = i + 1
                # Skip spaces after the minus sign
                while j < len(expression) and expression[j].isspace():
                    j += 1

                if j < len(expression) and (expression[j].isdigit() or expression[j] == '.'):
                    # It's a negative number - capture the minus sign with the number
                    decimal_point_seen = False
                    start = i  # Start from the minus sign
                    i = j  # Move to the first digit/decimal point

                    while i < len(expression) and (expression[i].isdigit() or expression[i] == '.'):
                        if expression[i] == '.':
                            if decimal_point_seen:
                                return None, f"Error: Invalid number format at position {i}"
                            decimal_point_seen = True
                        i += 1
                    tokens.append(expression[start:i])
                    continue
                else:
                    # It's just a minus operator
                    tokens.append(char)
                    i += 1
                    continue

            if char.isdigit() or (char == '.' and i + 1 < len(expression) and expression[i + 1].isdigit()):
                j = i
                decimal_point_seen = False
                while j < len(expression) and (expression[j].isdigit() or expression[j] == '.'):
                    if expression[j] == '.':
                        if decimal_point_seen:
                            return None, f"Error: Invalid number format at position {j}"
                        decimal_point_seen = True
                    j += 1
                tokens.append(expression[i:j])
                i = j
                continue
            if char.isalpha() or char == '_':
                j = i
                while j < len(expression) and (expression[j].isalnum() or expression[j] == '_'):
                    j += 1
                tokens.append(expression[i:j])
                i = j
                continue
            if char in self.valid_operators or char in self.opening_brackets or char in self.closing_brackets:
                tokens.append(char)
                i += 1
                continue
            return None, f"Error: Invalid character '{char}' at position {i}"
        return tokens, None

    def check_syntax(self, expression):
        if not expression.strip():
            return False, "Error: Empty expression"

        tokens, error = self.tokenize(expression)
        if error:
            return False, error

        if not tokens:
            return False, "Error: No valid tokens found in expression"

        # Check if expression starts with an operator (except minus which could indicate negative number)
        if tokens[0] in self.valid_operators and tokens[0] != '-':
            return False, f"Error: Expression cannot start with the operator '{tokens[0]}'"

        # Special handling for expressions that start with a minus
        # A standalone minus at the beginning should be followed by a number, variable, function or opening bracket
        if tokens[0] == '-':
            if len(tokens) < 2:
                return False, "Error: Expression cannot consist of only a minus sign"

            allowed_after_unary_minus = ['number', 'variable', 'function', 'open_bracket']
            next_token = tokens[1]
            next_token_type = None

            if self.is_number(next_token):
                next_token_type = 'number'
            elif self.is_function(next_token):
                next_token_type = 'function'
            elif self.is_variable(next_token):
                next_token_type = 'variable'
            elif next_token in self.opening_brackets:
                next_token_type = 'open_bracket'

            if next_token_type not in allowed_after_unary_minus:
                return False, f"Error: Invalid token '{next_token}' after unary minus"

        # The rest of the check_syntax method remains unchanged
        # ...
        self.stack = []
        prev_token_type = None
        i = 0
        while i < len(tokens):
            token = tokens[i]

            # Determine token type
            if self.is_number(token):
                token_type = 'number'
            elif self.is_function(token):
                token_type = 'function'
            elif self.is_variable(token):
                token_type = 'variable'
            elif token in self.valid_operators:
                token_type = 'operator'
            elif token in self.opening_brackets:
                token_type = 'open_bracket'
            elif token in self.closing_brackets:
                token_type = 'close_bracket'
            else:
                return False, f"Error: Unrecognized token '{token}' at position {i}"

            # Additional validation for first token
            if i == 0 and token_type == 'operator' and token != '-':
                return False, f"Error: Expression cannot start with operator '{token}'"

            # Check for strict function syntax (must be followed by an opening bracket)
            if prev_token_type == 'function':
                if token_type != 'open_bracket':
                    return False, f"Error: Function '{tokens[i - 1]}' must be followed by an opening bracket"

            # Handle implicit multiplication
            if prev_token_type in ['number', 'variable', 'close_bracket'] and token_type in ['open_bracket', 'function',
                                                                                             'variable']:
                # Valid implicit multiplication
                pass

            # Check for valid token sequences
            if token_type == 'operator':
                if i == len(tokens) - 1:
                    return False, f"Error: Expression cannot end with an operator"

                if i + 1 < len(tokens):
                    next_token = tokens[i + 1]
                    # After an operator, we can have: number, variable, function, opening bracket
                    # or another minus sign (for negative numbers)
                    if not (self.is_number(next_token) or self.is_variable(next_token) or
                            self.is_function(next_token) or next_token in self.opening_brackets or
                            (next_token == '-' and token in self.valid_operators)):
                        return False, f"Error: Expected number, variable, function, or opening bracket after operator at position {i + 1}"
            elif prev_token_type in ['number', 'variable'] and token_type not in ['operator', 'close_bracket',
                                                                                  'open_bracket', 'function',
                                                                                  'variable']:
                return False, f"Error: Expected operator, closing bracket, or implicit multiplication after {prev_token_type} at position {i}"
            elif prev_token_type == 'open_bracket' and token_type not in ['number', 'variable', 'function',
                                                                          'open_bracket',
                                                                          'operator']:  # Allow operator for negative numbers after bracket
                return False, f"Error: Expected number, variable, function, or opening bracket after opening bracket at position {i}"
            elif prev_token_type == 'close_bracket' and token_type not in ['operator', 'close_bracket', 'open_bracket',
                                                                           'function', 'variable']:
                return False, f"Error: Expected operator, closing bracket, or implicit multiplication after closing bracket at position {i}"

            # Handle brackets
            if token_type == 'open_bracket':
                self.stack.append(token)
            elif token_type == 'close_bracket':
                if not self.stack:
                    return False, f"Error: Unmatched closing bracket '{token}' at position {i}"
                last_open = self.stack.pop()
                if last_open != self.bracket_pairs[token]:
                    return False, f"Error: Mismatched bracket pair '{last_open}' and '{token}' at position {i}"

            prev_token_type = token_type
            i += 1

        # Check for unmatched opening brackets
        if self.stack:
            return False, f"Error: Unmatched opening brackets: {', '.join(self.stack)}"

        return True, "Expression syntax is valid"


# GUI Implementation
def check_expression():
    expression = entry.get()
    checker = MathSyntaxChecker()
    valid, message = checker.check_syntax(expression)

    if valid:
        status_text = "✅ Valid: " + message
        text_color = "green"
    else:
        status_text = "❌ Invalid: " + message
        text_color = "red"

    result_label.configure(
        text=status_text,
        text_color=text_color,
        wraplength=450
    )


# Add example expressions
def insert_example(example):
    entry.delete(0, tk.END)
    entry.insert(0, example)
    # Auto-check the syntax when an example is inserted
    check_expression()


# CustomTkinter GUI Setup
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("Math Syntax Checker")
root.geometry("700x550")
root.resizable(True, True)  # Allow resizing for better adaptability

# Main frame with proper padding
main_frame = ctk.CTkFrame(root)
main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

# Input section with better spacing
input_frame = ctk.CTkFrame(main_frame)
input_frame.pack(fill=tk.X, padx=10, pady=(10, 15))

input_label = ctk.CTkLabel(input_frame, text="Enter Expression:", font=("Helvetica", 12, "bold"))
input_label.pack(side=tk.LEFT, padx=(10, 5), pady=10)

entry = ctk.CTkEntry(input_frame, width=450, height=35, placeholder_text="Type your expression here...")
entry.pack(side=tk.LEFT, padx=(5, 10), pady=10, fill=tk.X, expand=True)

# Check button with better positioning
check_button = ctk.CTkButton(
    main_frame,
    text="Check Syntax",
    command=check_expression,
    cursor="hand2",
    height=35,
    font=("Helvetica", 12, "bold")
)
check_button.pack(pady=(0, 15))

# Examples section with improved layout
examples_label_frame = ctk.CTkFrame(main_frame)
examples_label_frame.pack(fill=tk.X, padx=10, pady=(5, 0))

examples_label = ctk.CTkLabel(
    examples_label_frame,
    text="Valid Examples:",
    font=("Helvetica", 12, "bold")
)
examples_label.pack(anchor=tk.W, padx=10, pady=5)

# Valid Examples Section with grid layout for consistency
examples_frame = ctk.CTkFrame(main_frame)
examples_frame.pack(fill=tk.X, padx=10, pady=(0, 15))

# Create a consistent grid for examples
for i in range(2):
    examples_frame.grid_rowconfigure(i, weight=1)
for i in range(3):
    examples_frame.grid_columnconfigure(i, weight=1)

# Add examples with consistent sizing
example_buttons = [
    {"text": "2 + 3 * 4", "example": "2 + 3 * 4", "row": 0, "column": 0},
    {"text": "sin(x) + cos(y)", "example": "sin(x) + cos(y)", "row": 0, "column": 1},
    {"text": "(a + b) * (c - d)", "example": "(a + b) * (c - d)", "row": 0, "column": 2},
    {"text": "sqrt(x^2 + y^2)", "example": "sqrt(x^2 + y^2)", "row": 1, "column": 0},
    {"text": "2x + 3(y - z)", "example": "2x + 3(y - z)", "row": 1, "column": 1},
    {"text": "log(10) + exp(-x^2) / (1 + x^2)", "example": "log(10) + exp(-x^2) / (1 + x^2)", "row": 1, "column": 2}
]

for btn in example_buttons:
    ctk.CTkButton(
        examples_frame,
        text=btn["text"],
        command=lambda ex=btn["example"]: insert_example(ex),
        width=200,
        height=35
    ).grid(row=btn["row"], column=btn["column"], padx=5, pady=5, sticky="ew")

# Invalid examples section with improved layout
invalid_label_frame = ctk.CTkFrame(main_frame)
invalid_label_frame.pack(fill=tk.X, padx=10, pady=(5, 0))

invalid_label = ctk.CTkLabel(
    invalid_label_frame,
    text="Invalid Examples:",
    text_color="red",
    font=("Helvetica", 12, "bold")
)
invalid_label.pack(anchor=tk.W, padx=10, pady=5)

# Invalid Examples Section with consistent grid layout
invalid_frame = ctk.CTkFrame(main_frame)
invalid_frame.pack(fill=tk.X, padx=10, pady=(0, 15))

# Create a consistent grid for invalid examples
for i in range(2):
    invalid_frame.grid_rowconfigure(i, weight=1)
for i in range(3):
    invalid_frame.grid_columnconfigure(i, weight=1)

# Add invalid examples with consistent sizing
invalid_buttons = [
    {"text": "2 +", "example": "2 +", "row": 0, "column": 0},
    {"text": "* 2 + 3", "example": "* 2 + 3", "row": 0, "column": 1},
    {"text": "2..5", "example": "2..5", "row": 0, "column": 2},
    {"text": "(2 + 3", "example": "(2 + 3", "row": 1, "column": 0},
    {"text": "sin 2", "example": "sin 2", "row": 1, "column": 1},
    {"text": "sqrt(x^2 + y^2", "example": "sqrt(x^2 + y^2", "row": 1, "column": 2}
]

for btn in invalid_buttons:
    ctk.CTkButton(
        invalid_frame,
        text=btn["text"],
        command=lambda ex=btn["example"]: insert_example(ex),
        width=200,
        height=35,
        fg_color="#b53b3b"
    ).grid(row=btn["row"], column=btn["column"], padx=5, pady=5, sticky="ew")

# Result label with better padding and frame to make it stand out
result_frame = ctk.CTkFrame(main_frame, fg_color=("#E3E3E3", "#2B2B2B"))  # Light/dark mode colors
result_frame.pack(fill=tk.X, padx=10, pady=(0, 10), ipady=5)

result_label = ctk.CTkLabel(
    result_frame,
    text="Enter an expression and click 'Check Syntax' or select an example",
    height=60,
    font=("Helvetica", 12),
    wraplength=600
)
result_label.pack(padx=15, pady=15, fill=tk.X)

# Run GUI
root.mainloop()