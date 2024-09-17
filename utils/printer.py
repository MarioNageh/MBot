from palettepy import init, color_style_foreground
from utils.time import get_current_time_hms

init()
light_blue_hex = '#ADD8E6'
yellow_hex = '#FFFF00'
red_hex = '#FF7F7F'
light_green_hex = '#90EE90'
info_hex = '#FFA500'
light_blue = color_style_foreground(light_blue_hex)
yellow = color_style_foreground(yellow_hex)
red = color_style_foreground(red_hex)
green = color_style_foreground(light_green_hex)
cyan = color_style_foreground('#00FFFF')
info = color_style_foreground(info_hex)


class PrinterData:
    def __init__(self, user_name: str = "", user_id: str = ""):
        self.printer_count = 0
        self.user_name = user_name
        self.user_id = user_id


class TerminalPrinter:
    def __init__(self, printer_data: PrinterData = None):
        self.printer_data = printer_data

    def get_message_header(self):
        self.printer_data.printer_count += 1
        current_time = get_current_time_hms()
        header_body = light_blue(
            f"[{self.printer_data.user_id}][{self.printer_data.user_name}][{self.printer_data.printer_count:08d}]")
        time_body = yellow(f"[{current_time}]")
        return f"{header_body}{time_body}:"

    @staticmethod
    def sprint_success(message: str):
        print(f"{green(message)}")

    def print(self, transformation: str):
        print(f"{self.get_message_header()} {transformation}")

    def get_fail_format(self, message: str):
        return f"{self.get_message_header()} {red(message)}"

    def print_fail(self, message: str):
        self.print(f"{red(message)}")

    def print_success(self, message: str):
        self.print(f"{green(message)}")

    def print_info(self, message: str):
        self.print(f"{info(message)}")

    def print_debug(self, message: str):
        self.print(f"{cyan(message)}")

    def print_received_packet(self, message: str):
        self.print(f"{light_blue(message)}")
