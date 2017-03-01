# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ElemTree  # Import the XML ElementTree module aliased as ET
import io  # Import used for more advanced file writing
import os  # Used for file name handling
import numpy
from symbol_parser import symbol_parser  # Import function which formats special charecters
from tkinter.filedialog import askopenfilename  # Tkinter libs or selecting files in OS file picker
from tkinter import Tk, Frame, Button, Label, StringVar, Entry  # Used for the GUI

class ParseGUI(object):
    """Class used for the handling of the GUI
    The object parameter is the root widget for the Tkinter GUI
    """
    def __init__(self, master):
        """Constructor method

        :param master: A "master" wigdet
        """
        self.mainframe = Frame(master)  # Create a Frame child widget
        self.mainframe.pack()  # Make the widget visible

        self.path = ''  # Define default path

        self.name = Label(self.mainframe, text="Welcome to Mathcad to LaTeX converter")  # Create a static text label
        self.name.pack(side="top")  # Make the widget visible and define location

        self.filename = StringVar()  # Create a dynamic string variable
        self.filename.set("Current selected file: none")  # Set the string value
        self.filename_label = Label(self.mainframe, textvariable=self.filename)  # Create a label with the dynamic var
        self.filename_label.pack()
        self.text_updater = Entry(self.mainframe, textvariable=self.filename)  # Create a Entry widget for auto updates

        self.status = StringVar()  # Used for displaying the status of the file operation
        self.status.set("Status: Not parsed")
        self.status_label = Label(self.mainframe, textvariable=self.status)
        self.status_label.pack()
        self.text_updater2 = Entry(self.mainframe, textvariable=self.status)

        self.parse_file = Button(self.mainframe, text="Parse and save!", command=self.parse_file)  # Button for parsing
        self.parse_file.pack(side="right")

        self.select_file = Button(self.mainframe, text="Select file", command=self.select_file)  # Runs a class method
        self.select_file.pack(side="left")

    def select_file(self):  # Method used for selecting a file
        self.path = askopenfilename()  # Display native os file dialog for choosing a file
        self.filename.set("Current selected file: " + os.path.basename(self.path))  # Change the dynamic variable
        self.status.set("Status: Not parsed")  # Set status

    def parse_file(self):  # Method for parsing the chosen file
        # Make sure a file is selected and it is a Mathcad file before trying to parse it
        if self.filename.get() != 'Current selected file: none' and os.path.splitext(self.path)[1] == '.xmcd':
            MathcadXMLParser(self.path)  # Call the MathcadXMLParser class with the path
            self.status.set("Status: File tried parsed! Look under the folder \ParsedLatexFile !")
        # Display a error message to the user
        else:
            self.status.set("Status: You need to select a .xmcd (Mathcad) file!")


class MathcadXMLParser(object):
    """Class used for reading Mathcad files and writing LaTeX files

    Parses the results from the file reading and saving it
    Takes in a object (the file path)
    """
    def __init__(self, filename):
        """The constructor method

        :param filename: A path to the targeted file
        """
        self.target_file = filename  # Define the filename as a class variable
        self.filename = os.path.basename(self.target_file).replace('.xmcd', '')  # Get the file name, remove extension
        math_tree_ok = True  # As a starting point, the file is ok

        try:  # Try to parse the file into a ElementTree
            self.math_tree = ElemTree.parse(self.target_file).getroot()  # Our full XML as an ElementTree

        except ElemTree.ParseError:  # Run if XML structure is corrupted
            print("Corrupted Mathcad document! Could not parse.")
            math_tree_ok = False  # Make sure rest of file is not tried parsed

        self.ml = "{http://schemas.mathsoft.com/math30}"  # Variable for namespaces as URI, used in prefixes
        self.ws = "{http://schemas.mathsoft.com/worksheet30}"
        self.debug = True  # Toggle debug messages

        if not os.path.exists('ParsedLatexFile'):  # If this folder doesn't exist
            os.makedirs('ParsedLatexFile')  # Create it

        # Open a new tex file for writing. Encoding for Danish chars etc. Save in a folder
        self.tex_file = io.open('ParsedLatexFile/' + self.filename + '.tex', 'w', encoding="utf-8")

        # Standard LaTeX document info as strings
        self.start_latex_doc = "\\documentclass[10pt,a4paper]{report}\n\\usepackage[utf8]{inputenc}\n\\usepackage{a" \
                               "msmath}\n\\usepackage{amsfonts}\n\\usepackage{amssymb}\n\\begin{document}\n\\noindent\n"
        self.end_latex_doc = "\end{document}"

        self.matrix_array = []  # Array to use for multiple values in matrixes

        self.i = 0  # Counter

        if math_tree_ok:  # Only run if file isn't corrupted
            self.main()  # Run main method

    def math_reader(self, elem):
        """Main reader method, used for ElementTree reading.

        Recursive method for efficiency
        :param elem: A ElementTree
        :return: Full LaTeX formatted math expressions
        """
        elem.tag = elem.tag.replace(self.ml, "")  # Only leave operator name left without prefix

        if elem.tag == "apply":  # If current Element's tag is apply
            # We need two cases; One for apply tag which includes a operator, and everything else
            # The first will always be the operator, if there's one
            if self.debug:  # Only prints debug messages if debug = True
                print("Apply tag found")

            # Either there's a operator
            if bool(elem[0]) is False and elem[0].text is None:  # Checks if
                if self.debug:  # Only prints debug messages if debug = True
                    print("Apply tag includes a operator")

                if len(elem) == 3:  # Either there's 3 parts (normal mathemathical expression)
                    print("elem[0].tag", elem[0].tag)
                    print("elem[1]", elem[1])
                    print("operator part")
                    val1 = self.math_reader(elem[1])  # Call this method again with 2nd child again to get first value
                    val2 = self.math_reader(elem[2])  # Call this method again with 3rd child again to get second value
                    # Return the formatted result (by calling math_formatter), to the original caller of this method
                    return self.math_formatter(elem[0].tag, val1, val2)  # Sends the operator and the two values

                elif len(elem) == 2:  # Used for other operators where there's only "two" parts
                    print("no operator part")
                    val1 = self.math_reader(elem[1])  # Call this method again to get the first result
                    return self.math_formatter(elem[0].tag, val1)  # Get first child's tag which is the operator

            # Or there's no operator - this is the case for ex cos(x) - currently hardcoded for "parens"
            # ToDo: Make a more general way of handling apply tags?
            elif bool(elem[0]) or elem[0].text is not None:
                val1 = self.math_reader(elem[0])  # Call this method again with 2nd child again to get first value
                val2 = self.math_reader(elem[1])  # Call this method again with 3rd child again to get second value
                return self.math_formatter("nothing", val1, val2)

        elif elem.tag == "parens":  # Handle parenteses
            val1 = self.math_reader(elem[0])
            return self.math_formatter("parens", val1)  # Only 1 value between parenteses

        elif elem.tag == "provenance":  # Interesting Mathcad structure handled here
            return self.math_reader(elem[len(elem)-1])  # Simply call this method again with the last child element

        elif elem.tag == "id":  # Current tag is pure text
            if self.debug:
                print("Text found:", elem.text)
            return symbol_parser(elem.text)  # Call external function with text

        elif elem.tag == "result" or elem.tag == "real":  # Current tag is used for pure numbers
            if self.debug:
                print("Number found:", elem.text)
            return elem.text  # Simply return the value as string

        # Current tag is some kind of equal sign
        elif elem.tag == "eval" or elem.tag == "equal" or elem.tag == "define":
            if self.debug:
                print("A type of equal expression found.")
            # Eval works like normal equal operator
            return self.math_formatter("equal", self.math_reader(elem[0]), self.math_reader(elem[1]))

        elif elem.tag == "vectorize":  # Current tag is a vector notation
            if self.debug:
                print("Vector found.")
            return self.math_formatter("vectorize", self.math_reader(elem[0]))

        elif elem.tag == "matrix":  # Currrent tag is a matrix
            if self.debug:
                print("Matrix found.")

            # Run through every entity in the matrix, and add it to a list
            for entity in elem:
                # Convert every entity in to string, for supporting advanced expressions in matrix
                self.matrix_array.append(str(self.math_reader(entity)))  # Recursive, to handling everything :D

            numpy_matrix_array = numpy.array(self.matrix_array)  # Convert from list to a numpy array for manipulation
            array_dimensions = (int(elem.attrib["rows"]), int(elem.attrib["cols"]))  # Grap the ints from the attribute
            numpy_matrix_array = numpy.reshape(numpy_matrix_array, array_dimensions)  # Transform from flat array
            if array_dimensions[0] > 1 and array_dimensions[1] > 1:  # Only transpose if there's more than 1 col or row
                numpy_matrix_array = numpy.transpose(numpy_matrix_array)  # Flip array around to fit LaTeX structure

            self.matrix_array = []  # Reset matrix array
            return self.math_formatter("matrix", numpy_matrix_array, array_dimensions)  # Send array and the dimensons
            
        elif elem.tag == "placeholder":  # Current tag is just a placeholder
            if self.debug:
                print("Empty placeholder found.")
            return " "  # Return space

        else:  # For unsupported tags
            print("Error, non-supported tag found at region", self.i)  # Print the problematic region number
            print("Current Elem.tag:", elem.tag)  # Debug message

    def text_reader(self, elem):
        """Pure text formatter method

        :param elem: The ElementTree that contains text
        :return: Formatted text with escape chars
        """
        text = ""  # Set default values
        i = 1

        if self.debug:
            print("Type: Text region.")

        for paragraph in elem:  # For each paragraph, print a new line
            i += 1  # Counter to handle for-loop
            if i <= len(elem):  # For every paragraph that isn't the last
                text += paragraph.text + "\\\\" + "\n"  # LaTeX formatting
            else:  # For the last paragraph (no newline)
                text += paragraph.text

        return text

    def math_formatter(self, operator, x, y=None):  # Define the value of y
        """LaTeX math formatter metod

        :param operator: A math operator or similar
        :param x: The first part of the expression
        :param y: The last part of the expression - Default value: None
        :return: Math expression formatted in LaTeX format
        """
        operator = operator.replace(self.ml, "")  # Remove prefix from operator

        if y is not None:  # Is y given?
            if self.debug:
                print("y given")

            if operator == "plus":  # Format into LaTeX expressions
                return x + " + " + y

            elif operator == "minus":
                return x + " - " + y

            elif operator == "mult":
                return x + " \cdot " + y

            elif operator == "div":
                return "\\frac{" + x + "}{" + y + "}"  # Double dash due to escape charecters in Python

            elif operator == "eval" or operator == "equal" or operator == "define":
                return x + " = " + y

            elif operator == "pow":
                return x + "^" + "{" + y + "}"

            elif operator == "nthRoot":
                return "\\sqrt[" + x + "]{" + y + "}"

            elif operator == "lessThan":
                return x + " < " + y

            elif operator == "greaterThan":
                return x + " > " + y

            elif operator == "lessOrEqual":
                return x + " \\leq " + y

            elif operator == "greaterOrEqual":
                return x + " \\geq " + y

            elif operator == "and":
                return x + " \\land " + y

            elif operator == "or":
                return x + " \\lor " + y

            elif operator == "matrix":
                string = "\\begin{pmatrix}\n"
                i2 = 1
                # Rows and cols in the matrix, taken from the y tuple
                rows = y[0]
                cols = y[1]

                # We have 2 counters; one to keep track of current row (i), one for col (i2)
                for i in range(0, rows):
                    for entity in x[i, :]:
                        if i2 == cols:  # RNS checkmate
                            string = string + entity
                        else:
                            string = string + entity + " & "
                        i2 += 1
                    i2 = 1
                    string += "\\\\\n"

                string += "\\end{pmatrix}"

                return string

            elif operator == "nothing":
                return x + y
                
        else:  # Else, there is only 1 value
            if self.debug:
                print("No y given")

            if operator == "parens":
                return "\\left(" + x + "\\right)"

            elif operator == "sqrt":
                return "\\sqrt{" + x + "}"

            elif operator == "absval":
                return "\\left|" + x + "\\right|"

            elif operator == "neg":
                return "-" + x

            elif operator == "vectorize":
                return "\\vec{" + x + "}"

    def main(self):
        """Method for controlling file writing

        Writes the final results to the new .tex file
        """
        self.tex_file.write(self.start_latex_doc)  # Write start of LaTeX document

        for child in self.math_tree[3]:  # Run for each region containing math or text
            self.i += 1  # Update counter
            print("\nTried to parse region", self.i)  # Line separator for ouput

            try:  # Try to parse
                if child[0].tag == self.ws + "math":  # Math region
                    if self.debug:
                        print("Type: Math region.")
                    # Write result of the region by calling fuction which sends the current element
                    self.tex_file.write("\\begin{align}\n" + self.math_reader(child[0][0]) + "\n\\end{align}\\\\\n")

                elif child[0].tag == self.ws + "text":  # Handle pure text regions
                    if self.debug:
                        print("Type: Text region.")
                    # Write result of the region by calling fuction which sends the current element
                    self.tex_file.write(self.text_reader(child[0]) + "\\\\\n")

            except TypeError:  # Catch the most common error
                print("Unsupported expessions found OR error occured, could not parse region", self.i)
            self.matrix_array = []  # Reset matrix array

        self.tex_file.write(self.end_latex_doc)  # Write end of LaTeX document


root_widget = Tk()  # Initialize Tkinter by creating a root widget others will be children of
new_app = ParseGUI(root_widget)  # Create a new instance of the ParseGUI class using the root widget as a parent

root_widget.wm_title("Mathcad to LaTeX converter")  # Set window title
root_widget.geometry('380x90')  # Set window size
root_widget.resizable(width=False, height=False)  # Make the window non-resizable
root_widget.mainloop()  # Start a loop that ends when the quit event is called (X button on window)
