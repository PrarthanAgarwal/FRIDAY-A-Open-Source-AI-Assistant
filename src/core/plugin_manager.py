from pathlib import Path
from typing import Dict, Type, Any
import importlib.util
import inspect
from loguru import logger

class PluginBase:
    """Base class for all plugins"""
    name: str = "base_plugin"
    version: str = "0.1.0"
    
    async def initialize(self) -> None:
        """Initialize plugin resources"""
        pass
    
    async def cleanup(self) -> None:
        """Cleanup plugin resources"""
        pass

class PluginManager:
    """Manages dynamic loading and lifecycle of plugins"""
    
    def __init__(self, plugin_dir: Path):
        self.plugin_dir = plugin_dir
        self.plugins: Dict[str, PluginBase] = {}
        self.active_plugins: Dict[str, bool] = {}
    
    async def load_plugins(self) -> None:
        """Dynamically load all plugins from the plugin directory"""
        for plugin_path in self.plugin_dir.glob("*.py"):
            if plugin_path.stem.startswith("_"):
                continue
                
            try:
                spec = importlib.util.spec_from_file_location(
                    plugin_path.stem, 
                    plugin_path
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Find plugin class in module
                for item_name, item in inspect.getmembers(module):
                    if (inspect.isclass(item) and 
                        issubclass(item, PluginBase) and 
                        item != PluginBase):
                        plugin = item()
                        await plugin.initialize()
                        self.plugins[plugin.name] = plugin
                        self.active_plugins[plugin.name] = True
                        logger.info(f"Loaded plugin: {plugin.name} v{plugin.version}")
                        
            except Exception as e:
                logger.error(f"Failed to load plugin {plugin_path.name}: {e}")
    
    async def unload_plugins(self) -> None:
        """Unload and cleanup all plugins"""
        for name, plugin in self.plugins.items():
            try:
                await plugin.cleanup()
                logger.info(f"Unloaded plugin: {name}")
            except Exception as e:
                logger.error(f"Error unloading plugin {name}: {e}")
        
        self.plugins.clear()
        self.active_plugins.clear() 