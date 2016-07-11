# coding=UTF-8

# Define a few special characters in a dictionary
symbol_dictionary = {'π': '\\pi',
                     'α': '\\alpha',
                     '': '\\epsilon',
                     'φ': '\\phi',
                     'θ': '\\theta',
                     'ρ': '\\rho',
                     'µ': '\\mu',
                     '∆': '\\Delta',
                     'ε': '\\varepsilon',
                     'ϕ': '\\Phi'}


def symbol_parser(symbol):
    """Parses symbols into LaTeX symbols

    :param symbol: A string which is the given symbol that needs to be checked
    :return: Formatted LaTeX symbol or what was given
    """
    if symbol in symbol_dictionary:  # Check if the symbol is in our dictionary
        return symbol_dictionary[symbol]  # Return the corresponding symbol from the dictionary
    else:
        return symbol  # Else, just return what was sent
