import re
from pycombrowser.browser import COMBrowser, IterableFunctionBrowser
from pycombrowser.viewer import FunctionViewer


class XMLExport:
    XML_ESCAPE_CHARS = {
        "&": "&amp;",
        '"': "&quot;",
        "'": "&apos;",
        ">": "&gt;",
        "<": "&lt;",
    }

    def __init__(self, browser: COMBrowser, version=1.0, encoding: str = "UFT-8"):
        """Create a well-formed XML string for export.

        Parameters
        ----------
        browser: COMBrowser
            The object used to gather all variables.
        version
            The current version of the XML.
        encoding: str
            The encoding type (default is UTF-8).
        """
        self._browser = browser
        self._xml_head = '<?xml version="{}" encoding="{}"?>\n'.format(str(version), encoding)
        self._xml_str = ''
        self._attrs = ['Name', 'Count']
        self._generate()

    @property
    def string(self):
        """Return the well-formed XML in string format."""
        return self._xml_str

    @property
    def min(self):
        """Return the minimized XML in string format.

        The minimized version removes all newlines and tabs.
        """

        return re.sub('\n*\t*', '', self._xml_str)

    @staticmethod
    def xml_encode(text: str):
        """Map special XML characters to their encoded form in a given string."""
        return "".join(XMLExport.XML_ESCAPE_CHARS.get(c, c) for c in str(text))

    def _generate(self):
        """Begin generating the XML string."""
        self._xml_str = self._xml_head + self._generate_tag(self._browser)

    def _generate_tag(self, elem, tabs: int = 0, **kwargs) -> str:
        """Recursively generate each element into a string.

        Parameters
        ----------
        elem
            The element to convert into an XML string.
        tabs: int
            The indentation level of the current element.

        Returns
        -------
        str
            The XML string of the element and sub-elements.
        """

        xml = ''
        if isinstance(elem, (COMBrowser, IterableFunctionBrowser)):
            # setup the tag and attributes
            attrs = ["Name", "Count"]
            tag = XMLExport.Tag(elem.name)
            [
                tag.add_attr(attr, value)
                for attr, value in elem.all.items()
                if attr in attrs
            ]

            # add the element and start adding the sub-elements
            xml += '\t' * tabs + tag.open_tag + '\n'
            for item, value in elem.all.items():
                if item not in attrs:
                    xml += self._generate_tag(value, tabs + 1, name=item)
            xml += '\t' * tabs + tag.close_tag + '\n'
        elif isinstance(elem, FunctionViewer):
            # display the function and its properties
            tag = XMLExport.Tag("Function", name=elem.name, params=len(elem.args))
            xml += '\t' * tabs + tag.open_tag + tag.close_tag + '\n'
        elif isinstance(elem, BaseException):
            # display the error location and method
            tag = XMLExport.Tag("Error", on=str(elem.args[2][1]))
            xml += '\t' * tabs + tag.open_tag + '\n'
            xml += '\t' * (tabs + 1) + self.xml_encode(str(elem.args[2][2])) + '\n'
            xml += '\t' * tabs + tag.close_tag + '\n'
        else:
            # display the variable and value
            tag = XMLExport.Tag(kwargs.get('name', 'Unknown'))
            xml += '\t' * tabs + tag.open_tag + '\n'
            xml += '\t' * (tabs + 1) + self.xml_encode(elem) + '\n'
            xml += '\t' * tabs + tag.close_tag + '\n'
        return xml

    def print(self, minimize: bool = False):
        """Print the XML string in the normal or minimized version."""
        print(self._xml_str) if not minimize else print(min)

    class Tag:
        NAME_RE = re.compile('(^xml)|(^[0-9]*)', re.IGNORECASE)

        def __init__(self, tag_name: str, **attrs):
            """Create and store XML tag information in the proper formatting.

            Parameters
            ----------
            tag_name: str
                The name that will be displayed.
            attrs
                The attributes to add.
            """
            self._name = self.format_name(tag_name)
            self._attrs = {
                self.format_name(key): value
                for key, value in attrs.items()
            }

        @property
        def name(self) -> str:
            """Return the name of the tag."""
            return self._name

        @property
        def attrs(self) -> dict:
            """Return a dictionary of the tag attributes in the form {attr: value}."""
            return self._attrs

        @property
        def open_tag(self) -> str:
            """Return the formatted opening tag."""
            tag = "<" + self._name
            if len(self._attrs) > 0:
                # add the attributes
                tag += " " + " ".join(
                    '{}="{}"'.format(key, value)
                    for key, value in self._attrs.items()
                )
            return tag + ">"

        @property
        def close_tag(self):
            """Return the formatted closing tag."""
            return "</{}>".format(self._name)

        @staticmethod
        def format_name(text: str) -> str:
            """Return a string formatted to XML tag naming conventions."""
            text = XMLExport.Tag.NAME_RE.sub('', text)
            return text.strip('!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~')

        def add_attr(self, attr: str, value):
            """Add an attribute to the tag."""
            attr = self.format_name(attr)
            self._attrs[attr] = value

        def rm_attr(self, attr):
            """Remove and return a tag attribute."""
            attr = self.format_name(attr)
            return self._attrs.pop(attr)


# TODO: export as a json
class JSONExport:
    pass


# TODO write to file
def save_as():
    pass