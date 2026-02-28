from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import CreateView, ListView
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Payment
from .forms import PaymentForm
from ..printers.services import print_receipt
from ..printers.models import PrinterConfig
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DeleteView

class PaymentCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Payment
    form_class = PaymentForm
    template_name = 'payments/payment_form.html'
    success_url = reverse_lazy('payment-list')
    permission_required = 'payments.add_payment'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        # Print receipt
        try:
            config = PrinterConfig.get_config()
            print_receipt(self.object, config)
            messages.success(self.request, "Payment saved and receipt printed.")
        except Exception as e:
            messages.warning(self.request, f"Payment saved but printing failed: {e}")
        return response

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from .models import Payment

class PaymentListView(LoginRequiredMixin, ListView):
    model = Payment
    template_name = "payments/payment_list.html"
    context_object_name = "payments"
    paginate_by = 20

from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

from .models import Payment
from ..printers.models import PrinterConfig
from ..printers.services import print_receipt


@login_required
@permission_required("payments.view_payment", raise_exception=True)
def payment_print_receipt(request, pk: int):
    payment = get_object_or_404(Payment, pk=pk)

    try:
        config = PrinterConfig.get_config()
        print_receipt(payment, config)
        messages.success(request, "Chek printerdan chiqarildi.")
    except Exception as e:
        messages.error(request, f"Chek chiqarilmadi: {e}")

    # listga qaytaradi
    return redirect("payment-list")

class PaymentDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Payment
    template_name = 'payments/payment_confirm_delete.html'  # tasdiqlash sahifasi
    success_url = reverse_lazy('payment-list')
    permission_required = 'payments.delete_payment'
