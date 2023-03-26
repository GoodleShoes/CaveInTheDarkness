import tcod


def handle_string_input(prompt):
    """Displays a prompt and allows the user to enter a string of text."""
    input_console = tcod.console.Console(width=80, height=1)
    input_console.set_default_foreground(0, tcod.white)

    input_string = ""
    while True:
        tcod.console_clear(input_console)
        input_console.print_(0, 0, prompt + ": " + input_string)
        tcod.console_flush()
        key = tcod.console_wait_for_keypress(True)
        if key.vk == tcod.KEY_ENTER:
            return input_string
        elif key.vk == tcod.KEY_BACKSPACE:
            input_string = input_string[:-1]
        elif key.c:
            input_string += chr(key.c)
