from django.urls import path
from .views import *

urlpatterns = [
    path('', 首页, name='index'),
    path('retrieve_category/', 获取分类, name='retrieve_category'),
    path('retrieve_subcategory/', 获取子分类, name='retrieve_subcategory'),
    path('record_income_expense/', 提交收支记录, name='record_income_expense'),
    path('retrieve_current_month_income_expense/', 获取当月收支echarts图表接口, name='retrieve_current_month_income_expense'),
    path('retrieve_current_year_income_expense/', 获取当年收支echarts图表接口, name='retrieve_current_year_income_expense'),
    path('retrieve_year_has_data/', 获取有数据的年份, name='retrieve_year_has_data'),
    path('retrieve_month_has_data/', 获取有数据的月份, name='retrieve_month_has_data'),
    path('search_record/', 搜索账单记录, name='search_record'),
    path('filter_record_by_date/', 通过日期筛选账单记录, name='filter_record_by_date'),
    path('transfer-between-accounts/', 转移账户余额, name='transfer_between_accounts')
]
