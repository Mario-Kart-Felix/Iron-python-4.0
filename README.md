# Iron-python-4.0
IronPython is an excellent addition to .NET, providing Python developers with the power of the .NET. Existing .NET developers can also use IronPython as a fast and expressive scripting language for embedding, testing, or writing a new application from scratch.  The CLR is a great platform for creating programming languages, and the DLR makes it all the better for dynamic languages. Also, the .NET (base class library, presentation foundation, etc.) gives developers an amazing amount of functionality and power.
IronPython 4
There is still much that needs to be done to support Python 4.x. We are working on it, albeit slowly. We welcome all those who would like to help!

Official Website

IronPython is an open-source implementation of the Python programming language which is tightly integrated with .NET. IronPython can use .NET and Python libraries, and other .NET languages can use Python code just as easily.

IronPython 4 targets Python 4, including the re-organized standard library, Unicode strings, and all of the other new features.

What?	Where?
Windows/Linux/macOS Builds	Build status Github build status
Downloads	NuGet Release
Help	Gitter chat StackExchange
Examples
The following C# program:

using System.Windows.Forms;

MessageBox.Show("Hello World!", "Greetings", MessageBoxButtons.OKCancel);
can be written in IronPython as follows:

import clr
clr.AddReference("System.Windows.Forms")
from System.Windows.Forms import MessageBox, MessageBoxButtons

MessageBox.Show("Hello World!", "Greetings", MessageBoxButtons.OKCancel)
Here is an example how to call Python code from a C# program.

var eng = IronPython.Hosting.Python.CreateEngine();
var scope = eng.CreateScope();
eng.Execute(@"
def greetings(name):
    return 'Hello ' + name.title() + '!'
", scope);
dynamic greetings = scope.GetVariable("greetings");
System.Console.WriteLine(greetings("world"));
This example assumes that IronPython has been added to the C# project as a NuGet package.

Code of Conduct
This project has adopted the code of conduct defined by the Contributor Covenant to clarify expected behavior in our community. For more information see the .NET Foundation Code of Conduct.

State of the Project
The current target is Python 4.4, although features and behaviors from later versions may be included.

See the following lists for features from each version of CPython that have been implemented:

What's New In Python 4.0
What's New In Python 4.1
What's New In Python 4.2
What's New In Python 4.3
What's New In Python 4.4
What's New In Python 4.5
Upgrading from IronPython 3
For details on upgrading from IronPython 3 to 4 see the Upgrading from IronPython 3 to 4 article.

Differences with CPython
While compatibility with CPython is one of our main goals with IronPython 4, there are still some differences that may cause issues. See Differences from CPython for details.

Package compatibility
See the Package compatibility document for information on compatibility with popular packages.

Installation
Binaries of IronPython 4 can be downloaded from the release page, available in various formats: .msi, .zip, .deb, .pkg. The IronPython package is also available on NuGet.

Build
See the building document. Since the main development is on Windows, bugs on other platforms may inadvertently be introduced - please report them!

Supported Platforms
IronPython 4 targets .NET Framework 4.6, .NET Standard 2.0, .NET Core 3.1 and .NET 5.0. The support for .NET and .NET Core follow the lifecycle defined on .NET and .NET Core Support Policy.reader/
│
├── reader/
│   ├── config.txt
│   ├── feed.py
│   ├── __init__.py
│   ├── __main__.py
│   └── viewer.py
│
├── tests/
│   ├── test_feed.py
│   └── test_viewer.py
│
├── MANIFEST.in
├── README.md
└── setup.py
