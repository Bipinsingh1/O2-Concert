from django.core.exceptions import ValidationError
from core.constants import GROUP_MAX_MEMBERS


def validate_group_size(members: int):
    if members < 1 or members > GROUP_MAX_MEMBERS:
        raise ValidationError(
            f'A group ticket must have between 1 and {GROUP_MAX_MEMBERS} members.'
        )


def validate_age_group_for_purchase(age_group: str, is_standalone: bool):
    """Children cannot purchase tickets on their own."""
    if age_group == 'child' and is_standalone:
        raise ValidationError('Children cannot purchase tickets independently.')
