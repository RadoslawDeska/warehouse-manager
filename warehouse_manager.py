import argparse
import decimal
from decimal import Decimal
import os
import shlex
import sys
from typing import Callable

from classes.item import Item
from classes.format import Formatter
from classes.decimals import numeric_input
from classes.io import IO_CSV, IO_JSON


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

quantize_exp = Decimal('0.01')
rounding = decimal.ROUND_HALF_UP

registered_commands : dict[str, Callable[[str], list[Item]]] = {}
registered_loaders : dict[str, Callable[[str], list[Item]]] = {}

def register(command):
    """Decorator to register a function as a user-supplied command."""
    """Decorator to register a function as a user-supplied command."""
    def decorator(func):
        registered_commands[command] = func
        return func
    return decorator

def register_loader(extension):
    """Decorator to register a function based on one or more file extensions."""
    def decorator(func):
        if isinstance(extension, (list, tuple, set)):
            for ext in extension:
                registered_loaders[ext] = func
        else:
            registered_loaders[extension] = func
        return func
    return decorator

# Global commands
@register("help")
def show_help(*args, **kwargs):
    print("Available commands:")
    for command in registered_commands.keys():
        if command in ["quit", "exit"]:
            continue
        print(f" - {command}")
        if command == "load":
            print("""
    usage:
    - load items=PATH_TO_ITEMS
    - load sales=PATH_TO_SALES
    - load items=PATH_TO_ITEMS sales=PATH_TO_SALES
""".strip("\n"))
    print("Type 'exit' or 'quit' to quit the program.")

@register("exit")
def exit_command(*args, **kwargs):
    """Exit the program (same as typing Ctrl+C)."""
    sys.exit(0)

@register("quit")
def quit_command(*args, **kwargs):
    """Alternate name for exit."""
    sys.exit(0)


# Loaders
@register_loader("csv")
def csv_loader(path: str, /, fieldnames: list[str], *, data=None, mode=None) -> tuple[bool, list[Item] | None]:
    if mode == "r":
        return IO_CSV._read_csv(path, fieldnames)
    elif mode == "w":
        if data is None:
            data = []
        return IO_CSV._write_csv(path, fieldnames, data), None
    else:
        print("Wrong operation mode. Accepts only (r)ead or (w)rite.")
        return False, None

@register_loader("json")
def json_loader(path: str, /, fieldnames=None, *, data=None, mode=None) -> tuple[bool, list[Item] | None]:
    if mode == "r":
        return IO_JSON._read_json(path)
    elif mode == "w":
        if data is None:
            data = []
        return IO_JSON._write_json(path, data), None
    else:
        print("Wrong operation mode. Accepts only (r)ead or (w)rite.")
        return False, None


# MAIN CLASS
class Warehouse:
    """Class representing manager of warehouse items.
    
    Specifies methods for adding, selling, displaying items and importing/exporting the data.
    """

    def __init__(self):
        self.items : list[Item] = []
        self.sold_items : list[Item] = []

    # Define helper functions
    def get_names(self, lst: list[Item]) -> list[str]:
        """Return list of items' names in lowercase."""
        return [item.name.lower() for item in lst]

    
    # Define item management methods
    @register("add")
    def add_item(self):
        print("Adding to warehouse...")
        name = input("Item name: ")
        if name.lower() in self.get_names(self.items):
            print(f"Item '{name}' already exists. You are about to update all fields. Use Enter to keep existing values.")
            existing_item = next(item for item in self.items if item.name.lower() == name.lower())
            quantity = numeric_input(f"Item quantity [{existing_item.quantity}]: ",
                                    default=existing_item.quantity)
            # unit = input(f"Item unit of measure (L, kg, pcs, etc.) [{existing_item.unit}]: ", 
            #                         default=existing_item.unit)
            unit_price = numeric_input(f"Item price in PLN [{existing_item.unit_price}]: ",
                                    default=existing_item.unit_price)
            # Update existing item
            existing_item.quantity = quantity
            existing_item.unit_price = unit_price

            print(f"Successfully updated {existing_item!r}")
        else:
            quantity = numeric_input("Item quantity: ")
            unit = input("Item unit of measure (L, kg, pcs, etc.): ")
            unit_price = numeric_input("Item price in PLN: ")
            
            self.items.append(Item(name=name, quantity=quantity, unit=unit, unit_price=unit_price))

            print(f"Successfully added {self.items[-1]!r}")
    
    @register("sell")
    def sell_item(self):
        name = input("Item name: ")
        quantity_to_sell = numeric_input("Quantity to sell: ")
        for item in self.items:
            if item.name.lower() == name.lower():
                if item.quantity < quantity_to_sell:
                    print(f"Not enough {name} in stock! Nothing sold.")
                    return
                item.quantity -= quantity_to_sell

                if name.lower() not in self.get_names(self.sold_items):
                    self.sold_items.append(Item(
                        name=item.name,
                        quantity=quantity_to_sell,  # Important
                        unit=item.unit,
                        unit_price=item.unit_price))
                else:
                    for item in self.sold_items:
                        if item.name.lower() == name.lower():
                            item.quantity += quantity_to_sell
                            break
                print(f"Successfully sold {quantity_to_sell} {item.unit} of {name}")
                return
        print(f"{name} not found in warehouse! Nothing sold.")


    # Define arithmetic methods
    def _get_costs(self) -> Decimal:
        return sum([item.quantity * item.unit_price for item in self.items], Decimal(0))

    def _get_income(self) -> Decimal:
        return sum([item.quantity * item.unit_price for item in self.sold_items], Decimal(0))

    
    # Define reporting methods
    @register("show")
    def get_items(self):
        header = Formatter._format_header(COLUMNS)
        print(header)

        for item in self.items:
            row = Formatter._format_row(item, COLUMNS)
            print(row)

    @register("show_revenue")
    def show_revenue(self):
        inc = self._get_income()
        cost = self._get_costs()
        revenue = Decimal(inc - cost).quantize(quantize_exp,rounding=rounding)
        print("Revenue breakdown (PLN):")
        print("Income: ", inc.quantize(quantize_exp,rounding=rounding))
        print("Costs: ", cost.quantize(quantize_exp,rounding=rounding))
        print("-"*10)
        print(f"Revenue: {revenue} PLN")


    # Define import/export methods
    @staticmethod
    def _export(path, data: list[Item], export_as="csv", fieldnames=[]):
        loader = registered_loaders.get(export_as)
        if loader:
            return loader(path, fieldnames, mode='w')
        if export_as == "csv":
            return IO_CSV._write_csv(path, data, fieldnames)

    
    @staticmethod
    def _import(path, import_as="csv", fieldnames=[]) -> list[Item]:
        loader = registered_loaders.get(import_as)
        if loader:
            ok, lst = loader(path, fieldnames, mode='r')
            return lst if ok else []
        # Fallback to CSV reader
        if import_as == "csv":
            ok, lst = IO_CSV._read_csv(path, fieldnames)
            return lst if ok else []
    
    @staticmethod
    def detect_ext(path: str) -> str:
        _, ext = os.path.splitext(path)
        ext = ext.lower().lstrip('.')
        # Prefer any registered loader matching the extension
        if ext in registered_loaders:
            return ext
        # Default to csv for common or unknown/empty extensions
        if ext == 'csv' or ext == '':
            return 'csv'
        print(f"Unknown file type '{ext}' for {path}. Defaulting to 'csv'.")
        return 'csv'
    
    @register("load")
    def import_warehouse(self, items_file=None, sales_file=None):
        """
        Load only the files explicitly specified.
        - items: path to warehouse CSV or None
        - sales: path to sales CSV or None
        If both are None, nothing is loaded (and a short message is printed).
        """
        if not any([items_file, sales_file]):
            print("No files specified to load. For usage use `help` command.")
            return
        
        if items_file:
            import_as = self.detect_ext(items_file)
            self.items = self._import(items_file, import_as=import_as, fieldnames=COLUMNS)
        if sales_file:
            import_as = self.detect_ext(sales_file)
            self.sold_items = self._import(sales_file, import_as=import_as, fieldnames=COLUMNS)
            
    @register("save")
    def export_warehouse(self):
        pass



def parse_arguments():
    """Parse command-line arguments passed to the script on startup."""
    """Parse command-line arguments passed to the script on startup."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--warehouse",
                        type=str,
                        dest="warehouse_file",
                        default=os.path.join(BASE_DIR, "magazyn.csv"),
                        required=False)
    parser.add_argument("-s", "--sales",
                        type=str,
                        dest="sales_file",
                        default=os.path.join(BASE_DIR, "sprzedaż.csv"),
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

def dispatch_command(warehouse: Warehouse, cmd_name, args, kwargs):
    """Lookup and invoke a registered command; print a helpful message on error."""
    if cmd_name is None:
        return  # empty user input
    command = registered_commands.get(cmd_name)
    if command is None:
        print("Unknown command. Type 'help' to see available commands.")
        return
    try:
        command(warehouse, *args, **kwargs)
    except TypeError as e:
        print("Arguments received:", args)
        print("Kwargs received", kwargs)
        print("Incorrect arguments for command.")
        print(e)
        print(e)


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    COLUMNS = list(Item.model_fields.keys())  # get fields from Item model
    
    args = parse_arguments()
    
    w = Warehouse()
    w.import_warehouse(items_file=args.warehouse_file, sales_file=args.sales_file)
    
    # Main loop
    while True:  # exit managed by registered commands
        inp = input("What would you like to do? ")
        if not inp:
            continue
        
        try:
            cmd_name, args, kwargs = parse_command_input(inp)
        except ValueError as e:
            print(e)
            continue
        
        dispatch_command(w, cmd_name, args, kwargs)