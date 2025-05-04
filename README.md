# Mathematical Expression Syntax Checker

A Python application that validates the syntax of mathematical expressions using a Deterministic Pushdown Automaton (DPDA) approach.

## Features

- **Real-time syntax validation** of mathematical expressions
- **Detailed error messages** with specific error locations
- **Support for common mathematical functions** (sin, cos, tan, log, sqrt, etc.)
- **Bracket matching** for parentheses, square brackets, and curly braces
- **Implicit multiplication** recognition (e.g., 2x is valid)
- **User-friendly GUI** with example expressions

## Installation

### Prerequisites

- Python 3.6 or higher
- CustomTkinter library

## How to Use

1. **Enter a mathematical expression** in the input field
2. **Click "Check Syntax"** or press Enter
3. View the results in the output area below:
   - ✅ Green indicates valid syntax
   - ❌ Red indicates errors (with specific error messages)

### Example Valid Expressions

- `2 + 3 * 4`
- `sin(x) + cos(y)`
- `(a + b) * (c - d)`
- `sqrt(x^2 + y^2)`
- `2x + 3(y - z)`

### Example Invalid Expressions

- `2 +` (incomplete expression)
- `* 2 + 3` (starts with operator)
- `(2 + 3` (unmatched bracket)
- `sin 2` (function without parentheses)

## Technical Details

The application implements a Deterministic Pushdown Automaton (DPDA) to validate mathematical expressions, with:

- Tokenization to identify numbers, variables, operators, functions, and brackets
- Stack-based parsing for bracket matching and expression structure validation
- Comprehensive syntax rules for operator placement and function usage

## License

[MIT License](LICENSE)

## Acknowledgments

- Based on formal language theory and automata concepts
- Built with Python and CustomTkinter for the GUI
