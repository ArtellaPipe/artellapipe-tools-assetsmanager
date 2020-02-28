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


class AssetsManagerToolset(artellapipe.Toolset, object):
    ID = TOOL_ID

    def __init__(self, *args, **kwargs):
        super(AssetsManagerToolset, self).__init__(*args, **kwargs)

    def contents(self):

        from artellapipe.tools.assetsmanager.widgets import assetsmanager

        assets_manager = assetsmanager.ArtellaAssetsManager(project=self._project, config=self._config)
        return [assets_manager]
