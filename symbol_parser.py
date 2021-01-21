# coding=UTF-8

# Define a few special charecters in a dictonary
symbol_dictionary = {'&amp;': '\\&',
                     'π': '\\pi ',
                     'α': '\\alpha ',
                     '': '\\epsilon ',
                     'φ': '\\phi ',
                     'θ': '\\theta ',
                     'ρ': '\\rho ',
                     'µ': '\\mu ',
                     '∆': '\\Delta ',
                     'ε': '\\varepsilon ',
                     'ϕ': '\\Phi ',
                     # For now, don't use these chars in mathmode...
                     #'æ': '\\textit{æ} ',
                     #'Æ': '\\textit{Æ} ',
                     #'ø': '\\textit{ø} ',
                     #'Ø': '\\textit{Ø} ',
                     #'å': '\\textit{å} ',
                     #'Å': '\\textit{Å} ',
                     '⇕': '\\Updownarrow ',
                     '⇔': '\\Leftrightarrow ',
                     'ω': '\\omega',
                     'Ω': '\\Omega',
                     '&': '\\&',
                     'γ' : '\\gamma',
                     'τ' : '\\tau',
                     'σ' : '\\sigma'}  # ToDo: Add more of these...


def symbol_parser(str_with_symbols, mathmode):
    """Parses symbols into LaTeX symbols

    :param str_with_symbols: A string which is the given symbol that needs to be checked
    :return: Formatted LaTeX symbol or what was given
    """
    if mathmode: # return the "pure" string
        for unicode_symbol in symbol_dictionary:  # Check entire dictionary
            try:  # Try to replace the given symbol
                str_with_symbols = str_with_symbols.replace(unicode_symbol, symbol_dictionary[unicode_symbol])
            except unicode_symbolError:  # If it fails, just skip it
                pass

        return str_with_symbols  # Return the parsed symbol

    elif mathmode is False: # return the parsed string with $ $ to create a LaTeX math mode region
        for unicode_symbol in symbol_dictionary:  # Check entire dictionary
            try:  # Try to replace the given symbol
                str_with_symbols = str_with_symbols.replace(unicode_symbol, "$" + symbol_dictionary[unicode_symbol] + "$")
            except unicode_symbolError:  # If it fails, just skip it
                pass

        return str_with_symbols  # Return the parsed symbol
