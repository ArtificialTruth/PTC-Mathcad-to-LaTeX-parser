# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ElemTree  # Import the XML ElementTree module aliased as ET
import io  # Import used for more advanced file writing
import os  # Used for file name handling
import numpy  # Used for arrays, and more advanced math manipulation
import base64  # Used for reading base64 encoded pictures
from tkinter.filedialog import askopenfilename  # Tkinter libs or selecting files in OS file picker
from tkinter import Tk, Frame, Button, Label, StringVar, Entry  # Used for the GUI
# Other files
from symbol_parser import symbol_parser  # Import function which formats special charecters


class ParseGUI(object):
    """Class used for the GUI
    The object parameter is the root widget for the Tkinter GUI
    """
    def __init__(self, master):
        """Constructor method

        :param master: A "master" wigdet
        """
        self.mainframe = Frame(master)  # Create a Frame child widget
        self.mainframe.pack()  # Make the widget visible

        self.path = ''  # Define default path for the .xmcd file
        self.texfile_path = ''  # Define path for the .tex file

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

        self.parse_file = Button(self.mainframe, text="Open LaTeX file", command=self.open_file)
        self.parse_file.pack(side="right")

        self.select_file = Button(self.mainframe, text="Select file", command=self.select_file)  # Runs a class method
        self.select_file.pack(side="right")

    def select_file(self):  # Method used for selecting a file
        self.path = askopenfilename()  # Display native os file dialog for choosing a file
        self.filename.set("Current selected file: " + os.path.basename(self.path))  # Change the dynamic variable
        self.status.set("Status: Not parsed")  # Set status

    def open_file(self):  # Method used for opening the parsed LaTeX file
        self.texfile_path = os.path.dirname(self.path) + '/ParsedLatexFile/' + os.path.splitext(os.path.basename(self.path))[0] + '.tex'
        if self.status.get() == "Status: File tried parsed! Look under the folder \ParsedLatexFile !":
            os.system("start " + "\"\" \"" + self.texfile_path + "\"")

    def parse_file(self):  # Method for parsing the chosen file
        # Make sure a file is selected and it is a Mathcad file before trying to parse it
        if self.filename.get() != 'Current selected file: none' and os.path.splitext(self.path)[1] == '.xmcd':
            self.status.set("Status: Tring to parse... (most files takes a few seconds)")
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

        self.output_folder = os.path.dirname(self.target_file) + "/ParsedLatexFile"
        if not os.path.exists(self.output_folder):  # If this folder doesn't exist
            os.makedirs(self.output_folder)  # Create it

        # Open a new tex file for writing. Encoding for Danish chars etc. Save in a folder
        self.tex_file = io.open(self.output_folder + "/" + self.filename + '.tex', 'w', encoding="utf-8")

        # Standard LaTeX document info as strings
        self.start_latex_doc = "\\documentclass[10pt,a4paper]{report}\n\\usepackage[utf8]{inputenc}\n" \
                               "\\usepackage[T1]{fontenc}\n\\usepackage{amsmath}\n\\usepackage{amsfonts}\n" \
                               "\\usepackage{amssymb}\n\\usepackage{graphicx}\n\\begin{document}\n\\noindent\n"
        self.end_latex_doc = "\end{document}"

        self.matrix_array = []  # Array to use for multiple values in matrixes

        self.i = 0  # Counter

        self.debug = False  # Toggle debug messages

        if math_tree_ok:  # Only run if file isn't corrupted
            self.main()  # Run main method

    def math_reader(self, elem):
        """Method for getting the math out of the XML file
        
        This method is used for reading the XML file (the ElementTree).
        Generally speaking this method gathers the data, the
        latex_formatter method uses to format the data into LaTeX.
        So no LaTeX-specific formatting is done in this method.
        Recursive method for efficiency and simplicity.
        
        This method is used for math Mathcad regions.
        :param elem: A ElementTree
        :return: Full LaTeX formatted math expressions
        """
        elem.tag = elem.tag.replace(self.ml, "")  # Only leave operator name left without prefix

        if elem.tag == "apply":  # If current Element's tag is apply
            # We need two cases; One for apply tag which includes a operator, and everything else
            # The first will always be the operator, if there's one
            if self.debug:  # Only prints debug messages if debug = True
                print("Apply tag found")

            # Either there's a operator (2 or 3 childs, first element is always the operator)
            if bool(elem[0]) is False and elem[0].text is None:  # Checks if the elem has children and doesn't have text
                if self.debug:  # Only prints debug messages if debug = True
                    print("Apply tag includes a operator")

                if len(elem) == 3:  # Either there's 3 parts (normal mathemathical expression)
                    if self.debug:
                        print("len(elem)", len(elem))
                    val1 = self.math_reader(elem[1])  # Call this method again with 2nd child again to get first value
                    val2 = self.math_reader(elem[2])  # Call this method again with 3rd child again to get second value
                    # Return the formatted result (by calling math_formatter), to the original caller of this method
                    return self.latex_formatter(elem[0].tag, val1, val2)  # Sends the operator and the two values

                elif len(elem) == 2:  # Used for other operators where there's only "two" parts
                    if self.debug:
                        print("len(elem)", len(elem))
                    val1 = self.math_reader(elem[1])  # Call this method again, skip the operator tag elem
                    return self.latex_formatter(elem[0].tag, val1)  # Get first child's tag which is the operator

            # ToDo: Make a more general way of handling apply tags?
            # Or there's no operator - this is the case for ex cos(x)
            # One of the 2 childs, must have children too, or text
            elif bool(elem[0]) or bool(elem[1]) or elem[0].text or elem[1].text is not None:
                val1 = self.math_reader(elem[0])
                val2 = self.math_reader(elem[1])
                return self.latex_formatter(elem.tag, val1, val2)

        # ToDo?: The following else tag checks, are only for non-operator tags, elements with no children or text
        elif elem.tag == "parens":  # Handle parenteses
            return self.latex_formatter(elem.tag, self.math_reader(elem[0]))  # Only 1 value between parenteses

        # Current tag is some kind of equal sign
        elif elem.tag == "define" or elem.tag == "symEval":
            if self.debug:
                print("A type of equal expression found.")
            return self.latex_formatter(elem.tag, self.math_reader(elem[0]), self.math_reader(elem[1]))

        # Eval works like normal equal operator, if the result is not defined using "define"
        # ToDo: add a way to handle non-user defined units in the result, and possibly add library to format to LaTeX?
        elif elem.tag == "eval":
            # Either the evaluated expression doesn't have a user defined unit in the result
            if len(elem) == 2:
                return self.latex_formatter(elem.tag, self.math_reader(elem[0]), self.math_reader(elem[1]))

            # Or it does, and we can use that as the unit
            elif len(elem) == 3:
                value_and_unit = self.math_reader(elem[2]) + self.math_reader(elem[1])
                return self.latex_formatter(elem.tag, self.math_reader(elem[0]), value_and_unit)

        elif elem.tag == "provenance":  # Interesting Mathcad structure handled here
            return self.math_reader(elem[len(elem)-1])  # Simply call this method again with the last child element

        elif elem.tag == "id":  # Current tag is pure text
            if self.debug:
                print("Text found:", elem.text)
            return self.latex_formatter(elem.tag, elem)  # Call external function with text

        elif elem.tag == "real":  # Current is a real number
            if self.debug:
                print("Number found:", elem.text)
            return elem.text  # Simply return the value as string

        # Result is used with equal signs, boundVars is used for special variables
        # degree is used for n'te degree derivatives
        # symResult is a result from a symbolic evaluation
        elif elem.tag == "result" or elem.tag == "boundVars" or elem.tag == "degree" or elem.tag == "symResult":
            if self.debug:
                print("Result found.")
            return self.math_reader(elem[0])
            # return elem[0][0].text  # Simply return the value as string

        elif elem.tag == "vectorize":  # Current tag is a vector notation
            if self.debug:
                print("Vector found.")
            return self.latex_formatter(elem.tag, self.math_reader(elem[0]))

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
            return self.latex_formatter(elem.tag, numpy_matrix_array, array_dimensions)  # Send array and the dimensons
            
        elif elem.tag == "placeholder":  # Current tag is just a placeholder
            if self.debug:
                print("Empty placeholder found.")
            return " "  # Return space

        elif elem.tag == "lambda" or elem.tag == "bounds":
            # lambda is used for both derivative and integral (+ more?!).
            # bounds is used for integral with limits
            # Therefore the latex_formatter must handle it, we can't go backwards in elements?
            return elem

        elif elem.tag == "unitedValue" or elem.tag == "unitOverride":  # Value and/or unit
            if self.debug:
                print("Unit stuff found.")
            return self.math_reader(elem[0])

        elif elem.tag == "function":
            if self.debug:
                print("Function found.")
            return self.latex_formatter(elem.tag, self.math_reader(elem[0]), self.math_reader(elem[1]))

        else:  # For unsupported tags
            print("Error, non-supported tag found at region", self.i)  # Print the problematic region number
            print("Current Elem.tag:", elem.tag)  # Debug message

    def text_reader(self, elem):
        """Pure text formatter method

        This method is used for text Mathcad regions.
        :param elem: The ElementTree that contains text
        :param special_char:
        :return: Formatted text with escape chars
        """
        text = ""  # Set default values
        i = 1
        i2 = 1

        if self.debug:
            print("Type: Text region.")

        for paragraph in elem:  # For each paragraph, in the text region
            i += 1
            if bool(paragraph) is True:  # Check if the paragraph has children
                i2 += 1
                for text_object in paragraph:  # Run through every item in the tree

                    """ToDo: Don't add newlines in this forloop (unless there's only 1 child in paragraph), just add
                    # the things in one long ass line"""
                    # To handle the "f" element that should be on the same line as the inline math, we have two cases.
                    # Either the element has a "region" with math
                    if paragraph.find(self.ws + "region") is not None:
                        if text_object.tag == self.ws + "region":
                            text += paragraph.text  # Grap the text infront of the inline math
                            text += " $ " + self.math_reader(paragraph[0][0][0]) + " $ "

                        elif text_object.tag == self.ws + "f":

                            if bool(text_object) is True:
                                if bool(text_object[0]) is False:  # Check if the element have a <sp/> child
                                    if i2 <= len(elem):
                                        text += text_object[0].text + " \\\\\n"  # The <inlineAttr> text
                                    else:
                                        text += text_object[0].text + " \\\\"

                                elif bool(text_object[0]) is True:  # The element has a <sp/> child
                                    text += " \n"

                            else:
                                if i2 <= len(elem):  # For every paragraph that isn't the last
                                    # family="Mathcad UniMath" symbols
                                    text += symbol_parser(text_object.text, False) + " \\\\\n"
                                else:
                                    text += symbol_parser(text_object.text, False) + " \\\\"

                    # Or it doesn't have a region with math.
                    else:
                        """
                        if text_object.tag == self.ws + "region":
                            text += paragraph.text  # Grap the text infront of the inline math
                            text += " $ " + self.math_reader(paragraph[0][0][0]) + " $ "
                        """
                        if text_object.tag == self.ws + "f":

                            if bool(text_object) is False:  # Check if the element don't have children
                                if i2 <= len(elem):  # For every paragraph that isn't the last
                                    # family="Mathcad UniMath" symbols
                                    text += symbol_parser(text_object.text, False) + " \\\\\n"
                                else:
                                    text += symbol_parser(text_object.text, False) + " \\\\"

                            elif bool(text_object) is True:
                                if bool(text_object[0]) is False:  # The element don't have children
                                    if i2 <= len(elem):
                                        text += text_object[0].text + " \\\\\n"  # The <inlineAttr> text
                                    else:
                                        text += text_object[0].text + " \\\\"
                                else:  # The element has a <sp/> child
                                    text += " "

            elif bool(paragraph) is False:
                if i <= len(elem):  # For every paragraph that isn't the last
                    text += paragraph.text + " \\\\\n"
                else:  # For the last paragraph (no newline)
                    text += paragraph.text + " \\\\"

        return symbol_parser(text, False)

    def picture_reader(self, elem):
        """Method for reading binary picture data

        This method converts the desired picture from base64 data to a .png image
        :param elem: The picture region as a ElementTree
        :return: The LaTeX code including the image file
        """
        image_id = int(elem[0].attrib["item-idref"])  # Grap the image ID from the elements attributes
        image_base64_data = self.math_tree[4][image_id-1].text  # Find the image data in the binaryContent part
        image_base64_data = image_base64_data.encode(encoding='UTF-8')  # Encode string as bytes instead
        filename = self.filename + "_" + str(image_id) + ".png"
        filename_no_ext = self.filename + "_" + str(image_id)

        # Open a new file for writing, name it the filename_id
        with open(self.output_folder + "/" + filename, "wb") as imagefile:  # Open the file, and close it afterwards
            imagefile.write(base64.decodebytes(image_base64_data))  # Write the decoded base64 bytes to the file

        return "\\includegraphics{\"" + filename_no_ext + "\"}"

    def latex_formatter(self, operator, x, y=None):  # Define the value of y
        """LaTeX math syntax formatter metod
        
        This method takes in the data math_reader() has found in the XML file,
        and formats it into LaTeX expressions.
        
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

            elif operator == "eval" or operator == "equal" or operator == "define" or operator == "symEval":
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
                for i in range(0, rows):  # Run this loop the amount of rows there exists
                    for entity in x[i, :]:  # For each value in the i'nte row
                        if i2 == cols:  # RNS checkmate
                            string += entity
                        else:
                            string = string + entity + " & "
                        i2 += 1
                    i2 = 1
                    string += "\\\\\n"

                string += "\\end{pmatrix}"
                return string

            # Return two strings that needs to be merged
            elif operator == "apply" or operator == "function":
                # For now we assume that the parenthesis is required
                return x + "\\left(" + y + "\\right)"

            elif operator == "integral":  # For integrals with limits
                lim_a = self.math_reader(y[0])
                lim_b = self.math_reader(y[1])
                var = self.math_reader(x[0])
                func = self.math_reader(x[1])
                return "\\int_{" + lim_a + "}^{" + lim_b + "} " + func + " d" + var

            elif operator == "derivative":  # For n'te derivative notation
                return "\\frac{d^" + y + "}{d" + self.math_reader(x[0]) + "^" + y + "}" + self.math_reader(x[1])

            elif operator == "indexer":  # For subscripts
                return x + "_{" + y + "}"

            else:
                return "Unhandled tag (y given) :("
                
        else:  # Else, there is only 1 value
            if self.debug:
                print("No y given")

            if operator == "id":
                if x.get("subscript") is not None:  # Checks if the attribute exists
                    return symbol_parser(x.text, True) + "_{" + x.attrib["subscript"] + "}"  # Find the attribute subscript
                else:
                    return symbol_parser(x.text, True)

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

            elif operator == "derivative":  # For derivative notation
                return "\\frac{d}{d" + self.math_reader(x[0]) + "}" + self.math_reader(x[1])

            elif operator == "integral":  # For integrals.
                var = self.math_reader(x[0])
                func = self.math_reader(x[1])
                return "\\int " + func + " d" + var

            else:
                return "Unhandled tag (y given) :("

    def main(self):
        """Method for controlling file writing

        Writes the final results to the new .tex file
        """
        self.tex_file.write(self.start_latex_doc)  # Write start of LaTeX document

        for child in self.math_tree[3]:  # Run for each region containing math or text
            self.i += 1  # Update counter
            print("\nTrying to parse the " + str(self.i) + "' region")  # Line separator for ouput
            # ToDo: Print the actual region-id
            # print("(region-id: " + child[0].attr["region-id"] + ")")

            try:  # Try to parse
                # ToDo: Smart align, that check for next region, if it's text or not?
                if child[0].tag == self.ws + "math":  # Math region
                    if self.debug:
                        print("Type: Math region.")
                    # Write result of the region by calling fuction which sends the current element
                    self.tex_file.write("\\begin{align}\n" + self.math_reader(child[0][0]) + "\n\\end{align}\\\\\n\n")

                elif child[0].tag == self.ws + "text":  # Handle pure text regions
                    if self.debug:
                        print("Type: Text region.")
                    self.tex_file.write(self.text_reader(child[0]) + "\n")

                elif child[0].tag == self.ws + "picture":  # Handle pure picture regions
                    if self.debug:
                        print("Type: Picture region.")
                    self.tex_file.write(self.picture_reader(child[0]) + "\\\\\n")

            except TypeError:  # Catch the most common error
                print("Unsupported expessions found OR error occured, could not parse region", self.i)

        self.tex_file.write(self.end_latex_doc)  # Write end of LaTeX document


root_widget = Tk()  # Initialize Tkinter by creating a root widget others will be children of
new_app = ParseGUI(root_widget)  # Create a new instance of the ParseGUI class using the root widget as a parent

root_widget.wm_title("Mathcad to LaTeX converter")  # Set window title
root_widget.geometry('380x90')  # Set window size
root_widget.resizable(width=False, height=False)  # Make the window non-resizable
root_widget.mainloop()  # Start a loop that ends when the quit event is called (X button on window)
