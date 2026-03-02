
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponseForbidden
from leads.models import Lead
from tasks.models import Task
from calls.models import Call


def _unique_customer_count(leads_qs):
    keys = []
    for l in leads_qs:
        if l.email:
            keys.append(f"e:{l.email.strip().lower()}")
        elif l.phone:
            keys.append(f"p:{l.phone.strip()}")
        else:
            keys.append(f"id:{l.id}")
    return len(set(keys))


@login_required
def dashboard_home(request):
    user = request.user
    if not user.is_staff:
        return HttpResponseForbidden("Not allowed")

    if user.is_superuser:
        leads = Lead.objects.all()
        tasks = Task.objects.all()
    elif user.is_staff:
        leads = Lead.objects.filter(assigned_to=user)
        tasks = Task.objects.filter(assigned_to=user)
    else:
        leads = Lead.objects.filter(assigned_to=user)
        tasks = Task.objects.filter(assigned_to=user)

    if user.is_superuser:
        my_leads = Lead.objects.all()
        my_tasks = Task.objects.all()
        my_calls = Call.objects.all()
    else:
        my_leads = Lead.objects.filter(assigned_to=user)
        my_tasks = Task.objects.filter(assigned_to=user)
        my_calls = Call.objects.filter(created_by=user)

    all_calls = Call.objects.all() if user.is_superuser else my_calls

    unique_total = _unique_customer_count(leads)
    my_unique_total = _unique_customer_count(my_leads)

    total_calls = all_calls.count()
    ivr_calls = all_calls.filter(call_type='ivr').count()
    incoming_calls = all_calls.filter(call_type='incoming').count()
    outgoing_calls = all_calls.filter(call_type='outgoing').count()
    missed_calls = all_calls.filter(call_type='missed').count()

    def pct(v, total):
        if total <= 0:
            return 0
        return round((v / total) * 100)

    context = {
    'total_leads': unique_total,
    'fresh_leads': leads.filter(status='fresh').count(),
    'returning_leads': leads.filter(status='returning').count(),
    'untouched_leads': leads.filter(status='untouched').count(),
    'closed_leads': leads.filter(status='closed').count(),
    'unassigned_leads': Lead.objects.filter(assigned_to__isnull=True).count(),

    'completed_tasks': tasks.filter(is_completed=True).count(),
    'pending_tasks': tasks.filter(is_completed=False).count(),
    'my_leads': my_unique_total,
    'my_fresh_leads': my_leads.filter(status='fresh').count(),
    'my_returning_leads': my_leads.filter(status='returning').count(),
    'my_tasks': my_tasks.count(),
    'my_site_visits': my_tasks.filter(task_type='site_visit').count(),
    'my_total_calls': my_calls.count(),
    'my_meetings': my_tasks.filter(task_type='meeting').count(),
    'my_mails': my_tasks.filter(task_type='follow_up').count(),
    'my_total_activities': my_calls.count() + my_tasks.count(),
    'ivr_calls': ivr_calls,
    'incoming_calls': incoming_calls,
    'outgoing_calls': outgoing_calls,
    'missed_calls': missed_calls,
    'ivr_calls_pct': pct(ivr_calls, total_calls),
    'incoming_calls_pct': pct(incoming_calls, total_calls),
    'outgoing_calls_pct': pct(outgoing_calls, total_calls),
    'missed_calls_pct': pct(missed_calls, total_calls),
}

    return render(request, 'dashboard/home.html', context)


@login_required
def activity_list(request):
    user = request.user
    if not user.is_staff:
        return HttpResponseForbidden("Not allowed")

    if user.is_superuser:
        tasks_qs = Task.objects.select_related("lead", "property", "assigned_to").all()
        calls_qs = Call.objects.select_related("lead", "created_by").all()
    else:
        tasks_qs = Task.objects.select_related("lead", "property", "assigned_to").filter(assigned_to=user)
        calls_qs = Call.objects.select_related("lead", "created_by").filter(created_by=user)

    items = []
    for t in tasks_qs:
        items.append({
            "kind": "Task",
            "type": t.task_type,
            "title": f"{t.task_type.title()} for {t.lead.name}",
            "who": t.assigned_to.username if t.assigned_to else "-",
            "when": t.due_date,
            "status": t.status,
        })

    for c in calls_qs:
        items.append({
            "kind": "Call",
            "type": c.call_type,
            "title": f"{c.call_type.title()} with {c.lead.name if c.lead else 'Lead'}",
            "who": c.created_by.username if c.created_by else "-",
            "when": c.created_at,
            "status": "completed",
        })

    items.sort(key=lambda x: x["when"], reverse=True)

    return render(request, "dashboard/activity_list.html", {"items": items})
