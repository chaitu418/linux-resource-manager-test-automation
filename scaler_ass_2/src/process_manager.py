"""
Mock Process Resource Manager for Linux Process Management System
"""
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Optional, List
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

app = FastAPI(title="Linux Process Resource Manager")

class ResourceClass(str, Enum):
    CRITICAL = "CRITICAL"
    STANDARD = "STANDARD"
    BEST_EFFORT = "BEST_EFFORT"

class ProcessState(str, Enum):
    RUNNING = "RUNNING"
    IDLE = "IDLE"
    TERMINATED = "TERMINATED"

class ResourceLimits(BaseModel):
    cpu_share_percent: int  # cgroups CPU controller
    memory_limit_mb: int    # cgroups memory controller
    max_file_descriptors: int  # ulimit -n
    max_processes: int      # ulimit -u
    io_weight: int          # cgroups I/O controller

class ResourceUsage(BaseModel):
    cpu_percent: float = 0.0
    memory_mb: int = 0
    open_file_descriptors: int = 0
    process_count: int = 1
    io_operations: int = 0
    high_cpu_duration_minutes: int = 0  # Track how long CPU has been high
    low_cpu_duration_minutes: int = 0   # Track how long CPU has been low

class ProcessMetadata(BaseModel):
    process_id: str
    name: str
    command: str
    resource_class: ResourceClass = ResourceClass.STANDARD
    state: ProcessState = ProcessState.RUNNING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    uptime_seconds: int = 0
    limits: ResourceLimits
    usage: ResourceUsage = Field(default_factory=ResourceUsage)

    def is_system_process(self) -> bool:
        """Check if this is a system process."""
        return "_SYSTEM_" in self.name.upper()

    def is_database_process(self) -> bool:
        """Check if this is a database process."""
        name_upper = self.name.upper()
        return any(db in name_upper for db in ["POSTGRES", "MYSQL", "MONGODB", "REDIS"])

    def should_downgrade(self) -> bool:
        """Check if process should be downgraded based on CPU usage."""
        # System processes never downgrade
        if self.is_system_process():
            return False

        # High CPU for 5+ minutes → downgrade to BEST_EFFORT
        if self.usage.cpu_percent > 80 and self.usage.high_cpu_duration_minutes >= 5:
            return True

        # Low CPU for 10+ minutes → downgrade one class
        if self.usage.cpu_percent < 20 and self.usage.low_cpu_duration_minutes >= 10:
            return True

        return False

    def should_upgrade(self) -> bool:
        """Check if process should be upgraded."""
        # Only BEST_EFFORT processes can auto-upgrade
        if self.resource_class != ResourceClass.BEST_EFFORT:
            return False

        # System processes should be CRITICAL
        if self.is_system_process():
            return True

        # Active processes (>50% CPU) upgrade to STANDARD
        if self.usage.cpu_percent > 50:
            return True

        return False

# Resource limits for each class
RESOURCE_CLASS_LIMITS = {
    ResourceClass.CRITICAL: ResourceLimits(
        cpu_share_percent=80,
        memory_limit_mb=8192,  # 8GB
        max_file_descriptors=65535,
        max_processes=4096,
        io_weight=1000
    ),
    ResourceClass.STANDARD: ResourceLimits(
        cpu_share_percent=50,
        memory_limit_mb=2048,  # 2GB
        max_file_descriptors=8192,
        max_processes=1024,
        io_weight=500
    ),
    ResourceClass.BEST_EFFORT: ResourceLimits(
        cpu_share_percent=20,
        memory_limit_mb=512,   # 512MB
        max_file_descriptors=1024,
        max_processes=256,
        io_weight=100
    )
}

# In-memory storage for demo purposes
processes: Dict[str, ProcessMetadata] = {}

def get_resource_limits(resource_class: ResourceClass, is_database: bool = False) -> ResourceLimits:
    """Get resource limits for a given class, with special handling for databases."""
    limits = RESOURCE_CLASS_LIMITS[resource_class].model_copy()

    # Database processes get 2x memory
    if is_database:
        limits.memory_limit_mb *= 2

    return limits

class CreateProcessRequest(BaseModel):
    name: str
    command: str
    resource_class: ResourceClass = ResourceClass.STANDARD

class UpdateUsageRequest(BaseModel):
    cpu_percent: float
    memory_mb: int
    duration_minutes: int = 0

@app.post("/processes", response_model=ProcessMetadata, status_code=status.HTTP_201_CREATED)
async def create_process(request: CreateProcessRequest):
    """Create a new managed process."""
    process_id = str(uuid.uuid4())

    # Validate process name
    if not request.name or len(request.name) == 0:
        raise HTTPException(status_code=400, detail="Process name cannot be empty")

    # Validate command
    if not request.command or len(request.command) == 0:
        raise HTTPException(status_code=400, detail="Process command cannot be empty")

    # System processes must be CRITICAL
    is_system = "_SYSTEM_" in request.name.upper()
    is_database = any(db in request.name.upper() for db in ["POSTGRES", "MYSQL", "MONGODB", "REDIS"])

    resource_class = ResourceClass.CRITICAL if is_system else request.resource_class
    limits = get_resource_limits(resource_class, is_database)

    now = datetime.utcnow()
    metadata = ProcessMetadata(
        process_id=process_id,
        name=request.name,
        command=request.command,
        resource_class=resource_class,
        state=ProcessState.RUNNING,
        created_at=now,
        last_updated=now,
        uptime_seconds=0,
        limits=limits,
        usage=ResourceUsage()
    )

    processes[process_id] = metadata
    return metadata

@app.get("/processes/{process_id}", response_model=ProcessMetadata)
async def get_process(process_id: str):
    """Get process details."""
    if process_id not in processes:
        raise HTTPException(status_code=404, detail="Process not found")

    process = processes[process_id]

    # Update uptime
    if process.state == ProcessState.RUNNING:
        process.uptime_seconds = int((datetime.utcnow() - process.created_at).total_seconds())

    return process

@app.get("/processes/{process_id}/resources")
async def get_process_resources(process_id: str):
    """Get detailed resource usage for a process."""
    if process_id not in processes:
        raise HTTPException(status_code=404, detail="Process not found")

    process = processes[process_id]

    # Calculate utilization percentages
    utilization = {
        "cpu_utilization": f"{(process.usage.cpu_percent / 100.0) * 100:.1f}%",
        "memory_utilization": f"{(process.usage.memory_mb / process.limits.memory_limit_mb) * 100:.1f}%",
        "fd_utilization": f"{(process.usage.open_file_descriptors / process.limits.max_file_descriptors) * 100:.1f}%",
        "process_utilization": f"{(process.usage.process_count / process.limits.max_processes) * 100:.1f}%"
    }

    return {
        "process_id": process_id,
        "resource_class": process.resource_class,
        "limits": process.limits,
        "usage": process.usage,
        "utilization": utilization
    }

@app.delete("/processes/{process_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_process(process_id: str):
    """Terminate a process."""
    if process_id not in processes:
        raise HTTPException(status_code=404, detail="Process not found")

    process = processes[process_id]
    process.state = ProcessState.TERMINATED
    process.last_updated = datetime.utcnow()

    # Remove from active processes
    processes.pop(process_id, None)

    return None

@app.post("/admin/rebalance")
async def rebalance_resources():
    """Trigger resource rebalancing based on usage patterns."""
    upgrades = 0
    downgrades = 0

    for process_id, process in list(processes.items()):
        if process.state == ProcessState.TERMINATED:
            continue

        original_class = process.resource_class

        # Check for upgrades first (higher priority)
        if process.should_upgrade():
            if process.is_system_process():
                process.resource_class = ResourceClass.CRITICAL
            elif process.resource_class == ResourceClass.BEST_EFFORT:
                process.resource_class = ResourceClass.STANDARD

            if process.resource_class != original_class:
                upgrades += 1

        # Then check for downgrades
        elif process.should_downgrade():
            if process.usage.cpu_percent > 80 and process.usage.high_cpu_duration_minutes >= 5:
                # High CPU → BEST_EFFORT
                process.resource_class = ResourceClass.BEST_EFFORT
                downgrades += 1
            elif process.usage.cpu_percent < 20 and process.usage.low_cpu_duration_minutes >= 10:
                # Low CPU → downgrade one class
                if process.resource_class == ResourceClass.CRITICAL:
                    process.resource_class = ResourceClass.STANDARD
                    downgrades += 1
                elif process.resource_class == ResourceClass.STANDARD:
                    process.resource_class = ResourceClass.BEST_EFFORT
                    downgrades += 1

        # Update limits if class changed
        if process.resource_class != original_class:
            process.limits = get_resource_limits(process.resource_class, process.is_database_process())
            process.last_updated = datetime.utcnow()

    return {
        "status": "success",
        "processes_rebalanced": upgrades + downgrades,
        "upgrades": upgrades,
        "downgrades": downgrades
    }

@app.get("/admin/stats")
async def get_stats():
    """Get system statistics."""
    stats = {
        "total_processes": len(processes),
        "by_class": {
            resource_class.value: {
                "count": 0,
                "total_cpu_usage": 0.0,
                "total_memory_mb": 0
            }
            for resource_class in ResourceClass
        },
        "by_state": {
            state.value: 0
            for state in ProcessState
        }
    }

    for process in processes.values():
        class_stats = stats["by_class"][process.resource_class.value]
        class_stats["count"] += 1
        class_stats["total_cpu_usage"] += process.usage.cpu_percent
        class_stats["total_memory_mb"] += process.usage.memory_mb

        stats["by_state"][process.state.value] += 1

    return stats

@app.post("/admin/processes/{process_id}/update-usage")
async def update_process_usage(process_id: str, request: UpdateUsageRequest):
    """Update resource usage for a process (testing only)."""
    if process_id not in processes:
        raise HTTPException(status_code=404, detail="Process not found")

    process = processes[process_id]

    # Update usage
    process.usage.cpu_percent = request.cpu_percent
    process.usage.memory_mb = request.memory_mb

    # Track CPU duration
    if request.cpu_percent > 80:
        process.usage.high_cpu_duration_minutes = request.duration_minutes
        process.usage.low_cpu_duration_minutes = 0
    elif request.cpu_percent < 20:
        process.usage.low_cpu_duration_minutes = request.duration_minutes
        process.usage.high_cpu_duration_minutes = 0
    else:
        # Reset both if CPU is in normal range
        process.usage.high_cpu_duration_minutes = 0
        process.usage.low_cpu_duration_minutes = 0

    # Validate resource limits
    if process.usage.memory_mb > process.limits.memory_limit_mb:
        # In real system, this would trigger OOM killer
        raise HTTPException(
            status_code=400,
            detail=f"Memory usage {request.memory_mb}MB exceeds limit {process.limits.memory_limit_mb}MB"
        )

    process.last_updated = datetime.utcnow()

    return {
        "status": "success",
        "process_id": process_id,
        "usage": process.usage
    }

def start_service():
    """Start the process manager service."""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    start_service()
