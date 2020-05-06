#  PyMODA, a Python implementation of MODA (Multiscale Oscillatory Dynamics Analysis).
#  Copyright (C) 2019  Lancaster University
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <https://www.gnu.org/licenses/>.
import asyncio
import logging
import os
import sys
import time
from pathlib import Path

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QKeySequence
from PyQt5.QtWidgets import QMessageBox, QShortcut
from pymodalib.utils.matlab_runtime import RuntimeStatus

import updater.update as upd
import utils
from data import resources
from data.resources import get
from gui.dialogs.MatlabRuntimeDialog import MatlabRuntimeDialog
from gui.dialogs.SettingsDialog import SettingsDialog
from gui.windows.CentredWindow import CentredWindow
from updater import update
from updater.update import get_latest_commit
from utils import args
from utils.os_utils import OS
from utils.qutils import retain_size_when_hidden
from utils.settings import Settings
from utils.shortcuts import create_shortcut


class LauncherWindow(CentredWindow):
    """
    The first window that opens, providing buttons to open the important windows.
    """

    def __init__(self, parent):
        super(LauncherWindow, self).__init__(parent)

        print(
            f"Welcome to PyMODA. Please do not close this terminal window while PyMODA is running."
            f"\n\nPyMODA is running under Python {'.'.join([f'{i}' for i in sys.version_info[:3]])}.\n"
            f"Python interpreter: {sys.executable}.\n"
        )

        # Hidden shortcuts to trigger a check for updates.
        self.update_shortcut = QShortcut(QKeySequence("Ctrl+U"), self)
        self.update_shortcut.activated.connect(self.force_check_updates)
        self.update_shortcut_force = QShortcut(QKeySequence("Ctrl+Shift+U"), self)
        self.update_shortcut_force.activated.connect(self.force_show_update)

        self.pymoda_has_set_cache_var = False
        self.reload_settings()

    def setup_ui(self) -> None:
        uic.loadUi(get("layout:window_launcher.ui"), self)
        self.load_banner_images()

        self.btn_time_freq.clicked.connect(self.application.start_time_frequency)
        self.btn_wavelet_phase.clicked.connect(self.application.start_phase_coherence)
        self.btn_group_coherence.clicked.connect(self.application.start_group_coherence)
        self.btn_ridge_extraction.clicked.connect(
            self.application.start_ridge_extraction
        )
        self.btn_wavelet_bispectrum.clicked.connect(self.application.start_bispectrum)
        self.btn_dynamical_bayesian.clicked.connect(self.application.start_bayesian)

        self.btn_harmonics.clicked.connect(self.application.start_harmonics)

        self.btn_create_shortcut.clicked.connect(self.create_shortcut)
        self.check_matlab_runtime()

        self.lbl_update.hide()

        self.btn_update.hide()
        self.btn_update.clicked.connect(self.on_update_clicked)
        self.btn_settings.clicked.connect(self.on_settings_clicked)

        retain_size_when_hidden(self.btn_update)

        # combo: QComboBox = self.combo_source
        # combo.currentTextChanged.connect(self.on_update_source_changed)
        # combo.setCurrentText(self.settings.get_update_branch().capitalize())

        if args.create_shortcut():
            self.create_shortcut(silent=True)

        if args.post_update():
            asyncio.ensure_future(self.post_update())
        elif update.should_check_for_updates():
            asyncio.ensure_future(self.check_for_updates())

    def check_matlab_runtime(self) -> None:
        """
        Checks whether the LD_LIBRARY_PATH for the MATLAB Runtime is correctly passed to
        the program, and shows a dialog if appropriate.
        """
        from pymodalib.utils.matlab_runtime import get_runtime_status

        status = get_runtime_status()

        if (
            not OS.is_windows()
            and status is RuntimeStatus.NOT_EXISTS
            and not args.matlab_runtime()
            and self.settings.is_runtime_warning_enabled()
        ):
            dialog = MatlabRuntimeDialog()
            dialog.exec()

            self.settings.set_runtime_warning_enabled(not dialog.dont_show_again)
            if not dialog.dont_show_again:
                sys.exit(0)

    def reload_settings(self) -> None:
        self.settings = Settings()

        cache_var = "PYMODALIB_CACHE"
        cache = self.settings.get_pymodalib_cache()

        logging.info(
            f"PyMODAlib cache is {os.environ.get(cache_var)} in environment, {cache} in settings."
        )

        if (
            (not os.environ.get(cache_var) or self.pymoda_has_set_cache_var)
            and cache
            and cache != "None"
        ):
            self.pymoda_has_set_cache_var = True
            os.environ[cache_var] = cache

            logging.info(f"Set {cache_var} = {os.environ.get(cache_var)}")

    def load_banner_images(self) -> None:
        """
        Loads the banner images and displays them at the top of the window.
        """
        image = QPixmap(resources.get("image:physicslogo.png"))
        self.lbl_physics.setPixmap(image.scaled(600, 300, Qt.KeepAspectRatio))

    @staticmethod
    def create_shortcut(silent: bool = False) -> None:
        """
        Calls `create_shortcut()` and shows a message box with the result.
        """
        status = create_shortcut()
        if not silent:
            QMessageBox(text=status).exec()

    def on_update_source_changed(self, branch: str) -> None:
        """
        Called when the selection in the "Update source" ComboBox is changed.

        :param branch: the branch name selected as the update source
        """
        branch = branch.lower()
        self.settings.set_update_source(branch)

        asyncio.ensure_future(self.check_for_updates(force=True))

    def on_settings_clicked(self) -> None:
        """
        Called when the "Settings" button is clicked.
        """
        branch = self.settings.get_update_branch()
        SettingsDialog().run()

        self.reload_settings()
        if branch != self.settings.get_update_branch():
            self.on_update_source_changed(self.settings.get_update_branch())

    def on_update_clicked(self) -> None:
        """
        Called when the button to update is clicked.
        """
        if utils.is_frozen:
            import webbrowser

            webbrowser.open_new_tab(
                "https://github.com/luphysics/PyMODA/releases/latest"
            )
            return

        response = QMessageBox().question(
            self,
            "Update",
            "PyMODA will close and update. Please close other PyMODA windows and "
            "ensure you have no unsaved work. \n\n"
            "The current version of PyMODA will be saved in a folder named 'backup'. "
            "Old backups will be deleted.\n\n"
            "Continue?",
        )

        if QMessageBox.Yes == response:
            cwd = os.getcwd()
            root = Path(cwd).parent

            upd.start_update(root)

    async def post_update(self) -> None:
        """
        Called when the program launches after a successful update.
        """
        upd.cleanup()
        self.settings.set_update_available(False)

        # Set the latest commit to the current commit on GitHub.
        self.settings.set_latest_commit(await get_latest_commit())

        # Remove the `--post-update` argument to prevent confusion in other parts of the program.
        sys.argv.remove(update.arg_post_update)
        args.set_post_update(False)

        # After updating, we want the relaunched window to be obvious.
        # On Windows, this will make the taskbar icon flash orange.
        self.activateWindow()

        await asyncio.sleep(0.2)  # Prevent jarring animations.
        QMessageBox.information(self, "Update", "Update completed.")

        await self.check_for_updates()

    def force_check_updates(self) -> None:
        """
        Forces a check for updates. Called when the hidden shortcut is triggered.
        """
        asyncio.ensure_future(self.check_for_updates(force=True))
        print("Forcing a check for updates...")

    def force_show_update(self) -> None:
        """
        Forces PyMODA to show an available update, even if one does not exist.
        """
        self.settings.set_latest_commit("dummy-commit-hash")
        asyncio.ensure_future(self.check_for_updates(force=True))
        print("Double-forcing a check for updates...")

    async def check_for_updates(self, force=False) -> None:
        """
        Checks for updates, and takes appropriate action such as saving
        to the settings.

        :param force: whether to force an update check, even if there was a recent check
        """
        # If there was an update found the last time we checked.
        if self.settings.get_update_available_on_branch():
            self.show_update_available(True)
            print(
                f"Update is available on branch '{self.settings.get_update_branch()}'."
            )
            return

        # If we should check for updates again now.
        elif not self.settings.should_check_updates() and not force:
            self.show_update_available(False)
            print(f"Skipping a check for updates.")
            return

        # Retrieve the latest commit from the GitHub API.
        new_commit = await get_latest_commit()

        if new_commit is None:
            self.show_update_available(False)
            return

        # If it's the first ever check for updates.
        elif self.settings.get_latest_commit_on_branch() is None:
            self.settings.set_latest_commit(new_commit)
            self.show_update_available(False)

        # If there's an update available.
        elif new_commit != self.settings.get_latest_commit_on_branch():
            self.settings.set_update_available(True)
            self.show_update_available(True)
            print(
                f"Found new update on branch '{self.settings.get_update_branch()}'. Commit hash: {new_commit}"
            )

        # No updates available.
        else:
            self.settings.set_update_available(False)
            self.show_update_available(False)
            print(
                f"No updates available on branch '{self.settings.get_update_branch()}'."
            )

        # Set now as the last time at which an update check occurred.
        self.settings.set_last_update_check(time.time())

    def show_update_available(self, show: bool) -> None:
        """
        Shows that an update is available by making the button and label visible.
        """
        for item in (self.lbl_update, self.btn_update):
            item.setStyleSheet("color: blue;")
            item.setVisible(show)
