## Version 0.1.4 (2018/12/22)

This is a bug fix release, mainly to resolve an incompatibility with Spyder 3.3.2.

### Issues Closed

* [Issue 183](https://github.com/spyder-ide/spyder-notebook/issues/183) - Resolve CI test failures with Python 2 ([PR 182](https://github.com/spyder-ide/spyder-notebook/pull/182))
* [Issue 181](https://github.com/spyder-ide/spyder-notebook/issues/181) - Update handling of temp directory for Spyder 3.3.2 ([PR 178](https://github.com/spyder-ide/spyder-notebook/pull/178))
* [Issue 179](https://github.com/spyder-ide/spyder-notebook/issues/179) - Update tests for pytest v4 ([PR 180](https://github.com/spyder-ide/spyder-notebook/pull/180))
* [Issue 172](https://github.com/spyder-ide/spyder-notebook/issues/172) - Remove untitled notebooks after they are closed ([PR 190](https://github.com/spyder-ide/spyder-notebook/pull/190))

In this release 4 issues were closed.

### Pull Requests Merged

* [PR 190](https://github.com/spyder-ide/spyder-notebook/pull/190) - PR: Delete file when closing notebook if in temp dir ([172](https://github.com/spyder-ide/spyder-notebook/issues/172))
* [PR 182](https://github.com/spyder-ide/spyder-notebook/pull/182) - PR: Specify Qt 5 in CI test script ([183](https://github.com/spyder-ide/spyder-notebook/issues/183))
* [PR 180](https://github.com/spyder-ide/spyder-notebook/pull/180) - PR: Use test fixture as pytest intends it ([179](https://github.com/spyder-ide/spyder-notebook/issues/179))
* [PR 178](https://github.com/spyder-ide/spyder-notebook/pull/178) - PR: Fix Spyder 3.3.2 import of TEMPDIR ([181](https://github.com/spyder-ide/spyder-notebook/issues/181))

In this release 4 pull requests were closed.


## Version 0.1.3 (2018/09/01)

This is a bug fix release, which resolves some problems reported by our users.

### Issues Closed

* [Issue 166](https://github.com/spyder-ide/spyder-notebook/issues/166) - Tests leave temporary directories in the home dir ([PR 167](https://github.com/spyder-ide/spyder-notebook/pull/167))
* [Issue 163](https://github.com/spyder-ide/spyder-notebook/issues/163) - test_open_notebook fails when running tests twice in a row ([PR 164](https://github.com/spyder-ide/spyder-notebook/pull/164))
* [Issue 160](https://github.com/spyder-ide/spyder-notebook/issues/160) - Set up pep8speaks
* [Issue 158](https://github.com/spyder-ide/spyder-notebook/issues/158) - Make plugin compatible with Spyder's split-plugins change ([PR 165](https://github.com/spyder-ide/spyder-notebook/pull/165))
* [Issue 157](https://github.com/spyder-ide/spyder-notebook/issues/157) - Be more robust when starting notebook ([PR 168](https://github.com/spyder-ide/spyder-notebook/pull/168))
* [Issue 156](https://github.com/spyder-ide/spyder-notebook/issues/156) - Migrate to CircleCI 2.0 ([PR 159](https://github.com/spyder-ide/spyder-notebook/pull/159))
* [Issue 153](https://github.com/spyder-ide/spyder-notebook/issues/153) - TypeError when parsing JSON when shutting kernel down ([PR 161](https://github.com/spyder-ide/spyder-notebook/pull/161))
* [Issue 152](https://github.com/spyder-ide/spyder-notebook/issues/152) - Opening console for notebook without kernel yields an error ([PR 170](https://github.com/spyder-ide/spyder-notebook/pull/170))
* [Issue 141](https://github.com/spyder-ide/spyder-notebook/issues/141) - Spyder notebook complains about missing file or directory: 'jupyter' ([PR 168](https://github.com/spyder-ide/spyder-notebook/pull/168))

In this release 9 issues were closed.

### Pull Requests Merged

* [PR 170](https://github.com/spyder-ide/spyder-notebook/pull/170) - PR: Display error when opening console for notebook with no kernel ([152](https://github.com/spyder-ide/spyder-notebook/issues/152))
* [PR 168](https://github.com/spyder-ide/spyder-notebook/pull/168) - PR: Do not call the jupyter executable when opening notebooks ([157](https://github.com/spyder-ide/spyder-notebook/issues/157), [141](https://github.com/spyder-ide/spyder-notebook/issues/141))
* [PR 167](https://github.com/spyder-ide/spyder-notebook/pull/167) - PR: Remove temporary directory created in test_open_notebook() ([166](https://github.com/spyder-ide/spyder-notebook/issues/166))
* [PR 165](https://github.com/spyder-ide/spyder-notebook/pull/165) - PR: Update to Spyder 4 after the split-plugins merge ([158](https://github.com/spyder-ide/spyder-notebook/issues/158))
* [PR 164](https://github.com/spyder-ide/spyder-notebook/pull/164) - PR: Make tests use a temporary directory ([163](https://github.com/spyder-ide/spyder-notebook/issues/163))
* [PR 161](https://github.com/spyder-ide/spyder-notebook/pull/161) - PR: More robust parsing of server reply in NotebookClient.get_kernel_id() ([153](https://github.com/spyder-ide/spyder-notebook/issues/153))
* [PR 159](https://github.com/spyder-ide/spyder-notebook/pull/159) - PR: Upgrade to CircleCI v2.0 ([156](https://github.com/spyder-ide/spyder-notebook/issues/156))

In this release 7 pull requests were closed.


## Version 0.1.2 (2018-02-15)

### Bugs fixed

**Issues**

* [Issue 137](https://github.com/spyder-ide/spyder-notebook/issues/137) - Add Opencollective badges to the project ([PR 138](https://github.com/spyder-ide/spyder-notebook/pull/138))
* [Issue 122](https://github.com/spyder-ide/spyder-notebook/issues/122) - Template for the reports of issues ([PR 124](https://github.com/spyder-ide/spyder-notebook/pull/124))
* [Issue 121](https://github.com/spyder-ide/spyder-notebook/issues/121) - Changes for compatibility with new undocking behavior of Spyder ([PR 123](https://github.com/spyder-ide/spyder-notebook/pull/123))
* [Issue 118](https://github.com/spyder-ide/spyder-notebook/issues/118) - Open the welcome tab if no tab is open ([PR 125](https://github.com/spyder-ide/spyder-notebook/pull/125))
* [Issue 113](https://github.com/spyder-ide/spyder-notebook/issues/113) - Server error because it takes too much time to start ([PR 117](https://github.com/spyder-ide/spyder-notebook/pull/117))
* [Issue 39](https://github.com/spyder-ide/spyder-notebook/issues/39) - how-to installation / testing ([PR 124](https://github.com/spyder-ide/spyder-notebook/pull/124))

In this release 6 issues were closed.

**Pull requests**

* [PR 138](https://github.com/spyder-ide/spyder-notebook/pull/138) - PR: Update README.md with Open collective info and missing badges. ([137](https://github.com/spyder-ide/spyder-notebook/issues/137))
* [PR 125](https://github.com/spyder-ide/spyder-notebook/pull/125) - PR: Open a 'welcome' tab if there are no open tabs ([118](https://github.com/spyder-ide/spyder-notebook/issues/118))
* [PR 124](https://github.com/spyder-ide/spyder-notebook/pull/124) - PR: Add issue template and a link to the Spyder group for contact. ([39](https://github.com/spyder-ide/spyder-notebook/issues/39), [122](https://github.com/spyder-ide/spyder-notebook/issues/122))
* [PR 123](https://github.com/spyder-ide/spyder-notebook/pull/123) - PR: Change 'menu' for 'options_menu' for the new Spyder 4 undocking feature ([121](https://github.com/spyder-ide/spyder-notebook/issues/121))
* [PR 117](https://github.com/spyder-ide/spyder-notebook/pull/117) - PR: Increase time for server to start ([113](https://github.com/spyder-ide/spyder-notebook/issues/113))
* [PR 105](https://github.com/spyder-ide/spyder-notebook/pull/105) - PR: Fix changelog

In this release 6 pull requests were closed.

---

## Version 0.1.1 (2017-08-06)

### Bugs fixed

**Issues**

* [Issue 103](https://github.com/spyder-ide/spyder-notebook/issues/103) - Release 0.1.1
* [Issue 101](https://github.com/spyder-ide/spyder-notebook/issues/101) - Files in MANIFEST.in not included in the installation
* [Issue 99](https://github.com/spyder-ide/spyder-notebook/issues/99) - Include runtests.py in MANIFEST.in
* [Issue 98](https://github.com/spyder-ide/spyder-notebook/issues/98) - Change Spyder version from setup.py
* [Issue 97](https://github.com/spyder-ide/spyder-notebook/issues/97) - Add setup.cfg to create universal wheels

In this release 5 issues were closed.

**Pull requests**

* [PR 102](https://github.com/spyder-ide/spyder-notebook/pull/102) - PR: Bugfixes after 0.1
* [PR 100](https://github.com/spyder-ide/spyder-notebook/pull/100) - PR: Update RELEASE.md with further instructions

In this release 2 pull requests were closed.

---

## Version 0.1 (2017-08-05)

### New features

Initial release

### Bugs fixed

**Issues**

* [Issue 93](https://github.com/spyder-ide/spyder-notebook/issues/93) - How to open notebooks after a failed (because slow) server start?
* [Issue 86](https://github.com/spyder-ide/spyder-notebook/issues/86) - Add RELEASE.md file
* [Issue 85](https://github.com/spyder-ide/spyder-notebook/issues/85) - Pandas Dataframes are not rendered as html tables but as plain text
* [Issue 83](https://github.com/spyder-ide/spyder-notebook/issues/83) - Notebook servers are not terminated after closing Spyder
* [Issue 75](https://github.com/spyder-ide/spyder-notebook/issues/75) - Add a menu entry to open an IPython console
* [Issue 74](https://github.com/spyder-ide/spyder-notebook/issues/74) - Check compatibility for PyQt4 and WebEngine
* [Issue 69](https://github.com/spyder-ide/spyder-notebook/issues/69) - Make Ctrl+P to show the file switcher here
* [Issue 67](https://github.com/spyder-ide/spyder-notebook/issues/67) - Add an "Open recent" menu
* [Issue 66](https://github.com/spyder-ide/spyder-notebook/issues/66) - Add ellipsis to shortened notebook names
* [Issue 64](https://github.com/spyder-ide/spyder-notebook/issues/64) - Ask users if they want to save untitled notebooks before closing them
* [Issue 61](https://github.com/spyder-ide/spyder-notebook/issues/61) - Hide server cmd.exe windows on Windows
* [Issue 60](https://github.com/spyder-ide/spyder-notebook/issues/60) - Create untitled notebooks under Spyder's TEMPDIR/notebooks
* [Issue 58](https://github.com/spyder-ide/spyder-notebook/issues/58) - Header not hiding when using the "Save as..." function
* [Issue 56](https://github.com/spyder-ide/spyder-notebook/issues/56) - Update Readme
* [Issue 54](https://github.com/spyder-ide/spyder-notebook/issues/54) - Installation is failing if jupyter notebook isn't already installed
* [Issue 52](https://github.com/spyder-ide/spyder-notebook/issues/52) - Add Jupyter Trove classifier
* [Issue 51](https://github.com/spyder-ide/spyder-notebook/issues/51) - Release 0.1
* [Issue 48](https://github.com/spyder-ide/spyder-notebook/issues/48) - Rename the plugin to Notebook
* [Issue 47](https://github.com/spyder-ide/spyder-notebook/issues/47) - Add more tests
* [Issue 45](https://github.com/spyder-ide/spyder-notebook/issues/45) - Add a file switcher instance to this plugin
* [Issue 41](https://github.com/spyder-ide/spyder-notebook/issues/41) - Add test that verifies that plugin starts and creates new notebooks
* [Issue 37](https://github.com/spyder-ide/spyder-notebook/issues/37) - Rename "Open a new notebook" action to "New notebook"
* [Issue 31](https://github.com/spyder-ide/spyder-notebook/issues/31) - Add plugin actions (Open, Save, etc) to the `NotebookWidget` context menu
* [Issue 30](https://github.com/spyder-ide/spyder-notebook/issues/30) - Add an "Open..." action
* [Issue 28](https://github.com/spyder-ide/spyder-notebook/issues/28) - Add code autoformatting, autolinting, test etc... ciocheck
* [Issue 21](https://github.com/spyder-ide/spyder-notebook/issues/21) - Create a pypi package
* [Issue 19](https://github.com/spyder-ide/spyder-notebook/issues/19) - [Errno 2] No such file or directory message
* [Issue 15](https://github.com/spyder-ide/spyder-notebook/issues/15) - Shorten file names to not pass 15 characters
* [Issue 13](https://github.com/spyder-ide/spyder-notebook/issues/13) - Create an Options menu with a way to move notebooks
* [Issue 12](https://github.com/spyder-ide/spyder-notebook/issues/12) - Add a workaround for notebook 4.3+
* [Issue 11](https://github.com/spyder-ide/spyder-notebook/issues/11) - Add a "+" button to the tab bar to let people know how to open new notebooks
* [Issue 9](https://github.com/spyder-ide/spyder-notebook/issues/9) - Hide header
* [Issue 8](https://github.com/spyder-ide/spyder-notebook/issues/8) - Make the notebook server to start Spyder kernels
* [Issue 5](https://github.com/spyder-ide/spyder-notebook/issues/5) - Shutdown kernel when closing a notebook
* [Issue 1](https://github.com/spyder-ide/spyder-notebook/issues/1) - Spelling Error in readme.md

In this release 35 issues were closed.

**Pull requests**

* [PR 95](https://github.com/spyder-ide/spyder-notebook/pull/95) - PR: Add welcome message page
* [PR 87](https://github.com/spyder-ide/spyder-notebook/pull/87) - PR: Add RELEASE.md file
* [PR 84](https://github.com/spyder-ide/spyder-notebook/pull/84) - PR: Close servers when closing Spyder
* [PR 82](https://github.com/spyder-ide/spyder-notebook/pull/82) - PR: Minor fix for a typo and a comment formatting
* [PR 80](https://github.com/spyder-ide/spyder-notebook/pull/80) - PR: Improve Readme and Changelog
* [PR 79](https://github.com/spyder-ide/spyder-notebook/pull/79) - PR: Add option to open an IPython console connected to the current notebook
* [PR 78](https://github.com/spyder-ide/spyder-notebook/pull/78) - PR: Add check_compatibility for PyQt4 and WebEngine
* [PR 77](https://github.com/spyder-ide/spyder-notebook/pull/77) - PR: Use Spyder kernel spec to create kernel notebooks
* [PR 72](https://github.com/spyder-ide/spyder-notebook/pull/72) - PR: Add notebook tabs to the global file switcher
* [PR 71](https://github.com/spyder-ide/spyder-notebook/pull/71) - PR: Add "Recent notebooks" menu entry
* [PR 70](https://github.com/spyder-ide/spyder-notebook/pull/70) - PR: Add ellipsis to shorten notebook names
* [PR 65](https://github.com/spyder-ide/spyder-notebook/pull/65) - PR: Add save question for modified untitled notebooks before closing them
* [PR 63](https://github.com/spyder-ide/spyder-notebook/pull/63) - PR: Add flag to not show cmd.exe windows on Windows
* [PR 62](https://github.com/spyder-ide/spyder-notebook/pull/62) - PR: Set a new tempdir for untitled notebooks
* [PR 59](https://github.com/spyder-ide/spyder-notebook/pull/59) - PR: Hide header after using Save as...
* [PR 57](https://github.com/spyder-ide/spyder-notebook/pull/57) - PR: Update Readme
* [PR 55](https://github.com/spyder-ide/spyder-notebook/pull/55) - PR: Move version out of init file.
* [PR 53](https://github.com/spyder-ide/spyder-notebook/pull/53) - PR: Add Jupyter Trove classifier
* [PR 50](https://github.com/spyder-ide/spyder-notebook/pull/50) - PR: Add more tests to this package
* [PR 49](https://github.com/spyder-ide/spyder-notebook/pull/49) - PR: Change the name of the plugin to 'Notebook'
* [PR 46](https://github.com/spyder-ide/spyder-notebook/pull/46) - PR: Add a file switcher instance
* [PR 44](https://github.com/spyder-ide/spyder-notebook/pull/44) - PR: Fixes to work with Notebook 4.3+
* [PR 43](https://github.com/spyder-ide/spyder-notebook/pull/43) - PR: Add a minimal test
* [PR 42](https://github.com/spyder-ide/spyder-notebook/pull/42) - PR: Hide the header of the notebook
* [PR 40](https://github.com/spyder-ide/spyder-notebook/pull/40) - PR: Add setup.py
* [PR 38](https://github.com/spyder-ide/spyder-notebook/pull/38) - PR: Change the name of the action to 'New notebook' instead of 'Open a new notebook'
* [PR 36](https://github.com/spyder-ide/spyder-notebook/pull/36) - PR: Add plugin actions to the 'NotebookWidget'
* [PR 35](https://github.com/spyder-ide/spyder-notebook/pull/35) - PR: Add action to open notebooks from a file
* [PR 29](https://github.com/spyder-ide/spyder-notebook/pull/29) - PR: Add CircleCI basic integration
* [PR 27](https://github.com/spyder-ide/spyder-notebook/pull/27) - PR: Add a better filter to the "Save as" dialog
* [PR 26](https://github.com/spyder-ide/spyder-notebook/pull/26) - PR: Shutdown kernel of the notebook before closing it
* [PR 25](https://github.com/spyder-ide/spyder-notebook/pull/25) - PR: Shorten notebook names with more than 15 characters
* [PR 24](https://github.com/spyder-ide/spyder-notebook/pull/24) - PR: Add a widget to do DOM manipulations using Javascript
* [PR 23](https://github.com/spyder-ide/spyder-notebook/pull/23) - PR: Fix [Errno 2] No such file or directory message
* [PR 20](https://github.com/spyder-ide/spyder-notebook/pull/20) - PR: Add 'Options menu' and a way to move notebooks ('Save as…')
* [PR 18](https://github.com/spyder-ide/spyder-notebook/pull/18) - PR: Change time to wait for the start of the server to max 10 secs.
* [PR 17](https://github.com/spyder-ide/spyder-notebook/pull/17) - PR: Don't try to set the widget fonts for now
* [PR 16](https://github.com/spyder-ide/spyder-notebook/pull/16) - PR: Add '+' button to open new notebooks.
* [PR 14](https://github.com/spyder-ide/spyder-notebook/pull/14) - PR: Simplify plugin title
* [PR 4](https://github.com/spyder-ide/spyder-notebook/pull/4) - PR: Initial implementation
* [PR 2](https://github.com/spyder-ide/spyder-notebook/pull/2) - PR: Spelling Error Fix

In this release 41 pull requests were closed.
