from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from .models import Call
from leads.models import Lead


@login_required
def call_list(request):
    if request.user.is_superuser:
        calls = Call.objects.select_related("lead", "created_by").all()
    elif request.user.is_staff:
        calls = Call.objects.select_related("lead", "created_by").filter(created_by=request.user)
    else:
        return HttpResponseForbidden("Not allowed")

    call_type = request.GET.get("type")
    if call_type in {"ivr", "incoming", "outgoing", "missed"}:
        calls = calls.filter(call_type=call_type)

    return render(request, "calls/call_list.html", {"calls": calls})


@login_required
def call_add(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("Not allowed")

    leads = Lead.objects.all() if request.user.is_superuser else Lead.objects.filter(assigned_to=request.user)

    if request.method == "POST":
        lead_id = request.POST.get("lead_id")
        call_type = request.POST.get("call_type")
        duration = request.POST.get("duration_seconds")
        notes = request.POST.get("notes") or ""

        lead = Lead.objects.filter(id=lead_id).first() if lead_id else None

        Call.objects.create(
            lead=lead,
            created_by=request.user,
            call_type=call_type,
            duration_seconds=int(duration) if duration else None,
            notes=notes,
        )
        return redirect("call-list")

    return render(request, "calls/call_form.html", {"leads": leads})
