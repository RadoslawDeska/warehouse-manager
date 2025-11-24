import argparse
import csv
import decimal
from decimal import Decimal
import os
import shlex
import sys

context = decimal.getcontext()
quantize_exp = Decimal('0.01')
rounding = decimal.ROUND_HALF_UP

items = []
sold_items = []

columns = ["Name", "Quantity", "Unit", "Unit Price"]

registered_commands = {}

def register(command):
    """Decorator to register a function as a user-supplied command."""
    def decorator(func):
        registered_commands[command] = func
        return func
    return decorator

def _get_widths() -> list:
    """Define widths for formatting the displayed warehouse data."""
    return [10,8,6,10]

def _convert_to_decimal(item: dict) -> dict:
    """Convert numeric fields to Decimal type for accurate calculations."""
    item['Quantity'] = Decimal(item['Quantity'], context=context)
    item['Unit Price'] = Decimal(item['Unit Price'], context=context)
    return item

def _format_row(item: dict) -> str:
    widths = _get_widths()
    row = []
    for i, column in enumerate(columns):
        if column == "Name" or column == "Unit":
            align = '<'
        else:
            align = '>'
        row.append(f"{item[column]:{align}{widths[i]}}")
    return "\t".join(row)

def _format_header(columns: list) -> str:
    widths = _get_widths()
    row = [f"{column:{widths[i]}}" for i, column in enumerate(columns)]
    row2 = [f"{'-'*widths[i]}" for i in range(len(columns))]
    return "\t".join(row) + "\n" + "\t".join(row2)

def _get_costs() -> Decimal:
    return sum([item['Quantity'] * item['Unit Price'] for item in items], Decimal(0))

def _get_income() -> Decimal:
    return sum([item['Quantity'] * item['Unit Price'] for item in sold_items], Decimal(0))

def _export_items_to_csv():
    with open("magazyn.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(items)
    print("Successfully exported data to magazyn.csv")

def _export_sales_to_csv():
    with open("sprzedaż.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(sold_items)
    print("Successfully exported data to sprzedaż.csv")

def _generate_list(reader: csv.DictReader):
    lst = []
    for row in reader:
        # Format numeric fields
        row = _convert_to_decimal(row)
        lst.append(row)
    return lst

def _read_csv(path) -> list:
    """Read CSV file and return the list of items where numbers are formatted as Decimal type."""
    # Read the CSV file
    with open(path, "r", newline='') as f:
        reader = csv.DictReader(f, fieldnames=columns)
        reader.__next__()  # Skip header
        formatted_list = _generate_list(reader)
    return formatted_list

def _import_items(path="magazyn.csv"):
    if not os.path.exists(path):
        print(f"File '{path}' not found. Warehouse file not loaded.")
        return
    lst = _read_csv(path)
    print(f'Successfully loaded warehouse data from "{path}"')
    return lst

def _import_sales(path="sprzedaż.csv"):
    if not os.path.exists(path):
        print(f"File '{path}' not found. Sales file not loaded.")
        return
    lst = _read_csv(path)
    print(f'Successfully loaded sales data from "{path}"')
    return lst

@register("help")
def show_help():
    print("Available commands:")
    for command in registered_commands.keys():
        print(f" - {command}")
    print("Type 'exit' or 'quit' to quit the program.")

@register("exit")
def exit_command():
    """Exit the program (same as typing Ctrl+C)."""
    sys.exit(0)

@register("quit")
def quit_command():
    """Alternate name for exit."""
    sys.exit(0)

@register("show")
def get_items():
    header = _format_header(columns)
    print(header)

    for item in items:
        row = _format_row(item)
        print(row)


@register("add")
def add_item():
    print("Adding to warehouse...")
    name = input("Item name: ")
    quantity = Decimal(input("Item quantity: "), context=context)
    unit = input("Item unit of measure (L, kg, pcs, etc.): ")
    unit_price = Decimal(input("Item price in PLN: "), context=context)

    items.append({
        'Name': name,
        'Quantity': quantity,
        'Unit': unit,
        'Unit Price': unit_price
        })


@register("sell")
def sell_item():
    name = input("Item name: ")
    quantity = Decimal(int(input("Quantity to sell: ")))
    for item in items:
        if item['Name'].lower() == name.lower():
            if item['Quantity'] < quantity:
                print(f"Not enough {name} in stock! Nothing sold.")
                return
            item['Quantity'] -= quantity

            if name.lower() not in \
                [sold_item['Name'].lower() for sold_item in sold_items]:
                sold_items.append({
                    'Name': item['Name'],
                    'Quantity': quantity,
                    'Unit': item['Unit'],
                    'Unit Price': item['Unit Price']
                    })
            else:
                for item in sold_items:
                    if item['Name'].lower() == name.lower():
                        item['Quantity'] += quantity
                        break
            print(f"Successfully sold {quantity} {item['Unit']} of {name}")
            return
    print(f"{name} not found in warehouse! Nothing sold.")


@register("show_revenue")
def show_revenue(args=None, kwargs=None):
    inc = _get_income()
    cost = _get_costs()
    revenue = Decimal(inc - cost).quantize(quantize_exp,rounding=rounding)
    print("Revenue breakdown (PLN):")
    print("Income: ", inc.quantize(quantize_exp,rounding=rounding))
    print("Costs: ", cost.quantize(quantize_exp,rounding=rounding))
    print("-"*10)
    print(f"Revenue: {revenue} PLN")


@register("save")
def export_warehouse_to_csv():
    _export_items_to_csv()
    _export_sales_to_csv()


@register("load")
def import_warehouse_from_csv(items_file=None, sales_file=None):
    """
    Load only the files explicitly specified.
    - items: path to warehouse CSV or None
    - sales: path to sales CSV or None
    If both are None, nothing is loaded (and a short message is printed).
    """
    if items_file is None and sales_file is None:
        print("No files specified to load. Use: load items=PATH and/or sales=PATH")
        return [[],[]]

    to_return = []

    if items_file is not None:
        imported_items = _import_items(items_file)
        to_return.append(imported_items)
    else:
        to_return.append([])
    if sales_file is not None:
        imported_sales = _import_sales(sales_file)
        to_return.append(imported_sales)
    else:
        to_return.append([])
    
    return to_return

def parse_arguments():
    """Parse command-line arguments passed to the script on startup."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--warehouse",
                        type=str,
                        dest="warehouse_file",
                        default="magazyn.csv",
                        required=False)
    parser.add_argument("-s", "--sales",
                        type=str,
                        dest="sales_file",
                        default="sprzedaż.csv",
                        required=False)
    
    return parser.parse_args()

def parse_command_input(inp):
    if inp.strip() == "":
        return None, [], {}
    try:
        parts = shlex.split(inp)
    except ValueError as e:
        raise ValueError(f"Error parsing command: {e}")
    if not parts:
        return None, [], {}
    cmd_name = parts[0].lower()
    # If there are any arguments to the command, collect them
    args = []
    kwargs = {}
    for argument in parts[1:]:
        if '=' in argument:
            k, v = argument.split('=', 1)
            kwargs[k] = v
        else:
            args.append(argument)
    return cmd_name, args, kwargs

def dispatch_command(cmd_name, args, kwargs):
    """Lookup and invoke a registered command; print a helpful message on error."""
    if cmd_name is None:
        return  # empty user input
    command = registered_commands.get(cmd_name)
    if command is None:
        print("Unknown command. Type 'help' to see available commands.")
        return
    try:
        command(*args, **kwargs)
    except TypeError as e:
        print("Arguments received:", args)
        print("Kwargs received", kwargs)
        print("Incorrect arguments for command.")
        print(e)


if __name__ == "__main__":
    args = parse_arguments()
    items, sales = import_warehouse_from_csv(items_file=args.warehouse_file, sales_file=args.sales_file)
    
    # Main loop
    while True:
        inp = input("What would you like to do? ")
        if not inp:
            continue
        if inp.lower() == "exit":
            break
        
        try:
            cmd_name, args, kwargs = parse_command_input(inp)
        except ValueError as e:
            print(e)
            continue
        
        dispatch_command(cmd_name, args, kwargs)