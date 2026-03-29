/**
 * 数据类型定义
 */

// 店铺
export interface Shop {
  shopId: string;
  shopName: string;
  templateId: string | null;
  orderId: string | null;
}

// 模块
export interface Module {
  name: string;
  fileName: string;
  isMemberCard: boolean;
  img: string;
}

// 任务记录
export interface TaskRecord {
  task_id: string;
  task_name: string;
  operation: string;
  shop_count: number;
  status: 'success' | 'failed' | 'running';
  start_time: string;
  end_time: string | null;
  log: string[];
  result?: any;
}

// 系统设置
export interface Settings {
  wechat_webhook: string;
}
