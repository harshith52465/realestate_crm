from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Lead
from django.http import HttpResponseForbidden
from accounts.permissions import is_admin
from django.contrib.auth.decorators import login_required
from .models import Lead
from django.contrib.auth.models import User

@login_required
def lead_list(request):

    # Admin sees all
    if request.user.is_superuser:
        leads = Lead.objects.all()

    # Agents see assigned leads only
    elif request.user.is_staff:
        leads = Lead.objects.filter(assigned_to=request.user)

    # Customers see nothing
    else:
        leads = Lead.objects.none()

    status = request.GET.get("status")
    if status == "unassigned":
        leads = leads.filter(assigned_to__isnull=True)
    elif status:
        leads = leads.filter(status=status)

    grouped = []
    seen = set()
    for l in leads.order_by("-created_at"):
        key = l.email or l.phone or f"id:{l.id}"
        if key in seen:
            continue
        seen.add(key)

        if l.email:
            qs = Lead.objects.filter(email=l.email)
        elif l.phone:
            qs = Lead.objects.filter(phone=l.phone)
        else:
            qs = Lead.objects.filter(id=l.id)

        props = list(
            qs.exclude(property__isnull=True)
              .values_list("property__title", flat=True)
              .distinct()
        )
        count = qs.count()

        grouped.append({
            "lead": l,
            "count": count,
            "properties": props,
        })

    return render(request, "leads/lead_list.html", {
        "grouped": grouped,
    })

@login_required
def lead_create(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("Not allowed")

    users = User.objects.filter(is_staff=False)

    if request.method == "POST":
        Lead.objects.create(
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),   
            status=request.POST.get('status'),
            assigned_to_id=request.POST.get('assigned_to')
        )
        return redirect('lead-list')

    return render(request, 'leads/lead_form.html', {'users': users})

@login_required
def lead_add(request):
    if not is_admin(request.user):
        return HttpResponseForbidden("You are not allowed to add leads")


@login_required
def lead_update_status(request, pk):
    lead = Lead.objects.filter(pk=pk).first()
    if not lead:
        return HttpResponseForbidden("Lead not found")

    # Admin can update any; agents can update their own leads only
    if not (request.user.is_superuser or lead.assigned_to == request.user):
        return HttpResponseForbidden("Not allowed")

    if request.method == "POST":
        status = request.POST.get("status")
        if status in {"fresh", "returning", "untouched", "closed"}:
            lead.status = status
            lead.save()
    return redirect("lead-list")
