from decimal import Decimal, InvalidOperation, getcontext

class DecimalValidationError(Exception):
    """Raised when Decimal conversion fails due to invalid input or type."""
    pass

def _decimal(value):
    try:
        return Decimal(value, context=getcontext())
    except (InvalidOperation, TypeError) as e:
        # Wrap both exceptions into one
        raise DecimalValidationError(f"Invalid decimal input: {value}") from e

def numeric_input(prompt, default: Decimal|None = None) -> Decimal:
    while True:
        inp = input(prompt)
        if inp.strip() == "":
            if default is not None:
                # Enter - no change, return default value
                return default
            else:
                continue
        try:
            valid = _decimal(inp)
        except DecimalValidationError as e:
            print(f"Error:", e)
        else:
            return valid