from classes.item import Item

class Formatter:
    def _get_widths() -> list:
        """Define widths for formatting the displayed warehouse data."""
        return [10,8,6,10]

    def _format_header(columns: list) -> str:
        widths = Formatter._get_widths()
        row = [f"{column:{widths[i]}}" for i, column in enumerate(columns)]
        row2 = [f"{'-'*widths[i]}" for i in range(len(columns))]
        return "\t".join(row) + "\n" + "\t".join(row2)

    def _format_row(item: Item, columns: list) -> str:
        widths = Formatter._get_widths()
        row = []
        for i, column in enumerate(columns):
            if column == "name" or column == "unit":
                align = '<'
            else:
                align = '>'
            row.append(f"{getattr(item, column):{align}{widths[i]}}")
        return "\t".join(row)