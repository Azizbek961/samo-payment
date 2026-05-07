from django.contrib import messages
from django.views.generic import CreateView, ListView, DeleteView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from .models import Payment
from .forms import PaymentForm
from ..printers.services import print_receipt
from ..printers.models import PrinterConfig


class PaymentCreateView(CreateView):
    model = Payment
    form_class = PaymentForm
    template_name = 'payments/payment_form.html'
    success_url = reverse_lazy('payment-list')
    def form_valid(self, form):
        response = super().form_valid(form)
        try:
            config = PrinterConfig.get_config()
            print_receipt(self.object, config)
            messages.success(self.request, "Payment saved and receipt printed.")
        except Exception as e:
            messages.warning(self.request, f"Payment saved but printing failed: {e}")
        return response


class PaymentListView(ListView):
    model = Payment
    template_name = "payments/payment_list.html"
    context_object_name = "payments"
    paginate_by = 20


class PaymentDeleteView(DeleteView):
    model = Payment
    template_name = 'payments/payment_confirm_delete.html'
    success_url = reverse_lazy('payment-list')
def payment_print_receipt(request, pk: int):
    payment = get_object_or_404(Payment, pk=pk)

    try:
        config = PrinterConfig.get_config()
        print_receipt(payment, config)
        messages.success(request, "Chek printerdan chiqarildi.")
    except Exception as e:
        messages.error(request, f"Chek chiqarilmadi: {e}")

    return redirect("payment-list")
