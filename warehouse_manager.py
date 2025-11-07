import argparse
import csv
import os
import shlex
import sys

items = [{
            'Name': "Milk",
            'Quantity': 120,
            'Unit': "L",
            'Unit Price': 2.3
        },
         {
            'Name': "Sugar",
            'Quantity': 1000,
            'Unit': "kg",
            'Unit Price': 3.0 
        },
        {
            'Name': "Flour",
            'Quantity': 12000,
            'Unit': "kg",
            'Unit Price': 1.2 
        },
        {
            'Name': "Coffee",
            'Quantity': 2500,
            'Unit': "kg",
            'Unit Price': 40.0 
        }
]

sold_items = []

columns = ["Name", "Quantity", "Unit", "Unit Price"]

registered_commands = {}

def register(command):
    def decorator(func):
        registered_commands[command] = func
        return func
    return decorator

def _get_widths():
    return [10,8,6,10]

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

def _get_costs():
    return sum([item['Quantity'] * item['Unit Price'] for item in items])

def _get_income():
    return sum([item['Quantity'] * item['Unit Price'] for item in sold_items])

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

def _import_items_from_csv(path="magazyn.csv"):
    if not os.path.exists(path):
        print(f"File '{path}' not found. Warehouse file not loaded.")
        return
    with open(path, "r", newline='') as f:
        reader = csv.DictReader(f, fieldnames=columns)
        reader.__next__()  # Skip header
        items.clear()
        for row in reader:
            for key in ['Quantity', 'Unit Price']:
                row[key] = float(row[key])
            items.append(row)
    print(f'Successfully loaded warehouse data from "{path}"')

def _import_sales_from_csv(path="sprzedaż.csv"):
    if not os.path.exists(path):
        print(f"File '{path}' not found. Sales file not loaded.")
        return
    with open(path, "r", newline='') as f:
        reader = csv.DictReader(f, fieldnames=columns)
        reader.__next__()  # Skip header
        sold_items.clear()
        for row in reader:
            for key in ['Quantity', 'Unit Price']:
                row[key] = float(row[key])
            sold_items.append(row)
    print(f'Successfully loaded sales data from "{path}"')


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
    quantity = int(input("Item quantity: "))
    unit = input("Item unit of measure (L, kg, pcs, etc.): ")
    unit_price = float(input("Item price in PLN: "))

    items.append({
        'Name': name,
        'Quantity': quantity,
        'Unit': unit,
        'Unit Price': unit_price
        })


@register("sell")
def sell_item():
    name = input("Item name: ")
    quantity = int(input("Quantity to sell: "))
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
def show_revenue():
    inc = _get_income()
    cost = _get_costs()
    print("Revenue breakdown (PLN):")
    print("Income: ", inc)
    print("Costs: ", cost)
    print("-"*10)
    print(f"Revenue: {inc - cost} PLN")


@register("save")
def export_warehouse_to_csv():
    _export_items_to_csv()
    _export_sales_to_csv()


@register("load")
def import_warehouse_from_csv(items=None, sales=None):
    """
    Load only the files explicitly specified.
    - items: path to warehouse CSV or None
    - sales: path to sales CSV or None
    If both are None, nothing is loaded (and a short message is printed).
    """
    if items is None and sales is None:
        print("No files specified to load. Use: load items=PATH and/or sales=PATH")
        return

    if items is not None:
        _import_items_from_csv(items)
    if sales is not None:
        _import_sales_from_csv(sales)

def parse_arguments():
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
    except TypeError:
        print("Incorrect arguments for command.")



if __name__ == "__main__":
    args = parse_arguments()
    import_warehouse_from_csv(items=args.warehouse_file, sales=args.sales_file)
    
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