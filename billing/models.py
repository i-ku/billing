from django.db import models
from django.utils import timezone

class Account(models.Model):
    账户名称 = models.CharField(max_length=100)
    余额 = models.DecimalField(max_digits=8, decimal_places=2)
    图标 = models.CharField(max_length=100, null=True)
    创建时间 = models.DateTimeField(auto_now_add=True)
    修改时间 = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.账户名称} - {self.余额}元'

    class Meta:
        ordering = ['创建时间']
        verbose_name = '账户'
        verbose_name_plural = '账户'

class Category(models.Model):
    CATEGORY_TYPES = (
        ("expense", "支出"),
        ("income", "收入"),
    )
    分类名 = models.CharField(max_length=100)
    收支类型 = models.CharField(choices=CATEGORY_TYPES, default=CATEGORY_TYPES[0][0], max_length=100)

    def __str__(self):
        return self.分类名

    class Meta:
        ordering = ['id']
        verbose_name = '分类'
        verbose_name_plural = '分类'

class SubCategory(models.Model):
    分类名 = models.CharField(max_length=100)
    父级分类 = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.分类名

    class Meta:
        ordering = ['id']
        verbose_name = '子分类'
        verbose_name_plural = '子分类'

class HistoryRecord(models.Model):
    账户 = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, default=1)
    记录时间 = models.DateTimeField(default=timezone.now)
    父级分类 = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    子级分类 = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True)
    金额 = models.DecimalField(max_digits=8, decimal_places=2)
    备注 = models.CharField(max_length=500, null=True, blank=True)
    创建时间 = models.DateTimeField(auto_now_add=True)
    修改时间 = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.父级分类.分类名} - {self.备注} - {self.金额}元'

    class Meta:
        ordering = ['-记录时间']
        verbose_name = '账单记录'
        verbose_name_plural = '账单记录'

class TransferRecord(models.Model):
    从哪个账户转移 = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, default=1, related_name='from_account')
    转移到哪个账户 = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, default=2, related_name='to_account')
    转移时间 = models.DateTimeField(default=timezone.now)
    转移金额 = models.DecimalField(max_digits=8, decimal_places=2)
    备注 = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        ordering = ['-转移时间']
