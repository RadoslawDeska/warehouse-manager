

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


@register("help")
def show_help():
    print("Available commands:")
    for command in registered_commands.keys():
        print(f" - {command}")
    print("Type 'exit' to quit the program.")


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

if __name__ == "__main__":
    while True:
        inp = input("What would you like to do? ")
        if inp.lower() == "exit":
            break
        
        command = registered_commands.get(inp.lower(), None)
        if command is None:
            print("Unknown command. Type 'help' to see available commands.")
        else:
            command()