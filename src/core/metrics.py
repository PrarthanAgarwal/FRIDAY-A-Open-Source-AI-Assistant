from dataclasses import dataclass, field
from time import perf_counter
from typing import Dict, List
import numpy as np
from loguru import logger
import time
import statistics

@dataclass
class PerformanceMetrics:
    start_time: float = field(default_factory=perf_counter)
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    response_times: List[float] = field(default_factory=list)
    gpu_utilization: List[float] = field(default_factory=list)
    memory_usage: List[float] = field(default_factory=list)

    def add_response_time(self, time: float):
        self.response_times.append(time)
        
    def get_average_response_time(self) -> float:
        return np.mean(self.response_times) if self.response_times else 0.0

    def get_percentile_response_time(self, percentile: float) -> float:
        return np.percentile(self.response_times, percentile) if self.response_times else 0.0

    def get_summary(self) -> Dict:
        return {
            "total_requests": self.total_requests,
            "success_rate": self.successful_requests / max(self.total_requests, 1),
            "avg_response_time": self.get_average_response_time(),
            "p95_response_time": self.get_percentile_response_time(95),
            "avg_gpu_utilization": np.mean(self.gpu_utilization) if self.gpu_utilization else 0.0,
            "avg_memory_usage": np.mean(self.memory_usage) if self.memory_usage else 0.0
        }

@dataclass
class TokenizationMetrics:
    total_tokens: int = 0
    processing_times: List[float] = field(default_factory=list)

    def add_measurement(self, num_tokens: int, process_time: float):
        """Record tokenization metrics
        Args:
            num_tokens: Number of tokens processed
            process_time: Time taken in seconds
        """
        self.total_tokens += num_tokens
        self.processing_times.append(process_time)

    def get_summary(self) -> dict:
        """Get tokenization performance metrics
        Returns:
            dict: Summary statistics
        """
        if not self.processing_times:
            return {
                "total_tokens": 0,
                "avg_tokens_per_second": 0,
                "avg_process_time": 0
            }

        avg_time = statistics.mean(self.processing_times)
        return {
            "total_tokens": self.total_tokens,
            "avg_tokens_per_second": self.total_tokens / sum(self.processing_times),
            "avg_process_time": avg_time
        }

# Global metrics instance
metrics = PerformanceMetrics() 