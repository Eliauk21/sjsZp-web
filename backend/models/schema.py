"""
数据模型定义
"""
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class Shop:
    """店铺模型"""
    shopId: str
    shopName: str
    templateId: Optional[str] = None
    orderId: Optional[str] = None


@dataclass
class Module:
    """模块模型"""
    name: str
    fileName: str
    isMemberCard: bool
    img: str


@dataclass
class TaskRecord:
    """任务记录模型"""
    task_id: str
    task_name: str
    operation: str
    shop_count: int
    status: str  # success, failed, running
    start_time: str
    end_time: Optional[str] = None
    log: str = ""
