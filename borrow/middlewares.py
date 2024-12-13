from datetime import datetime, timedelta
from django.utils.timezone import now
from .models import LabApparelRequest, Liability

class ExpiredLabApparelRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Logic to handle expired LabApparelRequests
        today = now().date()

        # Filter expired requests
        expired_requests = LabApparelRequest.objects.filter(
            date_borrowed__lt=today - timedelta(days=1),  # Expired requests (borrowed more than 1 day ago)
            status='borrowed'  # Ensure only borrowed items are processed
        )

        for lab_request in expired_requests:
            # Check if a liability already exists for this request
            if not Liability.objects.filter(request=lab_request.control_number, request_type='lab_apparel_request').exists():
                # Create a liability record
                Liability.objects.create(
                    request=lab_request.control_number,
                    request_type='lab_apparel_request',
                    student=lab_request.student,
                    is_complied=False,
                )
                # Optionally, update the status of the lab request
                lab_request.status = 'returned'
                lab_request.save()

        # Continue processing the request
        response = self.get_response(request)
        return response
