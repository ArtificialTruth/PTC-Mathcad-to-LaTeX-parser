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
                     'æ': '\\textit{æ}',
                     'Æ': '\\textit{Æ}',
                     'ø': '\\textit{ø}',
                     'Ø': '\\textit{Ø}',
                     'å': '\\textit{å}',
                     'Å': '\\textit{Å}',
                     '⇕': '\\Updownarrow',
                     '⇔': '\\Leftrightarrow'}  # ToDo: Add more of these...



def symbol_parser(symbol):
    """Parses symbols into LaTeX symbols

    :param symbol: A string which is the given symbol that needs to be checked
    :return: Formatted LaTeX symbol or what was given
    """

    for key in symbol_dictionary:  # Check entire dictionary
        try:  # Try to replace the given symbol
            symbol = symbol.replace(key, symbol_dictionary[key])
        except KeyError:  # If it fails, just skip it
            pass

    return symbol  # Return the parsed symbol
