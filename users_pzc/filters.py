from django_filters import rest_framework as filters
from django.core.exceptions import ValidationError
from django.db.models import Q
from users_pzc.models import Waste, Energy, Water, Biodiversity, Logistices, Facility


# Facility Filter
class FacilityFilter(filters.FilterSet):
    search = filters.CharFilter(field_name='facility_name', lookup_expr='icontains')
    facility_id = filters.CharFilter(field_name="facility_id")
    facility_location = filters.CharFilter(field_name="facility_location", lookup_expr='icontains')

    class Meta:
        model = Facility
        fields = ['facility_name', 'facility_id', 'facility_location']


# Base Filter for Facility Date
class FacilityDateFilterBase(filters.FilterSet):
    facility_id = filters.CharFilter(field_name="facility__facility_id")
    facility_location = filters.CharFilter(field_name="facility__facility_location", lookup_expr='icontains')
    start_year = filters.NumberFilter(field_name="DatePicker", lookup_expr="year__gte")
    end_year = filters.NumberFilter(field_name="DatePicker", lookup_expr="year__lte")

    class Meta:
        model = Facility
        fields = ['facility_id', 'facility_location', 'start_year', 'end_year']

    def clean_years(self):
        start_year = self.data.get('start_year')
        end_year = self.data.get('end_year')
        if start_year and end_year:
            try:
                start_year, end_year = int(start_year), int(end_year)
                if start_year > end_year:
                    raise ValidationError("Start year must be less than or equal to end year.")
            except ValueError:
                raise ValidationError("Start year and end year must be valid numbers.")

    def filter_queryset(self, queryset):
        self.clean_years()

        facility_id = self.data.get('facility_id')
        if facility_id and facility_id.lower() != 'all':
            if not Facility.objects.filter(facility_id=facility_id).exists():
                raise ValidationError("Facility with the specified ID does not exist.")

        return super().filter_queryset(queryset)


# Waste Filter
class WasteFilter(FacilityDateFilterBase):
    class Meta(FacilityDateFilterBase.Meta):
        model = Waste

    def filter_queryset(self, queryset):
        facility_id = self.data.get('facility_id', 'all')

        if facility_id.lower() != 'all':
            queryset = queryset.filter(facility__facility_id=facility_id)

        start_year = self.data.get('start_year')
        end_year = self.data.get('end_year')

        if start_year and end_year:
            queryset = queryset.filter(DatePicker__year__gte=start_year, DatePicker__year__lte=end_year)

        return super().filter_queryset(queryset)


# Energy Filter
class EnergyFilter(FacilityDateFilterBase):
    class Meta(FacilityDateFilterBase.Meta):
        model = Energy

    def filter_queryset(self, queryset):
        facility_id = self.data.get('facility_id', 'all')

        if facility_id.lower() != 'all':
            queryset = queryset.filter(facility__facility_id=facility_id)

        start_year = self.data.get('start_year')
        end_year = self.data.get('end_year')

        if start_year and end_year:
            queryset = queryset.filter(DatePicker__year__gte=start_year, DatePicker__year__lte=end_year)

        return super().filter_queryset(queryset)


# Water Filter
class WaterFilter(FacilityDateFilterBase):
    class Meta(FacilityDateFilterBase.Meta):
        model = Water


# Biodiversity Filter
class BiodiversityFilter(FacilityDateFilterBase):
    class Meta(FacilityDateFilterBase.Meta):
        model = Biodiversity


# Logistics Filter
class LogisticesFilter(FacilityDateFilterBase):
    class Meta(FacilityDateFilterBase.Meta):
        model = Logistices
