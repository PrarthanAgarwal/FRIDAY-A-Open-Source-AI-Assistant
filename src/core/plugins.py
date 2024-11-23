from typing import Dict, Type, Protocol
from pathlib import Path
import importlib.util
import inspect

class PluginProtocol(Protocol):
    name: str
    async def execute(self, *args, **kwargs): ...

class PluginManager:
    def __init__(self):
        self.plugins: Dict[str, Type[PluginProtocol]] = {}
        
    async def load_plugins(self, plugin_dir: Path):
        for plugin_file in plugin_dir.glob("*.py"):
            if plugin_file.stem.startswith("__"):
                continue
            
            spec = importlib.util.spec_from_file_location(
                plugin_file.stem, plugin_file
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and 
                        hasattr(obj, "execute") and 
                        hasattr(obj, "name")):
                        self.plugins[obj.name] = obj 