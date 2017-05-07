# -*- coding: utf-8 -*-
#
# Copyright (c) Spyder Project Contributors
# Licensed under the terms of the MIT License

"""
Widget to do DOM manipulations using Javascript.

Some code here comes from the Ghost.py project:
https://github.com/jeanphix/Ghost.py
"""

from qtpy.QtWebEngineWidgets import WEBENGINE
from spyder.widgets.browser import WebView


class DOMWidget(WebView):
    """Widget to do DOM manipulations using Javascript."""

    def __init__(self, parent):
        """Constructor."""
        super(DOMWidget, self).__init__(parent)
        if WEBENGINE:
            self.dom = self.page()
        else:
            self.dom = self.page().mainFrame()

    def evaluate(self, script):
        """
        Evaluate script in page frame.

        :param script: The script to evaluate.
        """
        if WEBENGINE:
            return self.dom.runJavaScript("{}".format(script))
        else:
            return self.dom.evaluateJavaScript("{}".format(script))

    def click(self, selector, btn=0):
        """
        Click the targeted element.

        :param selector: A CSS3 selector to targeted element.
        :param btn: The number of mouse button.
            0 - left button,
            1 - middle button,
            2 - right button
        """
        return self.evaluate("""
            (function () {{
                var element = document.querySelector({0});
                var evt = document.createEvent("MouseEvents");
                evt.initMouseEvent("click", true, true, window, 1, 1, 1, 1, 1,
                    false, false, false, false, {1}, element);
                return element.dispatchEvent(evt);
            }})();
        """.format(repr(selector), repr(btn)))

    def set_input_value(self, selector, value):
        """Set the value of the input matched by given selector."""
        script = 'document.querySelector("%s").setAttribute("value", "%s")'
        script = script % (selector, value)
        self.evaluate(script)

    def set_class_value(self, selector, classname):
        """Set the class of element matched by the given selector."""
        return self.evaluate("""
            (function () {{
            var element = document.querySelector({0});
            element.className = {1};
            }})();""".format(repr(selector), repr(classname)))
