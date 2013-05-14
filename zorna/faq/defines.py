from django.utils.translation import ugettext_lazy as _

STATUS_ACTIVE = 1
STATUS_INACTIVE = 0

QUESTION_STATUS_CHOICES = (
    (STATUS_ACTIVE, 'Active'),
    (STATUS_INACTIVE, 'Inactive'),
)