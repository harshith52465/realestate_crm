from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Task
from leads.models import Lead
from properties.models import Property
from django.contrib.auth.models import User


@login_required
def task_list(request):
    user = request.user

    if user.is_superuser:
        tasks = Task.objects.all()
    elif user.is_staff:
        tasks = Task.objects.filter(assigned_to=user)
    else:
        tasks = Task.objects.none()

    task_type = request.GET.get("type")
    if task_type in {"call", "meeting", "site_visit", "follow_up"}:
        tasks = tasks.filter(task_type=task_type)

    return render(request, 'tasks/task_list.html', {'tasks': tasks})


@login_required
def task_add(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("Not allowed")

    if request.user.is_superuser:
        leads = Lead.objects.all()
    else:
        leads = Lead.objects.filter(assigned_to=request.user)
    if request.user.is_superuser:
        properties = Property.objects.all()
    else:
        properties = Property.objects.filter(assigned_to=request.user)
    agents = User.objects.filter(is_staff=True)

    if request.method == "POST":
        lead_id = request.POST.get("lead_id")
        property_id = request.POST.get("property_id")
        assigned_to_id = request.POST.get("assigned_to")
        task_type = request.POST.get("task_type")
        note = request.POST.get("note") or ""
        due_date = request.POST.get("due_date")
        priority = request.POST.get("priority")
        status = request.POST.get("status")

        lead = Lead.objects.filter(id=lead_id).first()
        prop = Property.objects.filter(id=property_id).first() if property_id else None
        if request.user.is_superuser:
            assigned_to = User.objects.filter(id=assigned_to_id).first() if assigned_to_id else request.user
        else:
            assigned_to = request.user

        task = Task.objects.create(
            lead=lead,
            property=prop,
            assigned_to=assigned_to,
            task_type=task_type,
            note=note,
            due_date=due_date,
            priority=priority,
            status=status,
            is_completed=(status == "completed"),
        )

        return redirect("task-list")

    return render(request, "tasks/task_form.html", {
        "leads": leads,
        "properties": properties,
        "agents": agents,
        "task": None,
    })


@login_required
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk)

    if not (request.user.is_superuser or task.assigned_to == request.user):
        return HttpResponseForbidden("Not allowed")

    if request.user.is_superuser:
        leads = Lead.objects.all()
        properties = Property.objects.all()
        agents = User.objects.filter(is_staff=True)
    else:
        leads = Lead.objects.filter(assigned_to=request.user)
        properties = Property.objects.filter(assigned_to=request.user)
        agents = User.objects.filter(id=request.user.id)

    if request.method == "POST":
        lead_id = request.POST.get("lead_id")
        property_id = request.POST.get("property_id")
        assigned_to_id = request.POST.get("assigned_to")
        task_type = request.POST.get("task_type")
        note = request.POST.get("note") or ""
        due_date = request.POST.get("due_date")
        priority = request.POST.get("priority")
        status = request.POST.get("status")

        task.lead = Lead.objects.filter(id=lead_id).first()
        task.property = Property.objects.filter(id=property_id).first() if property_id else None
        if request.user.is_superuser:
            task.assigned_to = User.objects.filter(id=assigned_to_id).first() if assigned_to_id else task.assigned_to
        task.task_type = task_type
        task.note = note
        task.due_date = due_date
        task.priority = priority
        task.status = status
        task.is_completed = (status == "completed")
        task.save()

        return redirect("task-list")

    return render(request, "tasks/task_form.html", {
        "leads": leads,
        "properties": properties,
        "agents": agents,
        "task": task,
    })


@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if not (request.user.is_superuser or task.assigned_to == request.user):
        return HttpResponseForbidden("Not allowed")
    if request.method == "POST":
        task.delete()
    return redirect("task-list")
