import calendar
import datetime
import decimal

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect

from .forms import HistoryRecordForm, TransferRecordForm
from .models import *

# 中文版变量命名易于理解，英文版未上传

def 首页(request):
    today = datetime.date.today()
    全部账户 = Account.objects.all()
    收支类型 = Category.CATEGORY_TYPES
    账单记录 = HistoryRecord.objects.filter(记录时间__year=today.year, 记录时间__month=today.month).order_by("-记录时间")
    转移记录 = TransferRecord.objects.filter(转移时间__year=today.year, 转移时间__month=today.month).order_by("-转移时间")
    当月收入 = 0
    当月支出 = 0
    当月有账单记录的天数列表 = []
    当月全部账单记录 = {}
    当月有账单记录的天数列表及每天的收支合计 = {}
    for 一条账单记录 in 账单记录:
        if 一条账单记录.父级分类.收支类型.lower() == "expense":
            当月支出 -= 一条账单记录.金额
        elif 一条账单记录.父级分类.收支类型.lower() == "income":
            当月收入 += 一条账单记录.金额
        记录时间_日期星期格式 = 一条账单记录.记录时间.strftime("%Y-%m-%d %A")
        if 记录时间_日期星期格式 not in 当月有账单记录的天数列表:
            当月有账单记录的天数列表.append(记录时间_日期星期格式)
            当月全部账单记录[记录时间_日期星期格式] = [一条账单记录]
            当月有账单记录的天数列表及每天的收支合计[记录时间_日期星期格式] = {"income": 0, "expense": 0}
            if 一条账单记录.父级分类.收支类型.lower() == "expense":
                当月有账单记录的天数列表及每天的收支合计[记录时间_日期星期格式]["expense"] += 一条账单记录.金额
            elif 一条账单记录.父级分类.收支类型.lower() == "income":
                当月有账单记录的天数列表及每天的收支合计[记录时间_日期星期格式]["income"] += 一条账单记录.金额
        else:
            当月全部账单记录[记录时间_日期星期格式].append(一条账单记录)
            if 一条账单记录.父级分类.收支类型.lower() == "expense":
                当月有账单记录的天数列表及每天的收支合计[记录时间_日期星期格式]["expense"] += 一条账单记录.金额
            elif 一条账单记录.父级分类.收支类型.lower() == "income":
                当月有账单记录的天数列表及每天的收支合计[记录时间_日期星期格式]["income"] += 一条账单记录.金额
    for 一条转移记录 in 转移记录:
        记录时间_日期星期格式 = 一条转移记录.转移时间.strftime("%Y-%m-%d %A")
        if 记录时间_日期星期格式 not in 当月有账单记录的天数列表:
            当月有账单记录的天数列表.append(记录时间_日期星期格式)
            当月全部账单记录[记录时间_日期星期格式] = [一条转移记录]
            当月有账单记录的天数列表及每天的收支合计[记录时间_日期星期格式] = {"income": 0, "expense": 0}
        else:
            当月全部账单记录[记录时间_日期星期格式].append(一条转移记录)
    当月有账单记录的天数列表.sort(reverse=True)
    context = {
        '全部账户': 全部账户,
        '收支类型': 收支类型,
        '当月有账单记录的天数列表': 当月有账单记录的天数列表,
        # 'history_records': 账单记录,
        # 'transfer_records': 转移记录,
        '当月收入': 当月收入,
        '当月支出': 当月支出,
        '当月结余': 当月收入 + 当月支出,
        '当月全部账单记录': 当月全部账单记录,
        '当月有账单记录的天数列表及每天的收支合计': 当月有账单记录的天数列表及每天的收支合计
    }
    return render(request, 'index.html', context)

def 获取分类(request):
    if request.user.is_authenticated:
        收支类型 = request.POST.get('CATEGORY_TYPES')
        全部分类 = Category.objects.filter(收支类型=收支类型)
        分类列表 = []
        for 一个分类 in 全部分类:
            分类列表.append((一个分类.id, 一个分类.分类名))
        return JsonResponse({"categories": 分类列表})
    else:
        return JsonResponse({"error": "未登录用户，禁止访问数据！"})

def 获取子分类(request):
    if request.user.is_authenticated:
        收支类型 = request.POST.get('parent_category')
        父级分类 = Category.objects.filter(分类名=收支类型)[0]
        子分类 = SubCategory.objects.filter(父级分类=父级分类)
        子分类列表 = []
        for 一个子分类 in 子分类:
            子分类列表.append((一个子分类.id, 一个子分类.分类名))
        return JsonResponse({"subcategories": 子分类列表})
    else:
        return JsonResponse({"error": "未登录用户，禁止访问数据！"})

def 提交收支记录(request):
    if request.user.is_authenticated:
        子级分类 = request.POST.get('子级分类')
        if 子级分类 == "select value":
            try:
                账户 = request.POST.get('账户')
                父级分类 = request.POST.get('父级分类')
                金额 = request.POST.get('金额')
                备注 = request.POST.get('备注')
                记录时间 = request.POST.get('记录时间')
                账单记录 = HistoryRecord(账户_id=账户, 父级分类_id=父级分类, 金额=金额, 备注=备注, 记录时间=记录时间)
                账单记录.save()
                当前账户 = Account.objects.filter(id=账户)[0]
                当前账户类型 = Category.objects.filter(id=父级分类)[0].收支类型
                if 当前账户类型.lower() == "expense":
                    当前账户.余额 -= decimal.Decimal(金额)
                elif 当前账户类型.lower() == "income":
                    当前账户.余额 += decimal.Decimal(金额)
                当前账户.save()
            except Exception as e:
                print("not valid in request with error: %s" % str(e))
        else:
            form = HistoryRecordForm(request.POST)
            if form.is_valid():
                账户 = form.cleaned_data['账户']
                父级分类 = form.cleaned_data['父级分类']
                子级分类 = form.cleaned_data['子级分类']
                金额 = form.cleaned_data['金额']
                备注 = form.cleaned_data['备注']
                记录时间 = form.cleaned_data['记录时间']
                账单记录 = HistoryRecord(账户=账户, 父级分类=父级分类, 子级分类=子级分类, 金额=金额, 备注=备注, 记录时间=记录时间)
                账单记录.save()
                当前账户类型 = 父级分类.收支类型
                if 当前账户类型.lower() == "expense":
                    账户.余额 -= decimal.Decimal(金额)
                elif 当前账户类型.lower() == "income":
                    账户.余额 += decimal.Decimal(金额)
                账户.save()
            else:
                print("not valid in form")
        return redirect(首页)
    else:
        return JsonResponse({"error": "未登录用户，禁止访问数据！"})

def 获取当月收支echarts图表接口(request):
    if request.user.is_authenticated:
        year = request.POST.get('year')
        month = request.POST.get('month')
        if year and month:
            year = int(year)
            month = int(month)
        else:
            today = datetime.date.today()
            year = today.year
            month = today.month
        month_has_days = calendar.monthrange(year, month)[1]
        days = [datetime.date(year, month, day).strftime("%Y-%m-%d") for day in range(1, month_has_days+1)]
        days_income = []
        days_expense = []
        category_names = []
        month_category_income = {}
        month_category_expense = {}
        month_total_income = 0
        month_total_expense = 0
        month_history_records = HistoryRecord.objects.filter(记录时间__year=year, 记录时间__month=month).order_by("记录时间")
        for day in days:
            day_history_records = month_history_records.filter(记录时间__day=int(day.split("-")[-1]))
            day_income = 0
            day_expense = 0
            for hr in day_history_records:
                hr_category = hr.父级分类
                if hr_category.收支类型.lower() == "expense":
                    day_expense += hr.金额
                    month_total_expense += hr.金额
                    if hr_category.分类名 not in category_names:
                        category_names.append(hr_category.分类名)
                        month_category_expense[hr_category.分类名] = {"value": hr.金额, "name": hr_category.分类名}
                    else:
                        month_category_expense[hr_category.分类名]["value"] += hr.金额
                elif hr_category.收支类型.lower() == "income":
                    day_income += hr.金额
                    month_total_income += hr.金额
                    if hr_category.分类名 not in category_names:
                        category_names.append(hr_category.分类名)
                        month_category_income[hr_category.分类名] = {"value": hr.金额, "name": hr_category.分类名}
                    else:
                        month_category_income[hr_category.分类名]["value"] += hr.金额
            days_income.append(day_income)
            days_expense.append(day_expense)
        return JsonResponse({
            "days": days,
            "days_income": days_income,
            "days_expense": days_expense,
            "month_total_income": month_total_income,
            "month_total_expense": month_total_expense,
            "month_category_names": category_names,
            "month_category_income": list(month_category_income.values()),
            "month_category_expense": list(month_category_expense.values())
        })
    else:
        return JsonResponse({"error": "未登录用户，禁止访问数据！"})

def 获取当年收支echarts图表接口(request):
    if request.user.is_authenticated:
        year = request.POST.get('year')
        if year:
            year = int(year)
        else:
            today = datetime.date.today()
            year = today.year
        months = [i for i in range(1, 13)]
        months_income = []
        months_expense = []
        category_names = []
        year_category_income = {}
        year_category_expense = {}
        year_total_income = 0
        year_total_expense = 0
        year_history_records = HistoryRecord.objects.filter(记录时间__year=year).order_by("记录时间")
        for month in months:
            month_history_records = year_history_records.filter(记录时间__month=month)
            month_income = 0
            month_expense = 0
            for hr in month_history_records:
                hr_category = hr.父级分类
                if hr_category.收支类型.lower() == "expense":
                    month_expense += hr.金额
                    year_total_expense += hr.金额
                    if hr_category.分类名 not in category_names:
                        category_names.append(hr_category.分类名)
                        year_category_expense[hr_category.分类名] = {"value": hr.金额, "name": hr_category.分类名}
                    else:
                        year_category_expense[hr_category.分类名]["value"] += hr.金额
                elif hr_category.收支类型.lower() == "income":
                    month_income += hr.金额
                    year_total_income += hr.金额
                    if hr_category.分类名 not in category_names:
                        category_names.append(hr_category.分类名)
                        year_category_income[hr_category.分类名] = {"value": hr.金额, "name": hr_category.分类名}
                    else:
                        year_category_income[hr_category.分类名]["value"] += hr.金额
            months_income.append(month_income)
            months_expense.append(month_expense)
        return JsonResponse({
            "months": months,
            "months_income": months_income,
            "months_expense": months_expense,
            "year_total_income": year_total_income,
            "year_total_expense": year_total_expense,
            "year_category_names": category_names,
            "year_category_income": list(year_category_income.values()),
            "year_category_expense": list(year_category_expense.values())
        })
    else:
        return JsonResponse({"error": "未登录用户，禁止访问数据！"})

def 获取有数据的年份(request):
    """
    有Bug,早于当前年份的数据显示异常
    """
    if request.user.is_authenticated:
        按时间排序的记录 = HistoryRecord.objects.order_by("记录时间")
        第一条记录 = 按时间排序的记录.first()
        最后一条记录 = 按时间排序的记录.last()
        年份列表 = [y for y in range(最后一条记录.记录时间.year, 第一条记录.记录时间.year-1, -1)]
        return JsonResponse({"years": 年份列表})
    else:
        return JsonResponse({"error": "未登录用户，禁止访问数据！"})

def 获取有数据的月份(request):
    if request.user.is_authenticated:
        year = request.POST.get('year')
        按时间排序的记录 = HistoryRecord.objects.filter(记录时间__year=year).order_by("记录时间")
        第一条记录 = 按时间排序的记录.first()
        最后一条记录 = 按时间排序的记录.last()
        月份列表 = [m for m in range(最后一条记录.记录时间.month, 第一条记录.记录时间.month-1, -1)]
        return JsonResponse({"months": 月份列表})
    else:
        return JsonResponse({"error": "未登录用户，禁止访问数据！"})

def 搜索账单记录(request):
    if request.user.is_authenticated:
        keyword = request.POST.get('keyword')
        父级分类 = Category.objects.filter(分类名__icontains=keyword)
        子级分类 = SubCategory.objects.filter(分类名__icontains=keyword)
        全部账单记录 = HistoryRecord.objects.filter(Q(父级分类__in=父级分类) | Q(子级分类__in=子级分类) | Q(备注__icontains=keyword) | Q(金额__icontains=keyword))
        records = []
        for 一个账单记录 in 全部账单记录:
            records.append({
                "day": 一个账单记录.记录时间.strftime("%Y-%m-%d %A"),
                "父级分类": 一个账单记录.父级分类.分类名,
                "子级分类": 一个账单记录.子级分类.分类名 if 一个账单记录.子级分类 else "未选择子类",
                "金额": 一个账单记录.金额,
                "备注": 一个账单记录.备注 if 一个账单记录.备注 else "",
                "账户": 一个账单记录.账户.账户名称,
                "收支类型": 一个账单记录.父级分类.收支类型.lower()
            })
        return JsonResponse({"records": records})
    else:
        return JsonResponse({"error": "未登录用户，禁止访问数据！"})

def 通过日期筛选账单记录(request):
    if request.user.is_authenticated:
        year = request.POST.get('year')
        month = request.POST.get('month')
        账单记录 = HistoryRecord.objects.filter(记录时间__year=year, 记录时间__month=month).order_by("-记录时间")
        转移记录 = TransferRecord.objects.filter(转移时间__year=year, 转移时间__month=month).order_by("-转移时间")
        当月有账单记录的天数列表 = []
        指定月份的全部账单记录 = {}
        for 一条账单记录 in 账单记录:
            记录时间_日期星期格式 = 一条账单记录.记录时间.strftime("%Y-%m-%d %A")
            新的账单记录 = {
                "父级分类": 一条账单记录.父级分类.分类名,
                "子级分类": 一条账单记录.子级分类.分类名 if 一条账单记录.子级分类 else "未选择子类",
                "金额": 一条账单记录.金额,
                "备注": 一条账单记录.备注 if 一条账单记录.备注 else "",
                "账户": 一条账单记录.账户.账户名称,
                "收支类型": 一条账单记录.父级分类.收支类型.lower(),
                "记录类型": "income_expense"
            }
            if 记录时间_日期星期格式 not in 当月有账单记录的天数列表:
                当月有账单记录的天数列表.append(记录时间_日期星期格式)
                指定月份的全部账单记录[记录时间_日期星期格式] = [新的账单记录]
            else:
                指定月份的全部账单记录[记录时间_日期星期格式].append(新的账单记录)
        for 一条转移记录 in 转移记录:
            记录时间_日期星期格式 = 一条转移记录.转移时间.strftime("%Y-%m-%d %A")
            新的转移记录 = {
                "转移金额": 一条转移记录.转移金额,
                "备注": 一条转移记录.备注 if 一条转移记录.备注 else "",
                "从哪个账户转移": 一条转移记录.从哪个账户转移.账户名称,
                "转移到哪个账户": 一条转移记录.转移到哪个账户.账户名称,
                "记录类型": "transfer"
            }
            if 记录时间_日期星期格式 not in 当月有账单记录的天数列表:
                当月有账单记录的天数列表.append(记录时间_日期星期格式)
                指定月份的全部账单记录[记录时间_日期星期格式] = [新的转移记录]
            else:
                指定月份的全部账单记录[记录时间_日期星期格式].append(新的转移记录)
        # return JsonResponse({'day_has_record': 当月有账单记录的天数列表, "records": 指定月份的全部账单记录})
        return JsonResponse({"records": 指定月份的全部账单记录})
    else:
        return JsonResponse({"error": "未登录用户，禁止访问数据！"})

def 转移账户余额(request):
    if request.user.is_authenticated:
        form = TransferRecordForm(request.POST)
        if form.is_valid():
            从哪个账户转移 = form.cleaned_data['从哪个账户转移']
            转移到哪个账户 = form.cleaned_data['转移到哪个账户']
            if 从哪个账户转移 != 转移到哪个账户:
                转移金额 = form.cleaned_data['转移金额']
                备注 = form.cleaned_data['备注']
                转移时间 = form.cleaned_data['转移时间']
                转移记录 = TransferRecord(
                    从哪个账户转移=从哪个账户转移,
                    转移到哪个账户=转移到哪个账户,
                    转移金额=转移金额,
                    备注=备注,
                    转移时间=转移时间
                )
                转移记录.save()
                从哪个账户转移.余额 -= decimal.Decimal(转移金额)
                从哪个账户转移.save()
                转移到哪个账户.余额 += decimal.Decimal(转移金额)
                转移到哪个账户.save()
            else:
                print("警告: 不能在两个相同的账户之间转账!")
        return redirect(首页)
    else:
        return JsonResponse({"error": "未登录用户，禁止访问数据！"})
