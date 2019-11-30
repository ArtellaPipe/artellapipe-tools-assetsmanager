#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tool that allow artists to interact with Artella functionality inside DCCS
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import logging
from functools import partial

from Qt.QtCore import *
from Qt.QtWidgets import *

from tpQtLib.core import qtutils, base
from tpQtLib.widgets import splitters, stack

import artellapipe
from artellapipe.utils import resource, worker
from artellapipe.widgets import waiter
from artellapipe.core import defines
from artellapipe.tools.assetsmanager.widgets import assetswidget

LOGGER = logging.getLogger()


class ArtellaAssetsManager(artellapipe.Tool, object):

    ASSET_WIDGET_CLASS = assetswidget.AssetsWidget

    def __init__(self, project, config, auto_start_assets_viewer=True):

        self._artella_worker = worker.Worker(app=QApplication.instance())
        self._artella_worker.workCompleted.connect(self._on_artella_worker_completed)
        self._artella_worker.workFailure.connect(self._on_artella_worker_failed)
        self._artella_worker.start()

        self._is_blocked = False
        self._asset_to_sync = None

        super(ArtellaAssetsManager, self).__init__(project=project, config=config)

        if auto_start_assets_viewer:
            self._assets_widget.update_assets()

    def get_main_layout(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.setAlignment(Qt.AlignTop)

        return main_layout

    def ui(self):
        super(ArtellaAssetsManager, self).ui()

        # Create Top Menu Bar
        self._menu_bar = self._setup_menubar()
        if not self._menu_bar:
            self._menu_bar = QMenuBar(self)
        self.main_layout.addWidget(self._menu_bar)
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFrameShadow(QFrame.Raised)
        self.main_layout.addWidget(sep)

        self._main_stack = stack.SlidingStackedWidget(parent=self)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._attrs_stack = stack.SlidingStackedWidget(parent=self)

        no_items_widget = QFrame()
        no_items_widget.setFrameShape(QFrame.StyledPanel)
        no_items_widget.setFrameShadow(QFrame.Sunken)
        no_items_layout = QVBoxLayout()
        no_items_layout.setContentsMargins(0, 0, 0, 0)
        no_items_layout.setSpacing(0)
        no_items_widget.setLayout(no_items_layout)
        no_items_lbl = QLabel()
        no_items_pixmap = resource.ResourceManager().pixmap('no_asset_selected')
        no_items_lbl.setPixmap(no_items_pixmap)
        no_items_lbl.setAlignment(Qt.AlignCenter)
        no_items_layout.addItem(QSpacerItem(0, 10, QSizePolicy.Preferred, QSizePolicy.Expanding))
        no_items_layout.addWidget(no_items_lbl)
        no_items_layout.addItem(QSpacerItem(0, 10, QSizePolicy.Preferred, QSizePolicy.Expanding))

        self._waiter = waiter.ArtellaWaiter()

        self._user_info_layout = QVBoxLayout()
        self._user_info_layout.setContentsMargins(0, 0, 0, 0)
        self._user_info_layout.setSpacing(0)
        self._user_info_widget = QWidget()
        self._user_info_widget.setLayout(self._user_info_layout)

        self._tab_widget = QTabWidget()
        self._tab_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._tab_widget.setMinimumHeight(330)

        self._assets_widget = self.ASSET_WIDGET_CLASS(project=self._project)
        self._settings_widget = AssetsManagerSettingsWidget(settings=self.settings())

        self._tab_widget.addTab(self._assets_widget, 'Assets')
        self._tab_widget.setTabEnabled(1, False)

        self.main_layout.addWidget(self._main_stack)

        self._main_stack.addWidget(splitter)
        self._main_stack.addWidget(self._settings_widget)

        self._attrs_stack.addWidget(no_items_widget)
        self._attrs_stack.addWidget(self._waiter)
        self._attrs_stack.addWidget(self._user_info_widget)

        splitter.addWidget(self._tab_widget)
        splitter.addWidget(self._attrs_stack)

        artellapipe.Tracker().logged.connect(self._on_valid_login)

    def setup_signals(self):
        self._project_artella_btn.clicked.connect(self._on_open_project_in_artella)
        self._project_folder_btn.clicked.connect(self._on_open_project_folder)
        self._settings_btn.clicked.connect(self._on_open_settings)
        self._assets_widget.assetAdded.connect(self._on_asset_added)
        self._attrs_stack.animFinished.connect(self._on_attrs_stack_anim_finished)
        self._settings_widget.closed.connect(self._on_close_settings)

    def closeEvent(self, event):
        """
        Overrides base window.ArtellaWindow closeEvent function
        :param event: QEvent
        """

        self.save_settings()
        event.accept()

    def show_asset_info(self, asset_widget):
        """
        Shows Asset Info Widget UI associated to the given asset widget
        :param asset_widget: ArtellaAssetWidget
        """

        asset_info = asset_widget.get_asset_info()
        if not asset_info:
            LOGGER.warning(
                'Asset {} has not an AssetInfo widget associated to it. Skipping ...!'.format(asset_widget.get_name()))
            return

        self._set_asset_info(asset_info)

    def _setup_menubar(self):
        """
        Internal function used to setup Artella Manager menu bar
        """

        menubar_widget = QWidget()
        menubar_layout = QGridLayout()
        menubar_layout.setAlignment(Qt.AlignTop)
        menubar_layout.setContentsMargins(0, 0, 0, 0)
        menubar_layout.setSpacing(2)
        menubar_widget.setLayout(menubar_layout)
        self._project_artella_btn = QToolButton()
        self._project_artella_btn.setText('Artella')
        self._project_artella_btn.setIcon(resource.ResourceManager().icon('artella'))
        self._project_artella_btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self._project_folder_btn = QToolButton()
        self._project_folder_btn.setText('Project')
        self._project_folder_btn.setIcon(resource.ResourceManager().icon('folder'))
        self._project_folder_btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self._synchronize_btn = QToolButton()
        self._synchronize_btn.setText('Synchronize')
        self._synchronize_btn.setPopupMode(QToolButton.InstantPopup)
        self._synchronize_btn.setIcon(resource.ResourceManager().icon('sync'))
        self._synchronize_btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self._settings_btn = QToolButton()
        self._settings_btn.setText('Settings')
        self._settings_btn.setIcon(resource.ResourceManager().icon('settings'))
        self._settings_btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        for i, btn in enumerate(
                [self._project_artella_btn, self._project_folder_btn, self._synchronize_btn, self._settings_btn]):
            menubar_layout.addWidget(btn, 0, i, 1, 1, Qt.AlignCenter)

        self._setup_synchronize_menu()

        return menubar_widget

    def _setup_synchronize_menu(self):
        """
        Internal function that creates the synchronize menu
        """

        sync_menu = QMenu(self)
        sync_icon = resource.ResourceManager().icon('sync')

        for asset_type in artellapipe.AssetsMgr().get_asset_types():
            action_icon = resource.ResourceManager().icon(asset_type.lower())
            if action_icon:
                sync_action = QAction(action_icon, asset_type.title(), self)
            else:
                sync_action = QAction(asset_type.title(), self)
            sync_menu.addAction(sync_action)
            asset_file_types = artellapipe.AssetsMgr().get_asset_type_files(asset_type=asset_type) or list()
            if asset_file_types:
                asset_files_menu = QMenu(sync_menu)
                sync_action.setMenu(asset_files_menu)
                for asset_file_type in asset_file_types:
                    asset_type_icon = resource.ResourceManager().icon(asset_file_type)
                    asset_file_action = QAction(asset_type_icon, asset_file_type.title(), asset_files_menu)
                    asset_files_menu.addAction(asset_file_action)
                    asset_file_template = artellapipe.FilesMgr().get_template(asset_file_type)
                    if not asset_file_template:
                        LOGGER.warning('No File Template found for File Type: "{}"'.format(asset_file_type))
                        asset_file_action.setEnabled(False)
                        continue
                    asset_file_action.triggered.connect(partial(self._on_sync_file_type, asset_type, asset_file_type))
                all_asset_types_action = QAction(sync_icon, 'All', asset_files_menu)
                all_asset_types_action.triggered.connect(partial(self._on_sync_all_assets_of_type, asset_type))
                asset_files_menu.addAction(all_asset_types_action)

        sync_menu.addSeparator()
        sync_all_action = QAction(sync_icon, 'All', self)
        sync_all_action.triggered.connect(self._on_sync_all_types)
        sync_menu.addAction(sync_all_action)

        self._synchronize_btn.setMenu(sync_menu)

    def _setup_asset_signals(self, asset_widget):
        """
        Internal function that sets proper signals to given asset widget
        This function can be extended to add new signals to added items
        :param asset_widget: ArtellaAssetWidget
        """

        asset_widget.clicked.connect(self._on_asset_clicked)
        asset_widget.startSync.connect(self._on_start_asset_sync)

    def _set_asset_info(self, asset_info):
        """
        Sets the asset info widget currently being showed
        :param asset_info: AssetInfoWidget
        """

        if self._user_info_widget == asset_info:
            return

        qtutils.clear_layout(self._user_info_layout)

        if asset_info:
            self._user_info_widget = asset_info
            self._user_info_layout.addWidget(asset_info)
            self._attrs_stack.slide_in_index(2)

    def _get_asset_data_from_artella(self, data):
        """
        Internal function that starts worker to get asset data from Artella asynchronously
        :param data, dict
        """

        data.get('asset_widget').asset.get_artella_data()

        return data['asset_widget']

    def _show_asset_info(self, asset_widget):
        """
        Internal function that shows the asset info widget
        :param asset_widget: ArtellaAssetWidget
        """

        self.show_asset_info(asset_widget)
        self._is_blocked = False
        self._asset_to_sync = None
        self._attrs_stack.slide_in_index(2)

    def _on_artella_not_available(self):
        """
        Internal callback function that is called by ArtellaUserInfo widget when Artella is not available
        TODO: If Artella is not enabled we should disable all the widget of the UI and notify the user
        """

        pass

    def _on_artella_worker_completed(self, uid, asset_widget):
        """
        Internal callback function that is called when worker finishes its job
        """

        self._show_asset_info(asset_widget)

    def _on_artella_worker_failed(self, uid, msg, trace):
        """
        Internal callback function that is called when the Artella worker fails
        :param uid: str
        :param msg: str
        :param trace: str
        """

        if self._asset_to_sync:
            self._show_asset_info(self._asset_to_sync)
        else:
            self._is_blocked = False
            self._asset_to_sync = None
            self._attrs_stack.slide_in_index(0)

    def _on_attrs_stack_anim_finished(self, index):
        """
        Internal callback that is called each time slack animation finishes
        :return:
        """

        if self._asset_to_sync and index == 1:
            self._is_blocked = True
            self._artella_worker.queue_work(self._get_asset_data_from_artella, {'asset_widget': self._asset_to_sync})

    def _on_open_project_in_artella(self):
        """
        Internal callback function that is called when the user presses Artella menu bar button
        """

        if not self._project:
            return

        self._project.open_in_artella()

    def _on_open_project_folder(self):
        """
        Internal callback function that is called when the user presses Project menu bar button
        """

        if not self._project:
            return

        self._project.open_folder()

    def _on_open_settings(self):
        """
        Internal callback function that is called when settings button is clicked
        """

        if not self._settings_widget.settings:
            msg = 'No Settings to edit!'
            self.show_warning_message(msg)
            LOGGER.info(msg)
            return

        self._main_stack.slide_in_index(1)

    def _on_close_settings(self):
        """
        Internal callback function that is called when closed signal from settings widget is emitted
        """

        self._main_stack.slide_in_index(0)

    def _on_asset_added(self, asset_widget):
        """
        Internal callback function that is called when a new asset widget is added to the assets viewer
        :param asset_widget: ArtellaAssetWidget
        """

        if not asset_widget:
            return

        self._setup_asset_signals(asset_widget)

    def _on_asset_clicked(self, asset_widget, skip_sync=True):
        """
        Internal callback function that is called when an asset button is clicked
        :param asset_widget: ArtellaAssetWidget
        """

        if not asset_widget or self._is_blocked:
            return

        if skip_sync:
            self._show_asset_info(asset_widget)
        else:
            asset_data = asset_widget.asset.get_artella_data(update=False)
            if asset_data:
                self._show_asset_info(asset_widget)
            else:
                self._asset_to_sync = asset_widget
                self._attrs_stack.slide_in_index(1)

    def _on_start_asset_sync(self, asset, file_type, sync_type):
        """
        Internal callback function that is called when an asset needs to be synced
        :param asset: ArtellaAsset
        :param file_type: str
        :param sync_type: str
        """

        if not asset:
            return

        asset.sync(file_type, sync_type)

    def _on_valid_login(self):
        """
        Internal callback function that is called anytime user log in into Tracking Manager
        """

        self._assets_widget.update_assets()

    def _on_sync_file_type(self, asset_type, file_type, sync_type=defines.ArtellaFileStatus.ALL):
        """
        Internal callback function that is called when a file is selected from the sync menu
        :param file_type: str, file type to sync
        :param sync_type: ArtellaFileStatus, type of sync we want to do
        """

        assets_to_sync = artellapipe.AssetsMgr().get_assets_by_type(asset_type)
        if not assets_to_sync:
            LOGGER.warning('No Assets found of type "{}" to sync!'.format(asset_type))
            return

        for asset in assets_to_sync:
            asset.sync(file_type=file_type, sync_type=defines.ArtellaFileStatus.ALL)

        self.show_ok_message('Files of type {} has been synced!'.format(file_type))

    def _on_sync_all_assets_of_type(self, asset_type, ask=True):
        """
        Synchronizes all the assets of a given type
        :param asset_type: str
        :param ask: bol
        """

        assets_to_sync = artellapipe.AssetsMgr().get_assets_by_type(asset_type)
        if not assets_to_sync:
            LOGGER.warning('No Assets found of type "{}" to sync!'.format(asset_type))
            return

        total_assets = len(assets_to_sync)
        if ask:
            result = qtutils.show_question(
                None, 'Synchronizing All {} Assets ({})'.format(asset_type, total_assets),
                'Are you sure you want to synchronize all {} assets ({})? This can take lot of time!'.format(
                    asset_type, total_assets))
            if result == QMessageBox.No:
                return

        for asset in assets_to_sync:
            asset.sync(sync_type=defines.ArtellaFileStatus.ALL)

        self.show_ok_message('All assets have been synced!')

    def _on_sync_all_types(self, ask=True):
        """
        Synchronizes all the assets
        :param ask: bol
        """

        assets_to_sync = artellapipe.AssetsMgr().assets
        if not assets_to_sync:
            LOGGER.warning('No Assets found to sync!')
            return

        total_assets = len(assets_to_sync)
        if ask:
            result = qtutils.show_question(
                None, 'Synchronizing All Assets ({})'.format(total_assets),
                'Are you sure you want to synchronize all assets ({})? This will take lot of time!'.format(
                    total_assets))
            if result == QMessageBox.No:
                return

        for asset in assets_to_sync:
            asset.sync(sync_type=defines.ArtellaFileStatus.ALL)


class AssetsManagerSettingsWidget(base.BaseWidget, object):

    closed = Signal()

    def __init__(self, settings, parent=None):
        super(AssetsManagerSettingsWidget, self).__init__(parent=parent)

        self._settings = settings
        self._load_settings()

    def ui(self):
        super(AssetsManagerSettingsWidget, self).ui()

        self._auto_check_published_cbx = QCheckBox('Auto Check Published Versions?')
        self.main_layout.addWidget(self._auto_check_published_cbx)
        self._auto_check_working_cbx = QCheckBox('Auto Check Working Versions?')
        self.main_layout.addWidget(self._auto_check_working_cbx)
        self._auto_check_lock_cbx = QCheckBox('Check Lock/Unlock Working Versions?')
        self.main_layout.addWidget(self._auto_check_lock_cbx)

        self.main_layout.addLayout(splitters.SplitterLayout())
        self.main_layout.addItem(QSpacerItem(0, 10, QSizePolicy.Preferred, QSizePolicy.Expanding))

        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(1)
        self.main_layout.addLayout(bottom_layout)

        save_icon = resource.ResourceManager().icon('save')
        cancel_icon = resource.ResourceManager().icon('close')

        self._save_btn = QPushButton('Save')
        self._save_btn.setIcon(save_icon)
        self._cancel_btn = QPushButton('Cancel')
        self._cancel_btn.setIcon(cancel_icon)
        bottom_layout.addWidget(self._save_btn)
        bottom_layout.addWidget(self._cancel_btn)

    def setup_signals(self):
        self._save_btn.clicked.connect(self._on_save_settings)
        self._cancel_btn.clicked.connect(self._on_close_settings)

    @property
    def settings(self):
        return self._settings

    def _load_settings(self):
        """
        Internal function that updates widget status taking into account settings
        """

        if not self._settings:
            return

        try:
            auto_check_published = self._settings.getw('auto_check_published', default_value=False)
            auto_check_working = self._settings.getw('auto_check_working', default_value=False)
            auto_check_lock = self._settings.getw('auto_check_lock', default_value=False)

            print(auto_check_published, auto_check_working, auto_check_lock)
        except Exception as exc:
            LOGGER.error('Something went wrong when trying to load settings: {}'.format(exc))

    def _save_settings(self):
        """
        Internal function that saves settings taking into account current widget status
        """

        if not self._settings:
            LOGGER.warning('Impossible to save settings because they are not defined!')
            return

        self._settings.setw('auto_check_published', self._auto_check_published_cbx.isChecked())
        self._settings.setw('auto_check_working', self._auto_check_working_cbx.isChecked())
        self._settings.setw('auto_check_lock', self._auto_check_lock_cbx.isChecked())

    def _on_save_settings(self):
        """
        Internal callback function that is called when save button is pressed
        """

        try:
            self._save_settings()
        except Exception as exc:
            LOGGER.error('Something went wrong when trying to save settings: {}'.format(exc))
        self.closed.emit()

    def _on_close_settings(self):
        """
        Internal callback function that is called when close button is pressed
        """

        self.closed.emit()
