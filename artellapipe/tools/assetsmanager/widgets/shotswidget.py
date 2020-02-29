#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains widget implementation for sequences manager widget
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import logging.config

from Qt.QtCore import *
from Qt.QtWidgets import *

from tpDcc.libs.qt.core import base
# from tpDcc.libs.qt.widgets import stack, label

import artellapipe
# from artellapipe.widgets import spinner

LOGGER = logging.getLogger()


# class SequencesManager(base.BaseWidget, object):
#     def __init__(self, parent=None):
#         super(SequencesManager, self).__init__(parent=parent)
#
#         self._current_sequence = None
#
#     def get_main_layout(self):
#         main_layout = QHBoxLayout()
#         main_layout.setContentsMargins(0, 0, 0, 0)
#         main_layout.setSpacing(0)
#
#         return main_layout
#
#     def ui(self):
#         super(SequencesManager, self).ui()
#
#         splitter = QSplitter(Qt.Horizontal)
#         self.main_layout.addWidget(splitter)
#
#         bg_widget = SequencesManagerBackground()
#         wait_widget = SequenceManagerWaiting()
#         self._sequences_list = QListWidget()
#         self._shots_list = QListWidget()
#         self._shots_stack = stack.SlidingStackedWidget(parent=self)
#
#         self._shots_stack.addWidget(bg_widget)
#         self._shots_stack.addWidget(wait_widget)
#         self._shots_stack.addWidget(self._shots_list)
#
#         splitter.addWidget(self._sequences_list)
#         splitter.addWidget(self._shots_stack)
#
#         shots_widget = QWidget()
#         shots_layout = QVBoxLayout()
#         shots_layout.setContentsMargins(2, 2, 2, 2)
#         shots_layout.setSpacing(2)
#         shots_widget.setLayout(shots_layout)
#         splitter.addWidget(shots_widget)
#
#
# class SequencesManagerBackground(QFrame, object):
#     def __init__(self, parent=None):
#         super(SequencesManagerBackground, self).__init__(parent)
#
#         self.setStyleSheet(
#         "#background {border-radius: 3px;border-style: solid;border-width: 1px;border-color: rgb(32,32,32);}")
#         self.setFrameShape(QFrame.StyledPanel)
#         self.setFrameShadow(QFrame.Raised)
#
#         main_layout = QVBoxLayout()
#         main_layout.setContentsMargins(0, 0, 0, 0)
#         main_layout.setSpacing(0)
#         self.setLayout(main_layout)
#
#         lbl_layout = QHBoxLayout()
#         lbl_layout.addItem(QSpacerItem(0, 20, QSizePolicy.Expanding, QSizePolicy.Fixed))
#         self.thumbnail_label = label.ThumbnailLabel()
#         self.thumbnail_label.setMinimumSize(QSize(80, 55))
#         self.thumbnail_label.setMaximumSize(QSize(80, 55))
#         self.thumbnail_label.setStyleSheet('')
#         self.thumbnail_label.setPixmap(resource.ResourceManager().pixmap('solstice_logo', category='images'))
#         self.thumbnail_label.setScaledContents(False)
#         self.thumbnail_label.setAlignment(Qt.AlignCenter)
#         lbl_layout.addWidget(self.thumbnail_label)
#         lbl_layout.addItem(QSpacerItem(0, 20, QSizePolicy.Expanding, QSizePolicy.Fixed))
#
#         main_layout.addItem(QSpacerItem(0, 20, QSizePolicy.Fixed, QSizePolicy.Expanding))
#         main_layout.addLayout(lbl_layout)
#         main_layout.addItem(QSpacerItem(0, 20, QSizePolicy.Fixed, QSizePolicy.Expanding))
#
#
# class SequenceManagerWaiting(QFrame, object):
#     def __init__(self, parent=None):
#         super(SequenceManagerWaiting, self).__init__(parent)
#
#         self.setStyleSheet(
#         "#background {border-radius: 3px;border-style: solid;border-width: 1px;border-color: rgb(32,32,32);}")
#         self.setFrameShape(QFrame.StyledPanel)
#         self.setFrameShadow(QFrame.Raised)
#
#         main_layout = QVBoxLayout()
#         main_layout.setContentsMargins(0, 0, 0, 0)
#         main_layout.setSpacing(0)
#         self.setLayout(main_layout)
#
#         self.wait_spinner = spinner.WaitSpinner(spinner_type=spinner.SpinnerType.Loading)
#         self.wait_spinner.bg.setFrameShape(QFrame.NoFrame)
#         self.wait_spinner.bg.setFrameShadow(QFrame.Plain)
#
#         main_layout.addItem(QSpacerItem(0, 20, QSizePolicy.Fixed, QSizePolicy.Expanding))
#         main_layout.addWidget(self.wait_spinner)
#         main_layout.addItem(QSpacerItem(0, 20, QSizePolicy.Fixed, QSizePolicy.Expanding))


class ShotsWidget(base.BaseWidget, object):

    shotAdded = Signal(object)

    def __init__(self, project, show_viewer_menu=False, parent=None):

        self._project = project
        self._show_viewer_menu = show_viewer_menu
        if not self._project:
            LOGGER.warning('Invalid project for SequencesWidget!')

        super(ShotsWidget, self).__init__(parent=parent)

    def get_main_layout(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        return main_layout

    def ui(self):
        super(ShotsWidget, self).ui()

        self._shots_viewer = artellapipe.ShotsViewer(
            project=self._project, show_context_menu=self._show_viewer_menu, parent=self)
        self._shots_viewer.first_empty_cell()

        self.main_layout.addWidget(self._shots_viewer)

    def setup_signals(self):
        self._shots_viewer.shotAdded.connect(self.shotAdded.emit)

    def update_shots(self):
        """
        Updates the list of sequences in the sequences viewer
        """

        self._shots_viewer.update_shots()
