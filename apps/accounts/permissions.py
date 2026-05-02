from rest_framework import permissions

class IsAdminOrCashier(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name__in=['Admin', 'Cashier']).exists()

class CanPrintReceipt(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('payments.can_print_receipt')  # custom permission

# For Django views we'll use user_passes_test or group checks.