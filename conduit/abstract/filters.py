from django.db.models import QuerySet
from django.http import HttpRequest
from rest_framework import filters


class IsOwnerFilterBackend(filters.BaseFilterBackend):
    """
    Filter that only allows users to see their own objects.
    """

    def filter_queryset(self, request: HttpRequest, queryset, view) -> QuerySet:
        return queryset.filter(owner=request.user)
