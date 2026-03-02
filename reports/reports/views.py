from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from openpyxl import Workbook

from leads.models import Lead
from properties.models import Property
from tasks.models import Task


def _unique_customer_count(leads_qs):
    keys = []
    for lead in leads_qs:
        if lead.email:
            keys.append(f"e:{lead.email.strip().lower()}")
        elif lead.phone:
            keys.append(f"p:{lead.phone.strip()}")
        else:
            keys.append(f"id:{lead.id}")
    return len(set(keys))


def _apply_date_filters(request, leads_qs, tasks_qs):
    period = request.GET.get("period", "30d")
    from_date = request.GET.get("from", "")
    to_date = request.GET.get("to", "")

    if from_date and to_date:
        leads_qs = leads_qs.filter(created_at__date__gte=from_date, created_at__date__lte=to_date)
        tasks_qs = tasks_qs.filter(created_at__date__gte=from_date, created_at__date__lte=to_date)
    else:
        now = timezone.now()
        if period == "today":
            leads_qs = leads_qs.filter(created_at__date=now.date())
            tasks_qs = tasks_qs.filter(created_at__date=now.date())
        elif period == "7d":
            start = now - timedelta(days=7)
            leads_qs = leads_qs.filter(created_at__gte=start)
            tasks_qs = tasks_qs.filter(created_at__gte=start)
        elif period == "30d":
            start = now - timedelta(days=30)
            leads_qs = leads_qs.filter(created_at__gte=start)
            tasks_qs = tasks_qs.filter(created_at__gte=start)

    return leads_qs, tasks_qs, period, from_date, to_date


def _last_n_months(n=6):
    now = timezone.now()
    months = []
    y = now.year
    m = now.month
    for i in range(n - 1, -1, -1):
        mm = m - i
        yy = y
        while mm <= 0:
            mm += 12
            yy -= 1
        months.append((yy, mm))
    return months


def _polyline_points(values, y_min=30, y_max=170, scale_max=None):
    if not values:
        return ""
    max_val = scale_max if scale_max is not None else max(values)
    if max_val <= 0:
        max_val = 1
    step = 540 / (len(values) - 1) if len(values) > 1 else 0
    points = []
    for idx, value in enumerate(values):
        x = 30 + (idx * step)
        ratio = value / max_val
        y = y_max - ((y_max - y_min) * ratio)
        points.append(f"{x:.1f},{y:.1f}")
    return " ".join(points)


@login_required
def reports_home(request):
    user = request.user

    if user.is_staff:
        leads_qs = Lead.objects.all()
        tasks_qs = Task.objects.all()
    else:
        leads_qs = Lead.objects.filter(assigned_to=user)
        tasks_qs = Task.objects.filter(assigned_to=user)

    leads_qs, tasks_qs, period, from_date, to_date = _apply_date_filters(request, leads_qs, tasks_qs)

    total_enquiries = leads_qs.count()
    unique_customers = _unique_customer_count(leads_qs)
    closed_leads = leads_qs.filter(status="closed").count()
    conversion_rate = round((closed_leads / total_enquiries) * 100, 1) if total_enquiries else 0

    months = _last_n_months(6)
    month_labels = []
    enquiries_by_month = []
    closed_by_month = []
    for yy, mm in months:
        label = datetime(yy, mm, 1).strftime("%b")
        month_labels.append(label)
        month_enquiries = leads_qs.filter(created_at__year=yy, created_at__month=mm).count()
        month_closed = leads_qs.filter(created_at__year=yy, created_at__month=mm, status="closed").count()
        enquiries_by_month.append(month_enquiries)
        closed_by_month.append(month_closed)

    trend_rows = []
    for i in range(len(month_labels)):
        trend_rows.append(
            {
                "label": month_labels[i],
                "enquiries": enquiries_by_month[i],
                "closed": closed_by_month[i],
            }
        )

    if user.is_superuser:
        properties_qs = Property.objects.all()
    else:
        properties_qs = Property.objects.filter(assigned_to=user)

    total_properties = properties_qs.count()
    distribution = []
    colors = {
        "house": "#2563eb",
        "apartment": "#f59e0b",
        "villa": "#10b981",
        "building": "#8b5cf6",
        "complex": "#06b6d4",
        "commercial": "#ef4444",
        "land": "#94a3b8",
    }
    for key, label in Property.PROPERTY_TYPE_CHOICES:
        count = properties_qs.filter(property_type=key).count()
        if count == 0:
            continue
        percent = round((count / total_properties) * 100, 1) if total_properties else 0
        distribution.append(
            {
                "label": label,
                "count": count,
                "percent": percent,
                "color": colors.get(key, "#64748b"),
            }
        )

    recent_transactions = leads_qs.select_related("property", "assigned_to").order_by("-created_at")[:8]

    chart_scale_max = max(enquiries_by_month + closed_by_month) if (enquiries_by_month or closed_by_month) else 1

    context = {
        "total_leads": total_enquiries,
        "total_enquiries": total_enquiries,
        "unique_customers": unique_customers,
        "conversion_rate": conversion_rate,
        "fresh_leads": leads_qs.filter(status="fresh").count(),
        "returning_leads": leads_qs.filter(status="returning").count(),
        "untouched_leads": leads_qs.filter(status="untouched").count(),
        "closed_leads": closed_leads,
        "total_tasks": tasks_qs.count(),
        "completed_tasks": tasks_qs.filter(is_completed=True).count(),
        "pending_tasks": tasks_qs.filter(is_completed=False).count(),
        "selected_period": period,
        "from_date": from_date,
        "to_date": to_date,
        "query_string": request.GET.urlencode(),
        "trend_rows": trend_rows,
        "sales_polyline": _polyline_points(enquiries_by_month, scale_max=chart_scale_max),
        "closed_polyline": _polyline_points(closed_by_month, scale_max=chart_scale_max),
        "distribution": distribution,
        "recent_transactions": recent_transactions,
    }
    return render(request, "reports/home.html", context)


@login_required
def export_reports_excel(request):
    user = request.user

    if user.is_staff:
        leads = Lead.objects.all()
        tasks = Task.objects.all()
    else: 
        leads = Lead.objects.filter(assigned_to=user)
        tasks = Task.objects.filter(assigned_to=user)

    leads, tasks, _, _, _ = _apply_date_filters(request, leads, tasks)

    wb = Workbook()
    ws1 = wb.active
    ws1.title = "Leads Report"
    ws1.append(["Name", "Email", "Phone", "Status", "Assigned To"])

    for lead in leads:
        ws1.append(
            [
                lead.name,
                lead.email,
                lead.phone,
                lead.status,
                lead.assigned_to.username if lead.assigned_to else "",
            ]
        )

    ws2 = wb.create_sheet(title="Tasks Report")
    ws2.append(["Title", "Assigned To", "Completed"])

    for task in tasks:
        ws2.append(
            [
                str(task),
                task.assigned_to.username if task.assigned_to else "",
                "Yes" if task.is_completed else "No",
            ]
        )

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="crm_report.xlsx"'
    wb.save(response)
    return response
