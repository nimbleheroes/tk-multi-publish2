import sgtk
import random
from sgtk.platform.qt import QtCore, QtGui

logger = sgtk.platform.get_logger(__name__)


class PluginUIStack(object):

    def __init__(self, plugin=None, parent=None):
        """
        A container that keeps a tree of UIs so that
        they can remain persistent

        Args:
            plugin_name (str, optional): Name of the plugin that this object is storing widgets for. Defaults to None.
            parent (PluginWindows, optional): Main holder for all plugin UI stacks. Defaults to None.
        """
        self._name = None
        self.plugin = plugin
        self.name = self.plugin.name
        self.parent = parent

        self.instances = {}

        self.stack = QtGui.QStackedWidget()

    @property
    def plugin_custom_widget(self):
        """
        Returns a custom widget defined for the given plugin. 

        Returns:
            QWidget: instance of plugin-hook-defined Qt settings Widget
        """
        return self.plugin.run_create_settings_widget(
            self.parent.publish_dialog.ui.task_settings_parent, None)

    def set_id(self, id):
        """
        If there is no UI created and registered for the given plugin task,
        it creates and registers one to this stack. 
        Either way it sets the stack to the desired widget.

        Args:
            id (str): UUID of the publish-item 
        """
        if id not in self.instances.keys():
            # make a new instance of the UI
            self.instances[id] = self.plugin_custom_widget
            self.stack.addWidget(self.instances[id])

        # set the stack to view the requested id's UI
        self.stack.setCurrentWidget(self.instances[id])

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value


class PluginWindows(object):

    def __init__(self):
        """
        A container for all plugins that utilize a custom-ui.
        If a plugin uses a custom UI, the instance of it will be tracked
        with the other instances of it. 
        """
        self._plugins = {}
        self.publish_dialog = None

    def __getitem__(self, value):
        return self._plugins.get(value)

    def get_plugin(self, plugin):
        assert hasattr(plugin, "name")
        name = plugin.name
        if name not in self._plugins.keys():
            self._plugins[plugin.name] = PluginUIStack(plugin, parent=self)
        return self._plugins.get(name)

    def track_plugin_item(self, publish_tasks, dialog=None):

        if not self.publish_dialog:
            self.publish_dialog = dialog

        # self._current_tasks._items[0]
        assert hasattr(publish_tasks, "_items")
        assert hasattr(publish_tasks, "plugin")

        plugin = publish_tasks.plugin
        publish_task = publish_tasks._items[0]

        assert hasattr(publish_task,
                       "item"), "Plugin task must be attached to an item."
        assert hasattr(publish_task, "name"), "Plugin task must have a name."

        publish_item = publish_task.item
        plugin_name = publish_task.name

        plugin_stack = self.get_plugin(plugin)

        if not self.publish_dialog.ui.task_settings.widget:
            self.publish_dialog.ui.task_settings.widget = plugin_stack.stack

        publish_task_id = publish_item.properties.get(plugin_name)
        import uuid
        if not publish_task_id:
            publish_task_id = str(uuid.uuid4())
            publish_item.properties[plugin_name] = publish_task_id

        self.get_plugin(plugin).set_id(publish_task_id)

        logger.debug(publish_task_id)

        return publish_task_id
