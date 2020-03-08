#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tool to easily manage project assets
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import artellapipe

# Defines ID of the tool
TOOL_ID = 'artellapipe-tools-assetsmanager'

# We skip the reloading of this module when launching the tool
no_reload = True


class AssetsManagerTool(artellapipe.Tool, object):
    def __init__(self, *args, **kwargs):
        super(AssetsManagerTool, self).__init__(*args, **kwargs)

    @classmethod
    def config_dict(cls, file_name=None):
        base_tool_config = artellapipe.Tool.config_dict(file_name=file_name)
        tool_config = {
            'name': 'Assets Manager',
            'id': 'artellapipe-tools-assetsmanager',
            'logo': 'assetsmanager_logo',
            'icon': 'control_panel',
            'tooltip': 'Tool to easily manage project assets',
            'tags': ['assets', 'manager'],
            'sentry_id': 'https://503219603a654de1a4f34d677816a592@sentry.io/1764558',
            'is_checkable': False,
            'is_checked': False,
            'import_order': ['widgets', 'core'],
            'menu_ui': {'label': 'Assets Manager', 'load_on_startup': False, 'color': '', 'background_color': ''},
            'menu': [
                {'label': 'Assets',
                 'type': 'menu', 'children': [{'id': 'artellapipe-tools-assetsmanager', 'type': 'tool'}]}],
            'shelf': [
                {'name': 'Assets',
                 'children': [{'id': 'artellapipe-tools-assetsmanager', 'display_label': False, 'type': 'tool'}]}
            ]
        }
        base_tool_config.update(tool_config)

        return base_tool_config


class AssetsManagerToolset(artellapipe.Toolset, object):
    ID = TOOL_ID

    def __init__(self, *args, **kwargs):
        super(AssetsManagerToolset, self).__init__(*args, **kwargs)

        self._auto_start_assets_viewer = kwargs.pop('auto_start_assets_viewer', True)

    def contents(self):

        from artellapipe.tools.assetsmanager.widgets import assetsmanager

        assets_manager = assetsmanager.ArtellaAssetsManager(
            project=self._project, config=self._config, settings=self._settings, parent=self,
            auto_start_assets_viewer=self._auto_start_assets_viewer)
        return [assets_manager]
