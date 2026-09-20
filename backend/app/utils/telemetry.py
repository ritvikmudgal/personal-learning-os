"""Tutor request latency profiling and performance telemetry.

Provides high-resolution timing measurements for each pipeline stage:
1. Concept Resolution
2. Learner State Retrieval
3. Prerequisite Graph Traversal
4. Library Material Retrieval
5. Context Construction
6. LLM First Token (TTFT)
7. LLM Completion
8. Evidence Processing
9. Total Request Time
"""

import time
from typing import Dict, Optional
from app.utils.logging import get_logger

logger = get_logger("telemetry.tutor")


class TutorRequestProfiler:
    """Profiler for measuring execution durations across tutor pipeline stages."""

    def __init__(self, request_id: Optional[str] = None):
        self.request_id = request_id or f"req-{int(time.time() * 1000)}"
        self.start_time = time.perf_counter()
        self.stage_starts: Dict[str, float] = {}
        self.durations: Dict[str, float] = {}

    def start_stage(self, stage_name: str) -> None:
        """Mark the start of a stage."""
        self.stage_starts[stage_name] = time.perf_counter()

    def end_stage(self, stage_name: str) -> float:
        """Mark the end of a stage and compute duration in milliseconds."""
        if stage_name not in self.stage_starts:
            return 0.0
        start = self.stage_starts.pop(stage_name)
        duration_ms = (time.perf_counter() - start) * 1000.0
        self.durations[stage_name] = duration_ms
        return duration_ms

    def log_summary(self, llm_calls_count: int = 1) -> Dict[str, float]:
        """Compute total time and log structured latency breakdown."""
        total_ms = (time.perf_counter() - self.start_time) * 1000.0
        self.durations["total_request_time"] = total_ms

        breakdown_str = " | ".join(
            [f"{k}: {v:.1f}ms" for k, v in self.durations.items() if k != "total_request_time"]
        )
        logger.info(
            "Tutor Performance Telemetry [%s] (LLM Calls: %d) -> Total: %.1fms | %s",
            self.request_id,
            llm_calls_count,
            total_ms,
            breakdown_str,
        )
        return self.durations
