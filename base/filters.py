from django_filters import rest_framework as filters


class FlightFilter(filters.FilterSet):
    flight = filters.BaseInFilter(field_name="airplane", lookup_expr="in")
    airplane_name = filters.CharFilter(
        field_name="airplane__name", lookup_expr="icontains"
    )
