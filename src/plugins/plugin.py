#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Author: Bugfix<tanjelly@gmail.com
Created: 2019-12-11
MOdified: 2019-12-11
'''

import os
import sys
import traceback

from imp import load_module, \
                find_module
import importlib

class Plugin(object):
    """
    过滤插件基类
    """

    __pluginPath = 'plugins'
    # 插件配置，参见 $ROOT/config/plugin.conf
    # 对应每个插件的配置以文件名作为节点名（不含.py)
    _config = None
    
    @staticmethod
    def loadPluginsConfig(rootdir, debug=False):
        """
        载入所有插件配置信息
        :param rootdir: 应用根目录
        :param debug: 调试开关
        :return: 插件配置字典
        """
        fp = None
        try:
            fp = open(os.path.join(rootdir, 'config', 'plugin.yml'), encoding='utf-8')

            import yaml
            config = yaml.load(fp, Loader=yaml.SafeLoader)
            del(yaml)
            return config
        except:
            if debug: print('[-] ERROR:\n' + traceback.format_exc())
        finally:
            if fp: fp.close()
        return {}

    @staticmethod
    def loadPlugins(rootdir, debug=False):
        """
        载入所有可用插件
        :param rootdir: 应用根路径
        :param debug: 调试开关
        """
        pluginPath = os.path.join(rootdir, Plugin.__pluginPath)
        if not os.path.isdir(pluginPath):
            raise EnvironmentError('%s is not a directory' % pluginPath)

        # 将插件路径加入环境变量
        sys.path.insert(0, pluginPath)
        # 读取插件配置
        pluginConfigs = Plugin.loadPluginsConfig(rootdir, debug)
        
        plugins = {}
        for pluginName in pluginConfigs:
            # 插件是否启用
            if 'enable' not in pluginConfigs[pluginName] or not pluginConfigs[pluginName].pop('enable'):
                continue
            
            # 插件的处理顺序
            index = -1
            if 'index' in pluginConfigs[pluginName]: index = pluginConfigs[pluginName].pop('index')

            # 插件文件是否存在
            pluginFile = os.path.join(pluginPath, '{}.py'.format(pluginName))
            if not os.path.isfile(pluginFile):
                if debug: print('[!] Failed to load plugin {}. file not found.'.format(pluginName))
                continue

            # 插件加载
            try:
                plugin_spec = importlib.util.spec_from_file_location(pluginName, pluginFile)
                if plugin_spec:
                    plugin = importlib.util.module_from_spec(plugin_spec)
                    plugin_spec.loader.exec_module(plugin)
                    if hasattr(plugin, 'FilterPlugin'):
                        if hasattr(plugin.FilterPlugin, 'execute'):
                            plugins[index] = (pluginName, plugin.FilterPlugin(rootdir, debug))
                            if pluginConfigs[pluginName]:
                                plugins[index][1].set_config(pluginConfigs[pluginName])
                        else:
                            if debug: print('[!] `execute()` method not found in Plugin {}.'.format(pluginName))
                    else:
                        if debug: print('[!] Invalid plugin {}'.format(pluginName))
            except Exception as e:
                if debug:
                    print('[-] ERROR: {}'.format(str(e)))
                    print('[-] ERROR: {}'.format(traceback.format_exc()))
        # items = os.listdir(pluginPath)
        # for item in items:
        #     if os.path.isfile(os.path.join(pluginPath, item)):
        #         if item.endswith('.py') and item not in ['__init__.py', 'plugin.py']:
        #             moduleName = item[:-3]
                    
        #             try:
        #                 module_spec = importlib.util.spec_from_file_location(moduleName, os.path.join(pluginPath, item))
        #                 if module_spec:
        #                     plugin = importlib.util.module_from_spec(module_spec)
        #                     module_spec.loader.exec_module(plugin)
        #                     if hasattr(plugin, 'FilterPlugin'):
        #                         if hasattr(plugin.FilterPlugin, 'execute'):
        #                             plugins[plugin.__name__] = plugin.FilterPlugin(rootdir, debug)
        #                             if plugin.__name__ in pluginConfigs:
        #                                 if debug: print('[!] Plugin config loaded:\n{}'.format(str(pluginConfigs[plugin.__name__])))
        #                                 plugins[plugin.__name__].set_config(pluginConfigs[plugin.__name__])
        #                         else:
        #                             if debug: print('[!] `execute()` method not found in Plugin {}.'.format(plugin.__name__))
        #                     else:
        #                         if debug: print('[!] Invalid plugin {}'.format(plugin.__name__))
        #             except Exception as e:
        #                 if debug:
        #                     print('[-] ERROR: {}'.format(str(e)))
        #                     print('[-] ERROR: {}'.format(traceback.format_exc()))
        
        if debug:
            print('[!] Loaded Plugins:')
            for i in plugins:
                print('[!] - {}'.format(plugins[i][0]))
        
        return plugins

    def __init__(self, rootdir, debug=False):
        """
        初始化
        :param rootdir: 应用根目录
        :param debug: 调式开关
        """
        self._rootdir = rootdir
        self._debug = debug

    def remain_cmd_len(self, cmd):
        """
        获取剩余的命令行长度
        :param cmd: 命令行片段
        :return: 剩余可用命令行字符串长度
        """
        if os.name == 'nt': # Windows
            return 4096 - len(cmd)
        else: # CentOS/Ubuntu
            return 2097136 - len(cmd)

    def cmd_encode(self, str):
        """
        转义命令行的引号，防止命令注入
        :param str: 要编码的字符串
        :return: 编码后的字符串
        """
        return str.replace('\\', '\\\\').replace('"', '\"')

    def log(self, msg, level = 'INFO'):
        """日志输出"""
        if self._debug: print('[!][{}][{}] {}'.format(level, self.__class__.__module__, msg))

    def set_config(self, config):
        """
        设置插件配置，配置为字典形式，例如：{ "参数名": 参数值 }
        :param config: 参数字典
        """
        self._config = config

    def execute(self, msg, workdir, debug=False):
        """
        插件入口函数，根据插件的功能对 msg 进行处理
        :param msg: 需要处理的消息
        :param workdir: 应用主目录路径
        :param debug: 是否开启调试模式
        :return: 返回需要更新的消息字典（不含原始消息）
        """
        print('Please implement the execute() function for plugin {}.'.format(self.__class__.__name__))
        return None
