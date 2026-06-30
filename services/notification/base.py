# File: services/notification/base.py
"""
Observer Pattern — Base classes cho hệ thống thông báo.

Vai trò:
- IJobObserver  = Observer Interface  (Người theo dõi)
- JobSubject    = Subject             (Chủ thể - phát sự kiện)

Khi có công việc mới, Subject gọi notify_all() để thông báo
cho TẤT CẢ Observer đã đăng ký. Mỗi Observer tự quyết định
cách xử lý (gửi email, gửi SMS, hiện trên UI...).
"""
from abc import ABC, abstractmethod


class IJobObserver(ABC):
    """Interface Observer — Mọi kênh thông báo phải implement method này."""

    @abstractmethod
    def update(self, new_jobs: list[dict], eligible_users: list) -> dict:
        """Được gọi khi có job mới cần thông báo.
        
        Args:
            new_jobs: Danh sách công việc mới
            eligible_users: Danh sách (User, UserProfile) đủ điều kiện nhận
            
        Returns:
            dict: Kết quả thực thi {"sent": int, "errors": list}
        """
        pass


class JobSubject:
    """Subject — Quản lý danh sách Observer và phát thông báo.
    
    Ví dụ sử dụng:
        subject = JobSubject()
        subject.attach(EmailNotificationObserver())   # Đăng ký kênh Email
        subject.attach(SmsNotificationObserver())      # Đăng ký kênh SMS (tương lai)
        subject.notify_all(new_jobs, users)             # Phát thông báo cho tất cả
    """

    def __init__(self):
        self._observers: list[IJobObserver] = []

    def attach(self, observer: IJobObserver):
        """Đăng ký một Observer mới (thêm kênh thông báo)."""
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: IJobObserver):
        """Hủy đăng ký Observer (gỡ kênh thông báo)."""
        self._observers.remove(observer)

    def notify_all(self, new_jobs: list[dict], eligible_users: list) -> list[dict]:
        """Thông báo cho TẤT CẢ Observer đã đăng ký.
        
        Returns:
            list[dict]: Kết quả từ mỗi observer
        """
        results = []
        for observer in self._observers:
            result = observer.update(new_jobs, eligible_users)
            results.append(result)
        return results
