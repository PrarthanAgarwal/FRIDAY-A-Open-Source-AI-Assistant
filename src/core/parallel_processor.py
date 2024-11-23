from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import asyncio
import torch
from typing import Any, Callable, Coroutine, TypeVar, List
from loguru import logger

T = TypeVar('T')

class ParallelProcessor:
    def __init__(self, max_workers: int = None):
        self.thread_executor = ThreadPoolExecutor(max_workers=max_workers)
        self.process_executor = ProcessPoolExecutor(max_workers=max_workers)
        self.gpu_semaphore = asyncio.Semaphore(2)  # Limit concurrent GPU operations
        
    async def run_cpu_bound(self, func: Callable[..., T], *args, **kwargs) -> T:
        return await asyncio.get_event_loop().run_in_executor(
            self.process_executor, 
            func, 
            *args
        )
    
    async def run_io_bound(self, func: Callable[..., T], *args, **kwargs) -> T:
        return await asyncio.get_event_loop().run_in_executor(
            self.thread_executor, 
            func, 
            *args
        )
    
    async def run_gpu_bound(self, func: Callable[..., T], *args, **kwargs) -> T:
        async with self.gpu_semaphore:
            try:
                torch.cuda.empty_cache()
                return await asyncio.get_event_loop().run_in_executor(
                    self.thread_executor,
                    func,
                    *args
                )
            finally:
                torch.cuda.empty_cache()

    async def run_parallel(self, tasks: List[Coroutine]) -> List[Any]:
        return await asyncio.gather(*tasks)
    
    def cleanup(self):
        self.thread_executor.shutdown(wait=True)
        self.process_executor.shutdown(wait=True) 