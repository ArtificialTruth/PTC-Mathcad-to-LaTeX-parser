# coding=UTF-8

# Define a few special charecters in a dictonary
symbol_dictionary = {'π': '\\pi',
                     'α': '\\alpha',
                     '': '\\epsilon',
                     'φ': '\\phi',
                     'θ': '\\theta',
                     'ρ': '\\rho',
                     'µ': '\\mu',
                     '∆': '\\Delta',
                     'ε': '\\varepsilon',
                     'ϕ': '\\Phi',
                     'æ': '\\ae',
                     'Æ': '\\AE',
                     'ø': '\\oe',
                     'Ø': '\\OE',
                     'å': '\\aa',
                     'Å': '\\AA'}



def symbol_parser(symbol):
    """Parses symbols into LaTeX symbols

    :param symbol: A string which is the given symbol that needs to be checked
    :return: Formatted LaTeX symbol or what was given
    """
    # ToDo: Write for-loop that goes through every charecter in the string (symbol)
    if symbol in symbol_dictionary:  # Check if the symbol is in our dictonary
        return symbol_dictionary[symbol]  # Return the corresponding symbol from the dictonary
    else:
        return symbol  # Else, just return what was sent
