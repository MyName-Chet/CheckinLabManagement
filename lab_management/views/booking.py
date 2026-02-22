# อัษฎาวุธ — Booking

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

from ..forms.booking import BookingForm
from ..models import Booking, Computer


class AdminBookingView(LoginRequiredMixin, View):
    def get(self, request):
        bookings = Booking.objects.select_related("computer").order_by("-start_time")
        form = BookingForm()
        return render(
            request,
            "cklab/admin/admin-booking.html",
            {
                "bookings": bookings,
                "form": form,
            },
        )

    def post(self, request):
        form = BookingForm(request.POST)
        bookings = Booking.objects.select_related("computer").order_by("-start_time")

        if not form.is_valid():
            return render(
                request,
                "cklab/admin/admin-booking.html",
                {
                    "bookings": bookings,
                    "form": form,
                },
            )

        booking = Booking.objects.create(
            student_id=form.cleaned_data["student_id"],
            computer=form.cleaned_data["computer"],
            start_time=form.cleaned_data["start_time"],
            end_time=form.cleaned_data["end_time"],
            status=form.cleaned_data["status"],
        )

        if booking.computer and booking.status in ["PENDING", "APPROVED"]:
            Computer.objects.filter(pk=booking.computer_id).update(status="RESERVED")

        return redirect("admin_booking")


class AdminBookingDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        pass

    def post(self, request, pk):
        pass


class AdminImportBookingView(LoginRequiredMixin, View):
    def post(self, request):
        pass
