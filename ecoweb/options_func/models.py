from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserTracker(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trackers')
    method = models.CharField(max_length=20, default='distance')  # 交易策略方法
    stock1 = models.CharField(max_length=10)
    stock2 = models.CharField(max_length=10)
    start_date = models.DateField()
    end_date = models.DateField()
    window_size = models.IntegerField()
    n_std = models.FloatField()
    track_date = models.DateTimeField(default=timezone.now)  # 建立的日期
    created_at = models.DateTimeField(auto_now_add=True)
    print(track_date)

    def __str__(self):
        return f"{self.user.username}: {self.method} - {self.stock1}-{self.stock2} ({self.start_date} to {self.end_date})"