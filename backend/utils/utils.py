from datetime import datetime, timezone, timedelta


def any_to_utc(dt, assume_tz='Asia/Shanghai'):
    """任意时间转换为UTC时间（使用标准库）"""
    if dt.tzinfo is None:
        # 无时区时间，使用假设时区
        if assume_tz == 'Asia/Shanghai':
            source_tz = timezone(timedelta(hours=8))
        elif assume_tz == 'UTC':
            source_tz = timezone.utc
        else:
            # 对于其他时区，使用timedelta创建
            # 注意：这里简化处理，复杂时区建议用pytz
            source_tz = timezone.utc  # 默认UTC
        
        # 使用replace方法添加时区（不是localize）
        dt = dt.replace(tzinfo=source_tz)
    
    # 转换为UTC
    return dt.astimezone(timezone.utc)

class WechatPayResult:
    SUCCESS = 'SUCCESS'
    NOTPAY = 'NOTPAY'
    
class PaymentMethod:
    ALIPAY = 'alipay'
    WECHAT = 'wechat'
    
class OrderStatus:
    """订单状态常量组"""
    # 基础状态
    UNPAID = 'unpaid'        # 未支付
    PENDING = 'pending'      # 支付中
    PAID = 'paid'            # 支付成功
    FAILED = 'failed'         # 支付失败
    EXPIRED = 'expired'       # 已过期
    CLOSED = 'closed'        # 已关闭
    # 退款状态
    REFUNDING = 'refunding'   # 退款中
    REFUNDED = 'refunded'     # 已退款
    
    # 获取所有状态
    @classmethod
    def all_statuses(cls):
        """返回所有状态"""
        return [v for k, v in cls.__dict__.items() 
                if not k.startswith('_') and isinstance(v, str)]
    
    @classmethod
    def is_valid_status(cls, status):
        """验证状态是否有效"""
        return status in cls.all_statuses()

__all__ = ['OrderStatus','PaymentMethod','WechatPayResult']