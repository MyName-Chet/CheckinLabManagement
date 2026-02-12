from django.db import models

class Software(models.Model):
    TYPE_CHOICES = [('AI', 'AI Tool'), ('Software', 'General Software')]
    name = models.CharField(max_length=100)
    version = models.CharField(max_length=50)
    software_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
def __str__(self): return self.name

class Computer(models.Model):
    STATUS_CHOICES = [
        ('available', 'ว่าง'),
        ('in_use', 'ใช้งานอยู่'),
        ('reserved', 'จองแล้ว'),
        ('maintenance', 'แจ้งซ่อม')
    ]
    pc_id = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    pc_type = models.CharField(max_length=20, default='General')
    installed_software = models.ManyToManyField(Software, blank=True)
    
    # ข้อมูล Session
    current_user = models.CharField(max_length=100, blank=True, null=True)
    session_start = models.DateTimeField(null=True, blank=True)

    def __str__(self): return self.name

class UsageLog(models.Model):
    user_id = models.CharField(max_length=50)
    user_name = models.CharField(max_length=100)
    computer = models.ForeignKey(Computer, on_delete=models.SET_NULL, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(auto_now_add=True)
    satisfaction_score = models.IntegerField(null=True, blank=True)