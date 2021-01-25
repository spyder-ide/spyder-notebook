## Version 0.3.2 (2021/01/25)

### New Features

* Pressing Shift-Tab now shows the documentation of functions and so on, as in a Jupyter server ([Issue 315](https://github.com/spyder-ide/spyder-notebook/issues/315), [PR 344](https://github.com/spyder-ide/spyder-notebook/pull/344))
* Add an option to Preferences so that you can now have Spyder in a dark theme and notebooks in a light theme, or vice versa ([Issue 310](https://github.com/spyder-ide/spyder-notebook/issues/310), [PR 345](https://github.com/spyder-ide/spyder-notebook/pull/345))
* Shift-RightClick now shows the browser menu, which allows you to save a plot as a picture ([Issue 279](https://github.com/spyder-ide/spyder-notebook/issues/279), [PR 349](https://github.com/spyder-ide/spyder-notebook/pull/349))

### Bug Fixes

* Opening a link from a notebook now opens the correct page in your web browser ([Issue 185](https://github.com/spyder-ide/spyder-notebook/issues/185), [PR 351](https://github.com/spyder-ide/spyder-notebook/pull/351))
* If you change the Python interpreter in the Preferences, then notebooks opened afterwards will use the new environment; previously, you had to restart Spyder ([Issue 266](https://github.com/spyder-ide/spyder-notebook/issues/266), [PR 352](https://github.com/spyder-ide/spyder-notebook/pull/352))
* Update error message when server fails so that it is more helpful ([Issue 337](https://github.com/spyder-ide/spyder-notebook/issues/337), [PR 347](https://github.com/spyder-ide/spyder-notebook/pull/347))
* Prevent an AttributeError exception when saving or closing notebooks ([Issue 311](https://github.com/spyder-ide/spyder-notebook/issues/311), [Issue 333](https://github.com/spyder-ide/spyder-notebook/issues/333), [PR 334](https://github.com/spyder-ide/spyder-notebook/pull/334))
* Make saving more robust by waiting longer if necessary ([Issue 339](https://github.com/spyder-ide/spyder-notebook/issues/339), [PR 348](https://github.com/spyder-ide/spyder-notebook/pull/348))


## Version 0.3.1 (2020/11/01)

### Bug Fixes

* Fix compatibility issue which prevented the plugin from working at all if traitlets version 5 is installed ([Issue 314](https://github.com/spyder-ide/spyder-notebook/issues/314), [PR 326](https://github.com/spyder-ide/spyder-notebook/pull/326)).
* Add background to code completions to make them visible ([Issue 318](https://github.com/spyder-ide/spyder-notebook/issues/318), [PR 329](https://github.com/spyder-ide/spyder-notebook/pull/329)).
* Make strings brighter in dark mode to increase legibility ([Issue 319](https://github.com/spyder-ide/spyder-notebook/issues/319), [PR 331](https://github.com/spyder-ide/spyder-notebook/pull/331)).
* Prevent JSONDecodeError when closing notebook ([Issue 317](https://github.com/spyder-ide/spyder-notebook/issues/317), [PR 332](https://github.com/spyder-ide/spyder-notebook/pull/332)).


## Version 0.3.0 (2020/07/29)

### New Features

* The plugin now uses JupyterLab instead of Jupyter Notebook to render notebooks. This ensures that the new features developed by the Jupyter team, such as drag and drop to reorder code cells, are available in Spyder.
* Support for Python 2 is dropped. The plugin now requires Python 3.5 and Spyder 3.1 or later.
* Notebooks are rendered in a dark theme if Spyder is run using a dark theme.
* A new item, "Server Info", in the option menu of the plugin. This should help with troubleshooting in case of problems.
* Translations for Brazilian Portuguese, German and Spanish are now available.
* When you open Spyder, the plugin will open the notebooks that were open when you last quit Spyder.

### Issues Closed

* [Issue 306](https://github.com/spyder-ide/spyder-notebook/issues/306) - Shortcut 'M' does not switch cell type to Markdown ([PR 307](https://github.com/spyder-ide/spyder-notebook/pull/307))
* [Issue 305](https://github.com/spyder-ide/spyder-notebook/issues/305) - Enable translations ([PR 304](https://github.com/spyder-ide/spyder-notebook/pull/304))
* [Issue 296](https://github.com/spyder-ide/spyder-notebook/issues/296) - Check dependency on jupyterlab Python package ([PR 300](https://github.com/spyder-ide/spyder-notebook/pull/300))
* [Issue 295](https://github.com/spyder-ide/spyder-notebook/issues/295) - Plugin may use server not started by Spyder ([PR 298](https://github.com/spyder-ide/spyder-notebook/pull/298))
* [Issue 290](https://github.com/spyder-ide/spyder-notebook/issues/290) - Inherit dark or light theme from Spyder
* [Issue 288](https://github.com/spyder-ide/spyder-notebook/issues/288) - Use QProcess instead of subprocess to start server ([PR 298](https://github.com/spyder-ide/spyder-notebook/pull/298))
* [Issue 284](https://github.com/spyder-ide/spyder-notebook/issues/284) - Package JavaScript files ([PR 300](https://github.com/spyder-ide/spyder-notebook/pull/300))
* [Issue 280](https://github.com/spyder-ide/spyder-notebook/issues/280) - Normalize line endings in source ([PR 287](https://github.com/spyder-ide/spyder-notebook/pull/287))
* [Issue 275](https://github.com/spyder-ide/spyder-notebook/issues/275) - Move functionality out of NotebookPlugin ([PR 283](https://github.com/spyder-ide/spyder-notebook/pull/283))
* [Issue 270](https://github.com/spyder-ide/spyder-notebook/issues/270) - Replace sidebar by menubar in new notebook server ([PR 274](https://github.com/spyder-ide/spyder-notebook/pull/274))
* [Issue 261](https://github.com/spyder-ide/spyder-notebook/issues/261) - Transition to JupyterLab ([PR 264](https://github.com/spyder-ide/spyder-notebook/pull/264))
* [Issue 260](https://github.com/spyder-ide/spyder-notebook/issues/260) - Drop support for Python 2 ([PR 276](https://github.com/spyder-ide/spyder-notebook/pull/276))
* [Issue 245](https://github.com/spyder-ide/spyder-notebook/issues/245) - Cannot undock "Notebook" pane
* [Issue 171](https://github.com/spyder-ide/spyder-notebook/issues/171) - Cleanly exit notebook server ([PR 289](https://github.com/spyder-ide/spyder-notebook/pull/289))
* [Issue 133](https://github.com/spyder-ide/spyder-notebook/issues/133) - Using native menu actions of the notebook as 'Rename' its a point of failures
* [Issue 68](https://github.com/spyder-ide/spyder-notebook/issues/68) - Restore the previous list of opened notebooks (per session) ([PR 292](https://github.com/spyder-ide/spyder-notebook/pull/292))

In this release 16 issues were closed.

### Pull Requests Merged

* [PR 307](https://github.com/spyder-ide/spyder-notebook/pull/307) - PR: Add shortcuts that are available in Jupyter Lab ([306](https://github.com/spyder-ide/spyder-notebook/issues/306))
* [PR 304](https://github.com/spyder-ide/spyder-notebook/pull/304) - PR: Update translations from Crowdin ([305](https://github.com/spyder-ide/spyder-notebook/issues/305))
* [PR 303](https://github.com/spyder-ide/spyder-notebook/pull/303) - PR: Update localization source files
* [PR 300](https://github.com/spyder-ide/spyder-notebook/pull/300) - PR: Install JavaScript files and other server components in distribution ([296](https://github.com/spyder-ide/spyder-notebook/issues/296), [284](https://github.com/spyder-ide/spyder-notebook/issues/284))
* [PR 298](https://github.com/spyder-ide/spyder-notebook/pull/298) - PR: Rewrite code for starting and managing notebook servers ([295](https://github.com/spyder-ide/spyder-notebook/issues/295), [288](https://github.com/spyder-ide/spyder-notebook/issues/288))
* [PR 297](https://github.com/spyder-ide/spyder-notebook/pull/297) - PR: Implement dark theme
* [PR 292](https://github.com/spyder-ide/spyder-notebook/pull/292) - PR: Restore notebooks that were open at end of last session ([68](https://github.com/spyder-ide/spyder-notebook/issues/68))
* [PR 289](https://github.com/spyder-ide/spyder-notebook/pull/289) - PR: Shutdown notebook server properly ([171](https://github.com/spyder-ide/spyder-notebook/issues/171))
* [PR 287](https://github.com/spyder-ide/spyder-notebook/pull/287) - PR: Normalize line endings in text files to LF ([280](https://github.com/spyder-ide/spyder-notebook/issues/280))
* [PR 283](https://github.com/spyder-ide/spyder-notebook/pull/283) - PR: Split off part of NotebookPlugin into NotebookTabWidget ([275](https://github.com/spyder-ide/spyder-notebook/issues/275))
* [PR 276](https://github.com/spyder-ide/spyder-notebook/pull/276) - PR: Drop support for Python 2 ([260](https://github.com/spyder-ide/spyder-notebook/issues/260))
* [PR 274](https://github.com/spyder-ide/spyder-notebook/pull/274) - PR: Add menu bar to notebook ([270](https://github.com/spyder-ide/spyder-notebook/issues/270))
* [PR 264](https://github.com/spyder-ide/spyder-notebook/pull/264) - PR: Use JupyterLab to render notebooks ([261](https://github.com/spyder-ide/spyder-notebook/issues/261))

In this release 13 pull requests were closed.


## Version 0.2.3 (2020/03/21)

This release fixes some annoying bugs and UI glitches.

### Issues Closed

* [Issue 254](https://github.com/spyder-ide/spyder-notebook/issues/254) - Update badges in Readme ([PR 255](https://github.com/spyder-ide/spyder-notebook/pull/255))
* [Issue 245](https://github.com/spyder-ide/spyder-notebook/issues/245) - Cannot undock "Notebook" pane ([PR 256](https://github.com/spyder-ide/spyder-notebook/pull/256))
* [Issue 241](https://github.com/spyder-ide/spyder-notebook/issues/241) - Move CI to github actions ([PR 253](https://github.com/spyder-ide/spyder-notebook/pull/253))
* [Issue 215](https://github.com/spyder-ide/spyder-notebook/issues/215) - "Open recent" menu is buggy. Flickers when moused over. ([PR 256](https://github.com/spyder-ide/spyder-notebook/pull/256))
* [Issue 187](https://github.com/spyder-ide/spyder-notebook/issues/187) - Error when trying to open a moved recent file ([PR 249](https://github.com/spyder-ide/spyder-notebook/pull/249))
* [Issue 150](https://github.com/spyder-ide/spyder-notebook/issues/150) - Error when saving notebooks in write-protected directory ([PR 250](https://github.com/spyder-ide/spyder-notebook/pull/250))

In this release 6 issues were closed.

### Pull Requests Merged

* [PR 256](https://github.com/spyder-ide/spyder-notebook/pull/256) - PR: Use _options_menu instead of options_menu in plugin ([245](https://github.com/spyder-ide/spyder-notebook/issues/245), [215](https://github.com/spyder-ide/spyder-notebook/issues/215))
* [PR 255](https://github.com/spyder-ide/spyder-notebook/pull/255) - PR: Update badges in README ([254](https://github.com/spyder-ide/spyder-notebook/issues/254))
* [PR 253](https://github.com/spyder-ide/spyder-notebook/pull/253) - PR: Use GitHub Actions to do automatic testing ([241](https://github.com/spyder-ide/spyder-notebook/issues/241))
* [PR 250](https://github.com/spyder-ide/spyder-notebook/pull/250) - PR: Handle I/O errors when doing "Save As" ([150](https://github.com/spyder-ide/spyder-notebook/issues/150))
* [PR 249](https://github.com/spyder-ide/spyder-notebook/pull/249) - PR: Avoid reading notebook file when closing tab ([187](https://github.com/spyder-ide/spyder-notebook/issues/187))

In this release 5 pull requests were merged.


## Version 0.2.2 (2020/02/26)

This release corrects the bug fix in version 0.2.1 which was triggered opening or saving notebooks.

### Issues Closed

* [Issue 213](https://github.com/spyder-ide/spyder-notebook/issues/213) - closing_ipynb_tab ([PR 232](https://github.com/spyder-ide/spyder-notebook/pull/232))
* [Issue 192](https://github.com/spyder-ide/spyder-notebook/issues/192) - AttributeError: 'str' object has no attribute 'get' ([PR 232](https://github.com/spyder-ide/spyder-notebook/pull/232))

In this release 2 issues were closed.

### Pull Requests Merged

* [PR 234](https://github.com/spyder-ide/spyder-notebook/pull/234) - PR: Use correct type for CONF_DEFAULTS
* [PR 232](https://github.com/spyder-ide/spyder-notebook/pull/232) - PR: Make .get_kernel_id() more robust ([213](https://github.com/spyder-ide/spyder-notebook/issues/213), [192](https://github.com/spyder-ide/spyder-notebook/issues/192))

In this release 2 pull requests were closed.


## Version 0.2.1 (2019/12/31)

This release fixes a major bug when opening or saving notebooks. Happy New Year!

### Issues Closed

* [Issue 225](https://github.com/spyder-ide/spyder-notebook/issues/225) - Trying to save Jupyter notebook crashes notebook plugin, kernel shutdown ([PR 229](https://github.com/spyder-ide/spyder-notebook/pull/229))

In this release 1 issue was closed.

### Pull Requests Merged

* [PR 229](https://github.com/spyder-ide/spyder-notebook/pull/229) - PR: Set default for recent_notebooks config value ([225](https://github.com/spyder-ide/spyder-notebook/issues/225))

In this release 1 pull request was closed.


## Version 0.2.0 (2019/12/17)

This release updates the plugin to be used with Spyder 4.

### Pull Requests Merged

* [PR 218](https://github.com/spyder-ide/spyder-notebook/pull/218) - PR: Compatibility changes for Spyder 4

In this release 1 pull request was closed.


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
