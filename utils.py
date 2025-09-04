import ast
import streamlit as st
import json
from io import StringIO


def safe_execute(code: str, allowed_words: set, mode=None, extra_variables=None):
    """
    Executes or evaluates Python code safely by ensuring it only contains whitelisted words.

    Parameters:
    code (str): The Python code to execute or evaluate as a string.
    allowed_words (set): A set of allowed words for execution or evaluation.
    mode (str): The execution mode, either 'exec' for exec() or 'eval' for eval().
                Defaults to 'exec'.
    extra_variables (dict): Additional variables to include in the execution environment.

    Returns:
    Result of eval() if mode is 'eval', otherwise None.

    Raises:
    ValueError: If the code contains disallowed words or invalid syntax.
    """
    if mode not in {"exec", "eval"}:
        raise ValueError("Mode must be 'exec' or 'eval'")

    try:
        # Parse the code into an abstract syntax tree (AST)
        parsed_code = ast.parse(code, mode="exec" if mode == "exec" else "eval")
    except SyntaxError as e:
        raise ValueError(f"Invalid syntax: {e}")

    # Collect all names (identifiers) in the code
    class NameCollector(ast.NodeVisitor):
        def __init__(self):
            self.names = set()

        def visit_Name(self, node):
            self.names.add(node.id)
            self.generic_visit(node)

    collector = NameCollector()
    collector.visit(parsed_code)

    # Check if all names are in the whitelist
    disallowed_words = collector.names - allowed_words
    if disallowed_words:
        st.session_state.simulation_error = True
        raise ValueError(f"Disallowed words found: {disallowed_words}")

    # Prepare the restricted execution environment
    # Allow specific built-ins like print(), min() and max()
    safe_globals = {"__builtins__": {"print": print}, "min": min, "max": max}

    # Add extra variables (such as locals)
    if extra_variables:
        safe_globals.update(extra_variables)

    # Execute or evaluate the code
    if mode == "exec":
        exec(code, safe_globals)
    elif mode == "eval":
        return eval(code, safe_globals)


def parse_json_strategy(strategy_text):
    """
    Parse and validate JSON strategy from text.

    Parameters:
    strategy_text (str): JSON string to parse

    Returns:
    tuple: (parsed_strategy, is_valid, error)
        - parsed_strategy: The parsed JSON object or None if invalid
        - is_valid: Boolean indicating if JSON is valid
        - error: Error object or None if valid
    """
    try:
        # Use StringIO to create a temporary file-like object
        strategy_io = StringIO(strategy_text)
        # Load JSON from the StringIO object
        parsed_strategy = json.load(strategy_io)
        return parsed_strategy, True, None
    except json.JSONDecodeError as e:
        return None, False, e


def check_energy_balance(net_energy_balance):
    """
    Check if energy balance is maintained (all values should be zero).

    Parameters:
    net_energy_balance (Series): Series containing energy balance values

    Returns:
    tuple: (status_type, message)
        - status_type: "success" or "error"
        - message: Description of the result
    """
    # Find all non-zero values
    non_zero_indices = [i for i, value in enumerate(net_energy_balance) if abs(value) > 1e-10]

    if len(non_zero_indices) == 0:
        return ("success", "Energy balance check passed: All values are 0")
    elif len(non_zero_indices) == 1:
        return ("error", f"Warning: Energy imbalance at index {non_zero_indices[0]}")
    else:
        return ("error", "Warning: Energy imbalance, more than one value ≠ 0")


def calculate_electricity_price(electricity_wholesale_price, apply_additional_costs, taxes_and_fees, grid_fees):
    """
    Calculate final electricity price with taxes and fees.

    Parameters:
    electricity_wholesale_price (float): Base electricity price
    apply_additional_costs (bool): Whether to apply additional costs
    taxes_and_fees (float): Taxes and fees in ct/kWh
    grid_fees (float): Grid fees in ct/kWh

    Returns:
    float: Calculated electricity price
    """
    if apply_additional_costs:
        return (electricity_wholesale_price + taxes_and_fees / 100 + grid_fees / 100) * 1.19
    else:
        return electricity_wholesale_price
