# -*- coding: utf-8 -*-
#
# Copyright (c) Spyder Project Contributors
# Licensed under the terms of the MIT License

"""
Widget to do DOM manipulations using Javascript

Some code here comes from the Ghost.py project:
https://github.com/jeanphix/Ghost.py
"""

from qtpy.QtWebEngineWidgets import WEBENGINE
from spyder.widgets.browser import WebView


class DOMWidget(WebView):

    def __init__(self, parent):
        super(DOMWidget, self).__init__(parent)
        if WEBENGINE:
            self.page = self.page()
        else:
            self.page = self.page().mainFrame()

    def evaluate(self, script):
        """Evaluates script in page frame.
        :param script: The script to evaluate.
        """
        if WEBENGINE:
            return self.page.runJavaScript("%s" % script)
        else:
            return self.page.evaluateJavaScript("%s" % script)

    def click(self, selector, btn=0):
        """Click the targeted element.
        :param selector: A CSS3 selector to targeted element.
        :param btn: The number of mouse button.
            0 - left button,
            1 - middle button,
            2 - right button
        """
        return self.evaluate("""
            (function () {
                var element = document.querySelector(%s);
                var evt = document.createEvent("MouseEvents");
                evt.initMouseEvent("click", true, true, window, 1, 1, 1, 1, 1,
                    false, false, false, false, %s, element);
                return element.dispatchEvent(evt);
            })();
        """ % (repr(selector), str(btn)))

    def set_input_value(self, selector, value):
        """Sets the value of the input matched by given selector."""
        script = 'document.querySelector("%s").setAttribute("value", "%s")'
        script = script % (selector, value)
        self.evaluate(script)
