import pandas as pd
from datetime import datetime
from collections import defaultdict
from django.db.models import Sum, Value, FloatField,Min, Max,F,ExpressionWrapper
from django.db.models.functions import Coalesce, Cast, ExtractMonth
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserRegisterSerializer, UserLoginSerializer,WasteSerializer,WasteCreateSerializer,EnergyCreateSerializer,OrganizationSerializer,EnergySerializer,WaterCreateSerializer,WaterSerializer,BiodiversityCreateSerializer,BiodiversitySerializer,FacilitySerializer,LogisticesSerializer
from .models import CustomUser,Waste,Energy,Water,Biodiversity,Facility,Logistices,Org_registration
from django.db.models import Q

from django.db.models import Field
from .filters import FacilityFilter, WasteFilter, EnergyFilter, WaterFilter, BiodiversityFilter, LogisticesFilter
from django_filters.rest_framework import DjangoFilterBackend
import logging

logger = logging.getLogger(__name__)
#Register View
class RegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"msg": "User registered successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#LoginView
class LoginView(APIView):
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(email=email, password=password)  # Use authenticate here
            if user is None:
                return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

            refresh = RefreshToken.for_user(user)
            response = Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
            response.set_cookie('access_token', str(refresh.access_token), httponly=True)
            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#Dashboard View
class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_data = {
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'password':request.user.password
        }
        return Response(user_data, status=status.HTTP_200_OK)

'''Organization Crud Operations Starts'''

# OrganizationCreate
class OrganizationCreate(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = OrganizationSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Organization Registration added successfully"}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# OrganizationView
class OrganizationView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        org_reg_data = Org_registration.objects.filter(user=user)
        organization_serializer = OrganizationSerializer(org_reg_data, many=True)
        user_data = {
            'email': user.email,
            'org_reg_data': organization_serializer.data
        }
        return Response(user_data, status=status.HTTP_200_OK)
'''Oragnization Crud Operations Ends'''

'''Facility Crud Operations starts'''
#FacilityCreate
class FacilityCreateView(APIView):
    permission_classes = [IsAuthenticated] 

    def post(self, request):
        serializer = FacilitySerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Facility added successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FacilityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', 'all')
        location = request.GET.get('location')
        action = request.GET.get('action')

        # Start by filtering facilities by the user
        facility_data = Facility.objects.filter(user=user)

        # Apply optional filters based on query parameters
        if facility_id.lower() != 'all':
            facility_data = facility_data.filter(facility_id=facility_id)

        if location:
            facility_data = facility_data.filter(location__icontains=location)

        if action:
            facility_data = facility_data.filter(action__icontains=action)

        # Prepare the response
        if not facility_data.exists():
            # Provide "N/A" for each field
            facility_data_response = [{
                "facility_id": "N/A",
                "facility_name": "N/A",
                "facility_head": "N/A",
                "location": "N/A",
            }]
        else:
            facility_serializer = FacilitySerializer(facility_data, many=True)
            facility_data_response = facility_serializer.data

        user_data = {
            'email': user.email,
            'facility_data': facility_data_response,
        }

        return Response(user_data, status=status.HTTP_200_OK)

class FacilityEditView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, facility_id):
        try:
            facility = Facility.objects.get(facility_id=facility_id, user=request.user)
        except Facility.DoesNotExist:
            return Response({"error": "Facility not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = FacilitySerializer(facility, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Facility updated successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#FacilityDelete
class FacilityDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, facility_id):
        if not isinstance(facility_id, str) or len(facility_id) != 8:
            return Response({"error": "Invalid facility ID provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Try to get the facility using facility_id
            facility = Facility.objects.get(facility_id=facility_id, user=request.user)
            facility.delete()
            return Response({"message": "Facility deleted successfully."}, status=status.HTTP_200_OK)
        except Facility.DoesNotExist:
            return Response({"error": "Facility not found."}, status=status.HTTP_404_NOT_FOUND)
      
'''Facility Crud Operations Ends'''


'''Waste CRUD Operations Starts'''
#Watste Create Form
class WasteCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Check if data is a list (for multiple entries) or a single object
        is_bulk = isinstance(request.data, list)
        if is_bulk:
            serializer = WasteCreateSerializer(data=request.data, many=True, context={'request': request})
        else:
            serializer = WasteCreateSerializer(data=request.data, context={'request': request})

        # Validate and save the serializer
        if serializer.is_valid():
            serializer.save()
            message = "Waste data added successfully." if not is_bulk else "All Waste entries added successfully."
            return Response({"message": message}, status=status.HTTP_201_CREATED)

        # Return validation errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class WasteView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get("facility_id", None)
        year = request.GET.get("year", None)

        try:
            # Initialize queryset for Waste data
            waste_data = Waste.objects.filter(user=user)

            # Apply filters based on query parameters
            if year:
                try:
                    year = int(year)
                    start_date = datetime(year, 4, 1)  # Financial year starts from April
                    end_date = datetime(year + 1, 3, 31)  # Ends in March next year
                    waste_data = waste_data.filter(DatePicker__range=(start_date, end_date))
                except ValueError:
                    return Response(
                        {"error": "Invalid year format. Please provide a valid year, e.g., 2023."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            if facility_id:
                waste_data = waste_data.filter(facility__facility_id=facility_id)

            # Check if data exists, otherwise return zero-filled response
            if not waste_data.exists():
                return Response(
                    {
                         "message": "No data available for the selected facility and year." if facility_id or year else "No data available.",
                            "email": user.email,
                            "waste_data": [
                                {
                                    "food_waste": 0,
                                    "solid_waste": 0,
                                    "e_waste": 0,
                                    "biomedical_waste": 0,
                                    "other_waste": 0,
                                }
                            ],
                            "overall_waste_usage_total": 0,
                    },
                    status=status.HTTP_200_OK,
                )

            # Serialize and calculate totals
            waste_data = waste_data.order_by("-DatePicker")  # Order by date, descending
            waste_serializer = WasteSerializer(waste_data, many=True)
            overall_total = sum(
                (entry.food_waste or 0) +
                (entry.solid_Waste or 0) +
                (entry.E_Waste or 0) +
                (entry.Biomedical_waste or 0) +
                (entry.other_waste or 0)
                for entry in waste_data
            )

            return Response(
                {
                    "email": user.email,
                    "waste_data": waste_serializer.data,
                    "overall_waste_usage_total": overall_total,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class WasteEditView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, waste_id):
        try:
            waste = Waste.objects.get(waste_id=waste_id, user=request.user)
        except Waste.DoesNotExist:
            return Response({"error": "Waste data not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = WasteCreateSerializer(waste, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Waste data updated successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#Deletewaste
class WasteDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, waste_id):
        try:
           waste = Waste.objects.get(waste_id=waste_id, user=request.user)
        except Waste.DoesNotExist:
            return Response({"error": "Waste data not found."}, status=status.HTTP_404_NOT_FOUND)

        waste.delete()
        return Response({"message": "Waste data deleted successfully."}, status=status.HTTP_200_OK)

'''Waste CRUD Operations Ends'''

'''Energy CRUD Operations Starts'''
#EnergyCreate
class EnergyCreateView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        is_bulk = isinstance(request.data, list)
        if is_bulk:
            serializer = EnergyCreateSerializer(data=request.data, many=True, context={'request': request})
        else:
            serializer = EnergyCreateSerializer(data=request.data,context={'request':request})
        if serializer.is_valid():
            serializer.save()
            return Response({"messages":"Energy data added Succesfully"},status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EnergyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get("facility_id", None)
        year = request.GET.get("year", None)

        try:
            # Initialize queryset for Energy data
            energy_data = Energy.objects.filter(user=user)

            # Apply filters based on query parameters
            if year:
                try:
                    year = int(year)
                    start_date = datetime(year, 4, 1)  # Financial year starts in April
                    end_date = datetime(year + 1, 3, 31)  # Ends in March next year
                    energy_data = energy_data.filter(DatePicker__range=(start_date, end_date))
                except ValueError:
                    return Response(
                        {"error": "Invalid year format. Please provide a valid year, e.g., 2023."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            if facility_id:
                energy_data = energy_data.filter(facility__facility_id=facility_id) 

            # Check if data exists, otherwise return zero-filled response
            if not energy_data.exists():
                return Response(
                    {
                        "message": (
                            "No data available for the selected facility and year."
                            if facility_id or year
                            else "No data available."
                        ),
                        "email": user.email,
                        "energy_data": [
                            {
                                "hvac": 0,
                                "production": 0,
                                "stp": 0,
                                "admin_block": 0,
                                "others": 0,
                                "admin_block":0,
                                "utilities":0,
                                "others":0,
                                "coking_coal":0,
                                "coke_oven_coal":0,
                                "natural_gas":0,
                                "diesel":0,
                                "biomass_wood": 0,
                                "biomass_other_solid": 0,
                                "renewable_solar": 0,
                                "renewable_other": 0,
                            }
                        ],
                        "overall_energy_usage_total": 0,
                    },
                    status=status.HTTP_200_OK,
                )

            # Serialize and calculate totals
            energy_data = energy_data.order_by("-DatePicker")  # Order by date, descending
            energy_serializer = EnergySerializer(energy_data, many=True)
            overall_total = sum(
                (entry.hvac or 0) +
                (entry.production or 0) +
                (entry.stp or 0) +
                (entry.admin_block or 0) +
                (entry.others or 0)
                for entry in energy_data
            )
            return Response(
                {
                    "email": user.email,
                    "energy_data": energy_serializer.data,
                    "overall_energy_usage_total": overall_total,
                },
                status=status.HTTP_200_OK,
            )

        except ValueError as e:
            return Response(
                {"error": f"Value Error: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

#EnergyEdit
class EnergyEditView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, energy_id):
        try:
            energy = Energy.objects.get(energy_id=energy_id, user=request.user)
        except Energy.DoesNotExist:
            return Response({"error": "Energy data not found."}, status=status.HTTP_404_NOT_FOUND)
        

        serializer = EnergyCreateSerializer(energy, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Energy data updated successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#EnergyDelete
class EnergyDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, energy_id):
        try:
            energy = Energy.objects.get(energy_id=energy_id, user=request.user)
        except Energy.DoesNotExist:
            return Response({"error": "Energy data not found."}, status=status.HTTP_404_NOT_FOUND)

        energy.delete()
        return Response({"message": "Energy data deleted successfully."}, status=status.HTTP_200_OK)

'''Energy CRUD Operations Ends'''

'''Water CRUD Operations Starts'''
#waterCreate
class WaterCreateView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        is_bulk = isinstance(request.data, list)
        if is_bulk:
            serializer = WaterCreateSerializer(data=request.data, many=True, context={'request': request})
        else:
            serializer = WaterCreateSerializer(data=request.data,context={'request':request})
        if serializer.is_valid():
            serializer.save()
            return Response({"messages":"Water data added succesfully"},status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

#WaterView
class WaterView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get("facility_id", None)
        year = request.GET.get("year", None)

        try:
            # Initialize queryset for Water data
            water_data = Water.objects.filter(user=user)

            # Apply filters based on query parameters
            if year:
                try:
                    year = int(year)
                    start_date = datetime(year, 4, 1)  # Financial year starts in April
                    end_date = datetime(year + 1, 3, 31)  # Ends in March next year
                    water_data = water_data.filter(DatePicker__range=(start_date, end_date))
                except ValueError:
                    return Response(
                        {"error": "Invalid year format. Please provide a valid year, e.g., 2023."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            if facility_id:
                water_data = water_data.filter(facility__facility_id=facility_id) 

            # Check if data exists, otherwise return zero-filled response
            if not water_data.exists():
                return Response(
                    {
                        "message": (
                            "No data available for the selected facility and year."
                            if facility_id or year
                            else "No data available."
                        ),
                        "email": user.email,
                        "water_data": [
                            {
                                "Generated_Water": 0,
                                "Recycled_Water": 0,
                                "Softener_usage": 0,
                                "Boiler_usage": 0,
                                "otherUsage": 0
                            }
                        ],
                        "overall_water_usage_total": 0,
                    },
                    status=status.HTTP_200_OK,
                )

            # Serialize and calculate totals
            water_data = water_data.order_by("-DatePicker")  # Order by date, descending
            water_serializer = WaterSerializer(water_data, many=True)
            overall_total = sum(water.overall_usage for water in water_data)
            return Response(
                {
                    "email": user.email,
                    "water_data": water_serializer.data,
                    "overall_water_usage_total": overall_total,
                },
                status=status.HTTP_200_OK,
            )

        except ValueError as e:
            return Response(
                {"error": f"Value Error: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


#WaterEdit
class WaterEditView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, water_id):
        try:
            water = Water.objects.get(water_id=water_id,user=request.user)
        except Water.DoesNotExist:
            return Response({"error": "Water data not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = WaterCreateSerializer(water, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Water data updated successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#WaterDelete
class WaterDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, water_id):
        try:
            water = Water.objects.get(water_id=water_id, user=request.user)
        except Water.DoesNotExist:
            return Response({"error": "Water data not found."}, status=status.HTTP_404_NOT_FOUND)

        water.delete()
        return Response({"message": "Water data deleted successfully."}, status=status.HTTP_200_OK)

'''Water CRUD Operations Ends'''

'''Biodiversity CRUD Operations Starts'''

#biodiversity Create
class BiodiversityCreateView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        is_bulk = isinstance(request.data, list)
        if is_bulk:
            serializer = BiodiversityCreateSerializer(data=request.data, many=True, context={'request': request})
        else:
            serializer = BiodiversityCreateSerializer(data=request.data,context={'request':request})
        if serializer.is_valid():
            serializer.save()
            return Response({'messages':'Biodiversity data added Succesfully'},status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
#biodiversity View  
class BiodiversityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get("facility_id", None)
        year = request.GET.get("year", None)

        try:
            # Initialize queryset for Biodiversity data
            biodiversity_data = Biodiversity.objects.filter(user=user)

            # Apply year filter if provided
            if year:
                try:
                    year = int(year)
                    start_date = datetime(year, 4, 1)  # Fiscal year starts in April
                    end_date = datetime(year + 1, 3, 31)  # Ends in March next year
                    biodiversity_data = biodiversity_data.filter(DatePicker__range=(start_date, end_date))
                except ValueError:
                    return Response(
                        {"error": "Invalid year format. Please provide a valid year, e.g., 2023."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # Apply facility filter if provided
            if facility_id:
                biodiversity_data = biodiversity_data.filter(facility__facility_id=facility_id)

            # Check if data exists, otherwise return zero-filled response
            if not biodiversity_data.exists():
                empty_fields = {
                    "no_trees": 0,
                    "species": 0,
                    "age": 0,
                    "height": 0,
                    "width":0,
                    "totalArea":0,
                    "new_trees_planted":0,
                    "head_count":0
                }
                return Response(
                    {
                        "message": (
                            "No data available for the selected facility and fiscal year."
                            if facility_id or year
                            else "No data available."
                        ),
                        "email": user.email,
                        "biodiversity_data": [empty_fields],
                        "overall_biodiversity_usage_total": 0,
                    },
                    status=status.HTTP_200_OK,
                )

            # Serialize and calculate totals
            biodiversity_data = biodiversity_data.order_by("-DatePicker")  # Order by date, descending
            biodiversity_serializer = BiodiversitySerializer(biodiversity_data, many=True)
            serialized_data = biodiversity_serializer.data

            # Add facility ID to serialized data
            for data, biodiversity in zip(serialized_data, biodiversity_data):
                data["facility_id"] = biodiversity.facility.facility_id

            # Calculate overall totals
            overall_total = sum(biodiversity.no_trees for biodiversity in biodiversity_data)

            return Response(
                {
                    "email": user.email,
                    "biodiversity_data": serialized_data,
                    "overall_biodiversity_usage_total": overall_total,
                },
                status=status.HTTP_200_OK,
            )

        except ValueError as e:
            return Response(
                {"error": f"Value Error: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

 
#BiodiversityEdit
class BiodiversityEditView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, biodiversity_id):
        try:
            biodiversity = Biodiversity.objects.get(biodiversity_id=biodiversity_id, user=request.user)
        except Biodiversity.DoesNotExist:
            return Response({"error": "Biodiversity data not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = BiodiversityCreateSerializer(biodiversity, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Biodiversity data updated successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#BiodiversityDelete
class BiodiversityDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, biodiversity_id):
        try:
            biodiversity = Biodiversity.objects.get(biodiversity_id=biodiversity_id, user=request.user)
        except Biodiversity.DoesNotExist:
            return Response({"error": "Biodiversity data not found."}, status=status.HTTP_404_NOT_FOUND)

        biodiversity.delete()
        return Response({"message": "Biodiversity data deleted successfully."}, status=status.HTTP_200_OK)

'''Biodiversity CRUD Operations Ends'''


'''Logistices CRUD Operations Starts'''
#Logistices Create Form
class LogisticesCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        is_bulk = isinstance(request.data, list)
        data = request.data if is_bulk else [request.data]
        validated_data_list = []

        # Check for duplicates within the incoming data
        seen = set()
        for entry in data:
            key = (
                entry.get('facility_id'),
                entry.get('DatePicker'),
                entry.get('logistices_types'),
                entry.get('Typeof_fuel'),
            )
            if key in seen:
                return Response(
                    {"non_field_errors": "Duplicate entries detected in the submitted data."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            seen.add(key)

        # Validate and save
        serializer = LogisticesSerializer(data=data, many=True, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({"message": "Logistices data added successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#View Logistices
class LogisticesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        year = request.GET.get('year', None)

        try:
            # Initialize queryset for Logistices data
            logistices_data = Logistices.objects.filter(user=user)

            # Apply year filter if provided
            if year:
                try:
                    year = int(year)
                    start_date = datetime(year, 4, 1)  # Fiscal year starts in April
                    end_date = datetime(year + 1, 3, 31)  # Ends in March next year
                    logistices_data = logistices_data.filter(DatePicker__range=(start_date, end_date))
                except ValueError:
                    return Response(
                        {"error": "Invalid year format. Please provide a valid year, e.g., 2023."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # Apply facility filter if provided
            if facility_id:
                logistices_data = logistices_data.filter(facility__facility_id=facility_id)

            # Check if data exists, otherwise return zero-filled response
            if not logistices_data.exists():
                empty_fields = {
                    "facility_id": "N/A",
                    "logistices_types": "N/A",
                    "Typeof_fuel": "N/A",
                    "km_travelled": 0,
                    "No_Trips": 0,
                    "fuel_consumption": 0,
                    "No_Vehicles": 0,
                    "Spends_on_fuel": 0,
                }
                return Response(
                    {
                        "message": (
                            "No data available for the selected facility and year."
                            if facility_id or year
                            else "No data available."
                        ),
                        "email": user.email,
                        "logistices_data": [empty_fields],
                        "overall_logistices_usage_total": 0,
                    },
                    status=status.HTTP_200_OK,
                )

            # Serialize and calculate totals
            logistices_data = logistices_data.order_by("-DatePicker")  # Order by date, descending
            logistices_serializer = LogisticesSerializer(logistices_data, many=True)

            # Add facility ID to serialized data
            serialized_data = logistices_serializer.data
            for data, logistices in zip(serialized_data, logistices_data):
                data["facility_id"] = logistices.facility.facility_id

            # Calculate overall total fuel consumption
            overall_fuel_consumption = sum(
                logistices.fuel_consumption for logistices in logistices_data
            )

            return Response(
                {
                    "email": user.email,
                    "logistices_data": serialized_data,
                    "overall_logistices_usage_total": overall_fuel_consumption,
                },
                status=status.HTTP_200_OK,
            )

        except ValueError as e:
            return Response(
                {"error": f"Value Error: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

#Edit Logistices
class LogisticesEditView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, logistices_id):
        try:
            # Retrieve the instance to update
            logistices = Logistices.objects.get(logistices_id=logistices_id, user=request.user)
        except Logistices.DoesNotExist:
            return Response({"error": "Logistices entry not found."}, status=status.HTTP_404_NOT_FOUND)

        # Initialize the serializer with the instance and request data
        serializer = LogisticesSerializer(logistices, data=request.data, context={'request': request})

        # Validate and save
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Logistices data updated successfully."}, status=status.HTTP_200_OK)
        else:
            # Return detailed validation errors
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

#Delete Logistices
class LogisticesDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, logistices_id):
        try:
            logistices = Logistices.objects.get(logistices_id=logistices_id, user=request.user)
        except Logistices.DoesNotExist:
            return Response({"error": "Logistices data not found."}, status=status.HTTP_404_NOT_FOUND)

        logistices.delete()
        return Response({"message": "Logistices data deleted successfully."}, status=status.HTTP_200_OK)

'''Logistices CRUD Operations Ends'''

#Logout View
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        access_token = request.COOKIES.get('access_token')
        refresh_token = request.COOKIES.get('refresh_token')

        if not access_token or not refresh_token:
            return Response(
                {"error": "No active session or tokens found to logout."},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
           
            token = RefreshToken(refresh_token)
            token.blacklist() 
        except Exception as e:
            return Response(
                {"error": "Error logging out. Invalid or expired tokens."},
                status=status.HTTP_400_BAD_REQUEST
            )

        response = Response({"message": "Logout successful"}, status=status.HTTP_205_RESET_CONTENT)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')

        return response
    
    
'''OverViwe of allTotal_Usages '''

def calculate_emissions(monthly_energy, monthly_water, monthly_waste, monthly_logistices, yearly_biodiversity):
    electricity_factor = 0.82
    fuel_factors = {
        'coking_coal': 2.66,
        'coke_oven_coal': 3.1,
        'natural_gas': 2.7,
        'diesel': 2.91 * 1000,
        'biomass_wood': 1.75,
        'biomass_other_solid': 1.16,
    }
    petrol_factor = 2.29 * 1000
    diesel_factor = 2.91 * 1000

    electricity_emissions = (
        monthly_energy.aggregate(
            total=Coalesce(
                Sum(
                    F('hvac') + F('production') + F('stp') +
                    F('admin_block') + F('utilities') + F('others'),
                    output_field=FloatField()
                ),
                0.0
            )
        )['total'] or 0.0
    ) * electricity_factor

    fuel_emissions = sum([
        (monthly_energy.aggregate(total=Sum(F(fuel), output_field=FloatField()))['total'] or 0) * factor
        for fuel, factor in fuel_factors.items()
    ])

    water_emissions = (
        monthly_water.aggregate(
            total=Coalesce(
                Sum(
                    F('Generated_Water') + F('Recycled_Water') +
                    F('Softener_usage') + F('Boiler_usage') + F('otherUsage'),
                    output_field=FloatField()
                ),
                0.0
            )
        )['total'] or 0.0
    ) * 0.46

    waste_emissions = sum([
        (monthly_waste.aggregate(total=Sum(F('Landfill_waste'), output_field=FloatField()))['total'] or 0) * 300,
        (monthly_waste.aggregate(total=Sum(F('Recycle_waste'), output_field=FloatField()))['total'] or 0) * 10,
    ])

    logistices_emissions = sum([
        (monthly_logistices.filter(Typeof_fuel='diesel').aggregate(total=Sum(F('fuel_consumption'), output_field=FloatField()))['total'] or 0) * diesel_factor,
        (monthly_logistices.filter(Typeof_fuel='petrol').aggregate(total=Sum(F('fuel_consumption'), output_field=FloatField()))['total'] or 0) * petrol_factor,
    ])

    total_emissions = (
        electricity_emissions +
        fuel_emissions +
        water_emissions +
        waste_emissions +
        logistices_emissions
    )

    return total_emissions

class OverallUsageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', 'all').lower()
        year = request.GET.get('year')

        # Handle year input
        try:
            year = int(year) if year else None
        except ValueError:
            return Response(
                {"error": "Invalid fiscal year format. Provide a valid year, e.g., 2023."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Determine the fiscal year range
        if not year:
            # Fetch the latest year across all models for the user
            latest_date = max(
                [
                    Waste.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date'],
                    Energy.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date'],
                    Water.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date'],
                    Logistices.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date'],
                    Biodiversity.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date'],
                ],
                default=None,
                key=lambda d: d and datetime.combine(d, datetime.min.time()) or datetime.min  # Handle None and convert to datetime
            )

            if latest_date:
                year = latest_date.year if latest_date.month >= 4 else latest_date.year - 1
            else:
                year = datetime.now().year
                
        start_date = datetime(year, 4, 1)
        end_date = datetime(year + 1, 3, 31)

        # Build filters
        filters = {'user': user, 'DatePicker__range': (start_date, end_date)}
        if facility_id != 'all':
            filters['facility__facility_id'] = facility_id

        # Fetch data
        waste_data = Waste.objects.filter(**filters)
        energy_data = Energy.objects.filter(**filters)
        water_data = Water.objects.filter(**filters)
        logistices_data = Logistices.objects.filter(**filters)
        
        # Apply facility_id filter to Biodiversity if it's not "all"
        biodiversity_filters = {'user': user, 'DatePicker__year': year}
        if facility_id != 'all':
            biodiversity_filters['facility__facility_id'] = facility_id
        yearly_biodiversity = Biodiversity.objects.filter(**biodiversity_filters)

        # Calculate total emissions
        total_emissions = 0
        for month in [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]:
            monthly_energy = energy_data.filter(DatePicker__month=month)
            monthly_water = water_data.filter(DatePicker__month=month)
            monthly_waste = waste_data.filter(DatePicker__month=month)
            monthly_logistices = logistices_data.filter(DatePicker__month=month)

            total_emissions += calculate_emissions(
                monthly_energy, monthly_water, monthly_waste, monthly_logistices, yearly_biodiversity
            )

        # Prepare response data with rounded values
        response_data = {
            "email": user.email,
            "year": year,
            "facility_id": facility_id if facility_id != 'all' else "All facilities",
            "overall_data": {
                "waste_usage": round(waste_data.aggregate(total=Sum('overall_usage'))['total'] or 0.0, 2),
                "energy_usage": round(energy_data.aggregate(total=Sum('overall_usage'))['total'] or 0.0, 2),
                "water_usage": round(water_data.aggregate(total=Sum('overall_usage'))['total'] or 0.0, 2),
                "biodiversity_usage": round(yearly_biodiversity.aggregate(total=Sum('overall_Trees'))['total'] or 0.0, 2),
                "logistices_usage": round(logistices_data.aggregate(total=Sum('total_fuelconsumption'))['total'] or 0.0, 2),
                "total_emissions": round(total_emissions, 2),
            },
        }

        return Response(response_data, status=status.HTTP_200_OK)

'''OverViwe of allTotal_Usages'''
    
'''Waste Overviewgraphs and Individual Line charts and donut charts Starts'''

class WasteViewCard_Over(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', 'all')
        facility_location = request.GET.get('facility_location')
        year = request.GET.get('year')

        try:
            if facility_id != 'all' and not Facility.objects.filter(facility_id=facility_id, user=user).exists():
                return Response({'error': 'Invalid facility ID or not associated with the logged-in user.'}, status=status.HTTP_400_BAD_REQUEST)

            if year:
                try:
                    year = int(year)
                    if year < 1900 or year > datetime.now().year + 10:
                        return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)
                except ValueError:
                    return Response({'error': 'Year must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Find the latest year across all models (Water, Waste, etc.)
                latest_water_date = Water.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_waste_date = Waste.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_energy_date = Energy.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_biodiversity_date = Biodiversity.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_logistices_date = Logistices.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                
                
                latest_date = max(filter(None, [latest_water_date, latest_waste_date,latest_energy_date,latest_biodiversity_date,latest_logistices_date]), default=None)
                
                if latest_date:
                    year = latest_date.year if latest_date.month >= 4 else latest_date.year - 1
                else:
                    # Default to the current fiscal year if no data exists
                    today = datetime.now()
                    year = today.year - 1 if today.month < 4 else today.year

            start_date = datetime(year, 4, 1)
            end_date = datetime(year + 1, 3, 31)

            # Query waste data
            waste_data = Waste.objects.filter(user=user, DatePicker__range=(start_date, end_date))

            # Apply specific facility filter if provided
            if facility_id != 'all':
                waste_data = waste_data.filter(facility__facility_id=facility_id)

            # Apply facility location filter if provided
            if facility_location:
                waste_data = waste_data.filter(facility__location__icontains=facility_location)

            # If no data is found, create a structure with zeros
            waste_fields = [
                'food_waste', 'solid_Waste', 'E_Waste', 'Biomedical_waste',
                'liquid_discharge', 'other_waste', 'Recycle_waste', 'Landfill_waste'
            ]

            response_data = {
                'year': year,
                'overall_waste_totals': {},
                'facility_waste_data': {}
            }

            if not waste_data.exists():
                # Populate zero values when no data exists
                for field in waste_fields:
                    response_data['overall_waste_totals'][f"overall_{field}"] = 0
                    response_data['facility_waste_data'][field] = []
            else:
                for field in waste_fields:
                    # Facility-specific totals
                    facility_waste_data = (
                        waste_data
                        .values('facility__facility_name')
                        .annotate(total=Sum(field))
                        .order_by('-total')
                    )

                    response_data['facility_waste_data'][field] = [
                        {
                            "facility_name": entry['facility__facility_name'],
                            f"total_{field}": entry['total']
                        }
                        for entry in facility_waste_data
                    ]

                    # Overall totals
                    overall_total = waste_data.aggregate(total=Sum(field))['total'] or 0
                    response_data['overall_waste_totals'][f"overall_{field}"] = overall_total

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            print(error_message)
            return Response({'error': error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#FoodWaste
class FoodWasteOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        try:
            # Determine year
            if year:
                try:
                    year = int(year)
                    if year < 1900 or year > datetime.now().year + 10:
                        return Response({'error': 'Invalid year parameter.'}, status=400)
                except ValueError:
                    return Response({'error': 'Year must be an integer.'}, status=400)
            else:
                year = self.get_latest_available_year(user)

            start_date, end_date = self.get_fiscal_year_range(year)

            # Build filters
            filters = {
                'user': user,
                'DatePicker__range': (start_date.date(), end_date.date())
            }
            if facility_id and facility_id.lower() != 'all':
                filters['facility__facility_id'] = facility_id
            if facility_location:
                filters['facility__location__icontains'] = facility_location

            # Query filtered data
            waste_data = Waste.objects.filter(**filters)
            if not waste_data.exists():
                return self.get_empty_response(year)

            # Line chart data: monthly food waste
            monthly_food_waste = (
                waste_data
                .values('DatePicker__month')
                .annotate(total_food_waste=Sum('food_waste'))
            )

            food_waste = {month: 0 for month in range(1, 13)}
            for entry in monthly_food_waste:
                food_waste[entry['DatePicker__month']] = entry['total_food_waste']

            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            line_chart_data = [
                {
                    "month": datetime(1900, month, 1).strftime('%b'),
                    "food_waste": food_waste[month]
                }
                for month in month_order
            ]

            # Donut chart data: facility contribution
            facility_food_waste = (
                waste_data
                .values('facility__facility_name')
                .annotate(total_food_waste=Sum('food_waste'))
                .order_by('-total_food_waste')
            )

            total_food_waste = sum(entry['total_food_waste'] for entry in facility_food_waste)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_food_waste'] / total_food_waste * 100) if total_food_waste else 0,
                }
                for entry in facility_food_waste
            ]

            # Construct response
            response_data = {
                "year": year,
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': f'An error occurred while processing your request: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_latest_available_year(self, user):
        # Find the latest date across all models
        latest_water_date = Water.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_waste_date = Waste.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_energy_date = Energy.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_biodiversity_date = Biodiversity.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_logistices_date = Logistices.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']

        latest_date = max(
            filter(None, [latest_water_date, latest_waste_date, latest_energy_date, latest_biodiversity_date, latest_logistices_date]),
            default=None
        )

        if latest_date:
            return latest_date.year if latest_date.month >= 4 else latest_date.year - 1
        today = datetime.now()
        return today.year - 1 if today.month < 4 else today.year

    def get_fiscal_year_range(self, year):
        start_date = datetime(year, 4, 1)
        end_date = datetime(year + 1, 3, 31)
        return start_date, end_date

    def get_empty_response(self, year):
        month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
        line_chart_data = [{"month": datetime(1900, month, 1).strftime('%b'), "food_waste": 0} for month in month_order]
        donut_chart_data = [{"facility_name": "No Facility", "percentage": 0}]
        return Response({
            "year": year,
            "line_chart_data": line_chart_data,
            "donut_chart_data": donut_chart_data
        }, status=status.HTTP_200_OK)

#SolidWaste
class SolidWasteOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        try:
            # Determine year
            if year:
                try:
                    year = int(year)
                    if year < 1900 or year > datetime.now().year + 10:
                        return Response({'error': 'Invalid year parameter.'}, status=400)
                except ValueError:
                    return Response({'error': 'Year must be an integer.'}, status=400)
            else:
                year = self.get_latest_available_year(user)

            start_date, end_date = self.get_fiscal_year_range(year)




            filters = {
                'user': user,
                'DatePicker__range': (start_date.date(), end_date.date())
            }
            if facility_id and facility_id.lower() != 'all':
                filters['facility__facility_id'] = facility_id
            if facility_location:
                filters['facility__location__icontains'] = facility_location

            waste_data = Waste.objects.filter(**filters)
            if not waste_data.exists():
                return self.get_empty_response(year)

            monthly_solid_Waste = (
                waste_data
                .values('DatePicker__month')
                .annotate(total_solid_Waste=Sum('solid_Waste'))
            )

            solid_Waste = {month: 0 for month in range(1, 13)}
            for entry in monthly_solid_Waste:
                solid_Waste[entry['DatePicker__month']] = entry['total_solid_Waste']

            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            line_chart_data = [
                {
                    "month": datetime(1900, month, 1).strftime('%b'),
                    "solid_Waste": solid_Waste[month]
                }
                for month in month_order
            ]

            # Prepare facility data for donut chart
            facility_solid_Waste = (
                waste_data
                .values('facility__facility_name')
                .annotate(total_solid_Waste=Sum('solid_Waste'))
                .order_by('-total_solid_Waste')
            )

            total_solid_Waste = sum(entry['total_solid_Waste'] for entry in facility_solid_Waste)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_solid_Waste'] / total_solid_Waste * 100) if total_solid_Waste else 0,
                }
                for entry in facility_solid_Waste
            ]

            response_data = {
                "year": year,
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            print(f"Error: {str(e)}")
            print("Traceback:", traceback.format_exc())
            return Response(
                {'error': f'An error occurred while processing your request: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_latest_available_year(self, user):
        # Find the latest date across all models
        latest_water_date = Water.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_waste_date = Waste.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_energy_date = Energy.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_biodiversity_date = Biodiversity.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_logistices_date = Logistices.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']

        latest_date = max(
            filter(None, [latest_water_date, latest_waste_date, latest_energy_date, latest_biodiversity_date, latest_logistices_date]),
            default=None
        )

        if latest_date:
            return latest_date.year if latest_date.month >= 4 else latest_date.year - 1
        today = datetime.now()
        return today.year - 1 if today.month < 4 else today.year
    
    def get_fiscal_year_range(self, year):
        start_date = datetime(year, 4, 1)
        end_date = datetime(year + 1, 3, 31)
        return start_date, end_date

    def get_empty_response(self, year):
        month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
        line_chart_data = [{"month": datetime(1900, month, 1).strftime('%b'), "solid_waste": 0} for month in month_order]
        donut_chart_data = [{"facility_name": "No Facility", "percentage": 0}]
        return Response({
            "year": year,
            "line_chart_data": line_chart_data,
            "donut_chart_data": donut_chart_data
        }, status=status.HTTP_200_OK)

#e_waste overview view
class E_WasteOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        try:
            if year:
                try:
                    year = int(year)
                    if year < 1900 or year > datetime.now().year + 10:
                        return Response({'error': 'Invalid year parameter.'}, status=400)
                except ValueError:
                    return Response({'error': 'Year must be an integer.'}, status=400)
            else:
                year = self.get_latest_available_year(user)

            start_date, end_date = self.get_fiscal_year_range(year)


            filters = {
                'user': user,
                'DatePicker__range': (start_date.date(), end_date.date())
            }
            if facility_id and facility_id.lower() != 'all':
                filters['facility__facility_id'] = facility_id
            if facility_location:
                filters['facility__location__icontains'] = facility_location

            waste_data = Waste.objects.filter(**filters)
            if not waste_data.exists():
                return self.get_empty_response(year)

            monthly_E_Waste = (
                waste_data
                .values('DatePicker__month')
                .annotate(total_E_Waste=Sum('E_Waste'))
            )

            E_Waste = {month: 0 for month in range(1, 13)}
            for entry in monthly_E_Waste:
                E_Waste[entry['DatePicker__month']] = entry['total_E_Waste']

            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            line_chart_data = [
                {
                    "month": datetime(1900, month, 1).strftime('%b'),
                    "E_Waste": E_Waste[month]
                }
                for month in month_order
            ]

            # Prepare facility data for donut chart
            facility_E_Waste = (
                waste_data
                .values('facility__facility_name')
                .annotate(total_E_Waste=Sum('E_Waste'))
                .order_by('-total_E_Waste')
            )

            total_E_Waste = sum(entry['total_E_Waste'] for entry in facility_E_Waste)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_E_Waste'] / total_E_Waste * 100) if total_E_Waste else 0,
                }
                for entry in facility_E_Waste
            ]

            response_data = {
                "year": year,
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            print(f"Error: {str(e)}")
            print("Traceback:", traceback.format_exc())
            return Response(
                {'error': f'An error occurred while processing your request: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_latest_available_year(self, user):
        # Find the latest date across all models
        latest_water_date = Water.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_waste_date = Waste.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_energy_date = Energy.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_biodiversity_date = Biodiversity.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_logistices_date = Logistices.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']

        latest_date = max(
            filter(None, [latest_water_date, latest_waste_date, latest_energy_date, latest_biodiversity_date, latest_logistices_date]),
            default=None
        )

        if latest_date:
            return latest_date.year if latest_date.month >= 4 else latest_date.year - 1
        today = datetime.now()
        return today.year - 1 if today.month < 4 else today.year

    def get_fiscal_year_range(self, year):
        start_date = datetime(year, 4, 1)
        end_date = datetime(year + 1, 3, 31)
        return start_date, end_date

    def get_empty_response(self, year):
        month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
        line_chart_data = [{"month": datetime(1900, month, 1).strftime('%b'), "E_Waste": 0} for month in month_order]
        donut_chart_data = [{"facility_name": "No Facility", "percentage": 0}]
        return Response({
            "year": year,
            "line_chart_data": line_chart_data,
            "donut_chart_data": donut_chart_data
        }, status=status.HTTP_200_OK)

#biomedical_waste Overview
class Biomedical_WasteOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        try:
            if year:
                try:
                    year = int(year)
                    if year < 1900 or year > datetime.now().year + 10:
                        return Response({'error': 'Invalid year parameter.'}, status=400)
                except ValueError:
                    return Response({'error': 'Year must be an integer.'}, status=400)
            else:
                year = self.get_latest_available_year(user)

            start_date, end_date = self.get_fiscal_year_range(year)


            filters = {
                'user': user,
                'DatePicker__range': (start_date.date(), end_date.date())
            }
            if facility_id and facility_id.lower() != 'all':
                filters['facility__facility_id'] = facility_id
            if facility_location:
                filters['facility__location__icontains'] = facility_location

            waste_data = Waste.objects.filter(**filters)
            if not waste_data.exists():
                return self.get_empty_response(year)

            monthly_Biomedical_waste = (
                waste_data
                .values('DatePicker__month')
                .annotate(total_Biomedical_waste=Sum('Biomedical_waste'))
            )

            Biomedical_waste = {month: 0 for month in range(1, 13)}
            for entry in monthly_Biomedical_waste:
                Biomedical_waste[entry['DatePicker__month']] = entry['total_Biomedical_waste']

            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            line_chart_data = [
                {
                    "month": datetime(1900, month, 1).strftime('%b'),
                    "Biomedical_waste": Biomedical_waste[month]
                }
                for month in month_order
            ]

            # Prepare facility data for donut chart
            facility_Biomedical_waste = (
                waste_data
                .values('facility__facility_name')
                .annotate(total_Biomedical_waste=Sum('Biomedical_waste'))
                .order_by('-total_Biomedical_waste')
            )

            total_Biomedical_waste = sum(entry['total_Biomedical_waste'] for entry in facility_Biomedical_waste)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_Biomedical_waste'] / total_Biomedical_waste * 100) if total_Biomedical_waste else 0,
                }
                for entry in facility_Biomedical_waste
            ]

            response_data = {
                "year": year,
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            print(f"Error: {str(e)}")
            print("Traceback:", traceback.format_exc())
            return Response(
                {'error': f'An error occurred while processing your request: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_latest_available_year(self, user):
        # Find the latest date across all models
        latest_water_date = Water.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_waste_date = Waste.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_energy_date = Energy.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_biodiversity_date = Biodiversity.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_logistices_date = Logistices.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']

        latest_date = max(
            filter(None, [latest_water_date, latest_waste_date, latest_energy_date, latest_biodiversity_date, latest_logistices_date]),
            default=None
        )

        if latest_date:
            return latest_date.year if latest_date.month >= 4 else latest_date.year - 1
        today = datetime.now()
        return today.year - 1 if today.month < 4 else today.year

    def get_fiscal_year_range(self, year):
        start_date = datetime(year, 4, 1)
        end_date = datetime(year + 1, 3, 31)
        return start_date, end_date

    def get_empty_response(self, year):
        month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
        line_chart_data = [{"month": datetime(1900, month, 1).strftime('%b'), "Biomedical_waste": 0} for month in month_order]
        donut_chart_data = [{"facility_name": "No Facility", "percentage": 0}]
        return Response({
            "year": year,
            "line_chart_data": line_chart_data,
            "donut_chart_data": donut_chart_data
        }, status=status.HTTP_200_OK)

#Liquid_DischargeOverviewView
class Liquid_DischargeOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        try:
            if year:
                try:
                    year = int(year)
                    if year < 1900 or year > datetime.now().year + 10:
                        return Response({'error': 'Invalid year parameter.'}, status=400)
                except ValueError:
                    return Response({'error': 'Year must be an integer.'}, status=400)
            else:
                year = self.get_latest_available_year(user)

            start_date, end_date = self.get_fiscal_year_range(year)


            filters = {
                'user': user,
                'DatePicker__range': (start_date.date(), end_date.date())
            }
            if facility_id and facility_id.lower() != 'all':
                filters['facility__facility_id'] = facility_id
            if facility_location:
                filters['facility__location__icontains'] = facility_location

            waste_data = Waste.objects.filter(**filters)
            if not waste_data.exists():
                return self.get_empty_response(year)

            monthly_liquid_discharge = (
                waste_data
                .values('DatePicker__month')
                .annotate(total_liquid_discharge=Sum('liquid_discharge'))
            )

            liquid_discharge = {month: 0 for month in range(1, 13)}
            for entry in monthly_liquid_discharge:
                liquid_discharge[entry['DatePicker__month']] = entry['total_liquid_discharge']

            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            line_chart_data = [
                {
                    "month": datetime(1900, month, 1).strftime('%b'),
                    "liquid_discharge": liquid_discharge[month]
                }
                for month in month_order
            ]

            # Prepare facility data for donut chart
            facility_liquid_discharge = (
                waste_data
                .values('facility__facility_name')
                .annotate(total_liquid_discharge=Sum('liquid_discharge'))
                .order_by('-total_liquid_discharge')
            )

            total_liquid_discharge = sum(entry['total_liquid_discharge'] for entry in facility_liquid_discharge)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_liquid_discharge'] / total_liquid_discharge * 100) if total_liquid_discharge else 0,
                }
                for entry in facility_liquid_discharge
            ]

            response_data = {
                "year": year,
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            print(f"Error: {str(e)}")
            print("Traceback:", traceback.format_exc())
            return Response(
                {'error': f'An error occurred while processing your request: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_latest_available_year(self, user):
        # Find the latest date across all models
        latest_water_date = Water.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_waste_date = Waste.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_energy_date = Energy.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_biodiversity_date = Biodiversity.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_logistices_date = Logistices.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']

        latest_date = max(
            filter(None, [latest_water_date, latest_waste_date, latest_energy_date, latest_biodiversity_date, latest_logistices_date]),
            default=None
        )

        if latest_date:
            return latest_date.year if latest_date.month >= 4 else latest_date.year - 1
        today = datetime.now()
        return today.year - 1 if today.month < 4 else today.year
    def get_fiscal_year_range(self, year):
        start_date = datetime(year, 4, 1)
        end_date = datetime(year + 1, 3, 31)
        return start_date, end_date

    def get_empty_response(self, year):
        month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
        line_chart_data = [{"month": datetime(1900, month, 1).strftime('%b'), "liquid_discharge": 0} for month in month_order]
        donut_chart_data = [{"facility_name": "No Facility", "percentage": 0}]
        return Response({
            "year": year,
            "line_chart_data": line_chart_data,
            "donut_chart_data": donut_chart_data
        }, status=status.HTTP_200_OK)

#OtherOverview
class OthersOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        try:
            if year:
                try:
                    year = int(year)
                    if year < 1900 or year > datetime.now().year + 10:
                        return Response({'error': 'Invalid year parameter.'}, status=400)
                except ValueError:
                    return Response({'error': 'Year must be an integer.'}, status=400)
            else:
                year = self.get_latest_available_year(user)

            start_date, end_date = self.get_fiscal_year_range(year)


            filters = {
                'user': user,
                'DatePicker__range': (start_date.date(), end_date.date())
            }
            if facility_id and facility_id.lower() != 'all':
                filters['facility__facility_id'] = facility_id
            if facility_location:
                filters['facility__location__icontains'] = facility_location

            waste_data = Waste.objects.filter(**filters)
            if not waste_data.exists():
                return self.get_empty_response(year)

            monthly_other_waste = (
                waste_data
                .values('DatePicker__month')
                .annotate(total_other_waste=Sum('other_waste'))
            )

            other_waste = {month: 0 for month in range(1, 13)}
            for entry in monthly_other_waste:
                other_waste[entry['DatePicker__month']] = entry['total_other_waste']

            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            line_chart_data = [
                {
                    "month": datetime(1900, month, 1).strftime('%b'),
                    "other_waste": other_waste[month]
                }
                for month in month_order
            ]

            # Prepare facility data for donut chart
            facility_other_waste = (
                waste_data
                .values('facility__facility_name')
                .annotate(total_other_waste=Sum('other_waste'))
                .order_by('-total_other_waste')
            )

            total_other_waste = sum(entry['total_other_waste'] for entry in facility_other_waste)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_other_waste'] / total_other_waste * 100) if total_other_waste else 0,
                }
                for entry in facility_other_waste
            ]

            response_data = {
                "year": year,
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            print(f"Error: {str(e)}")
            print("Traceback:", traceback.format_exc())
            return Response(
                {'error': f'An error occurred while processing your request: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_latest_available_year(self, user):
        # Find the latest date across all models
        latest_water_date = Water.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_waste_date = Waste.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_energy_date = Energy.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_biodiversity_date = Biodiversity.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_logistices_date = Logistices.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']

        latest_date = max(
            filter(None, [latest_water_date, latest_waste_date, latest_energy_date, latest_biodiversity_date, latest_logistices_date]),
            default=None
        )

        if latest_date:
            return latest_date.year if latest_date.month >= 4 else latest_date.year - 1
        today = datetime.now()
        return today.year - 1 if today.month < 4 else today.year 

    def get_fiscal_year_range(self, year):
        start_date = datetime(year, 4, 1)
        end_date = datetime(year + 1, 3, 31)
        return start_date, end_date

    def get_empty_response(self, year):
        month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
        line_chart_data = [{"month": datetime(1900, month, 1).strftime('%b'), "other_waste": 0} for month in month_order]
        donut_chart_data = [{"facility_name": "No Facility", "percentage": 0}]
        return Response({
            "year": year,
            "line_chart_data": line_chart_data,
            "donut_chart_data": donut_chart_data
        }, status=status.HTTP_200_OK)

#Sent for RecycleOverview
class Waste_Sent_For_RecycleOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        try:
            if year:
                try:
                    year = int(year)
                    if year < 1900 or year > datetime.now().year + 10:
                        return Response({'error': 'Invalid year parameter.'}, status=400)
                except ValueError:
                    return Response({'error': 'Year must be an integer.'}, status=400)
            else:
                year = self.get_latest_available_year(user)

            start_date, end_date = self.get_fiscal_year_range(year)


            filters = {
                'user': user,
                'DatePicker__range': (start_date.date(), end_date.date())
            }
            if facility_id and facility_id.lower() != 'all':
                filters['facility__facility_id'] = facility_id
            if facility_location:
                filters['facility__location__icontains'] = facility_location

            waste_data = Waste.objects.filter(**filters)
            if not waste_data.exists():
                return self.get_empty_response(year)

            monthly_Recycle_waste = (
                waste_data
                .values('DatePicker__month')
                .annotate(total_Recycle_waste=Sum('Recycle_waste'))
            )

            Recycle_waste = {month: 0 for month in range(1, 13)}
            for entry in monthly_Recycle_waste:
                Recycle_waste[entry['DatePicker__month']] = entry['total_Recycle_waste']

            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            line_chart_data = [
                {
                    "month": datetime(1900, month, 1).strftime('%b'),
                    "Recycle_waste": Recycle_waste[month]
                }
                for month in month_order
            ]

            # Prepare facility data for donut chart
            facility_Recycle_waste = (
                waste_data
                .values('facility__facility_name')
                .annotate(total_Recycle_waste=Sum('Recycle_waste'))
                .order_by('-total_Recycle_waste')
            )

            total_Recycle_waste = sum(entry['total_Recycle_waste'] for entry in facility_Recycle_waste)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_Recycle_waste'] / total_Recycle_waste * 100) if total_Recycle_waste else 0,
                }
                for entry in facility_Recycle_waste
            ]

            response_data = {
                "year": year,
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            print(f"Error: {str(e)}")
            print("Traceback:", traceback.format_exc())
            return Response(
                {'error': f'An error occurred while processing your request: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_latest_available_year(self, user):
        # Find the latest date across all models
        latest_water_date = Water.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_waste_date = Waste.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_energy_date = Energy.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_biodiversity_date = Biodiversity.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_logistices_date = Logistices.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']

        latest_date = max(
            filter(None, [latest_water_date, latest_waste_date, latest_energy_date, latest_biodiversity_date, latest_logistices_date]),
            default=None
        )

        if latest_date:
            return latest_date.year if latest_date.month >= 4 else latest_date.year - 1
        today = datetime.now()
        return today.year - 1 if today.month < 4 else today.year
    def get_fiscal_year_range(self, year):
        start_date = datetime(year, 4, 1)
        end_date = datetime(year + 1, 3, 31)
        return start_date, end_date

    def get_empty_response(self, year):
        month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
        line_chart_data = [{"month": datetime(1900, month, 1).strftime('%b'), "Recycle_waste": 0} for month in month_order]
        donut_chart_data = [{"facility_name": "No Facility", "percentage": 0}]
        return Response({
            "year": year,
            "line_chart_data": line_chart_data,
            "donut_chart_data": donut_chart_data
        }, status=status.HTTP_200_OK)

#Sent For LandFill Overview
class Waste_Sent_For_LandFillOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        try:
            if not year:
                year = self.get_latest_available_year(user)

            try:
                year = int(year)
            except ValueError:
                return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

            start_date, end_date = self.get_fiscal_year_range(year)

            filters = {
                'user': user,
                'DatePicker__range': (start_date.date(), end_date.date())
            }
            if facility_id and facility_id.lower() != 'all':
                filters['facility__facility_id'] = facility_id
            if facility_location:
                filters['facility__location__icontains'] = facility_location

            waste_data = Waste.objects.filter(**filters)
            if not waste_data.exists():
                return self.get_empty_response(year)

            monthly_Landfill_waste = (
                waste_data
                .values('DatePicker__month')
                .annotate(total_Landfill_waste=Sum('Landfill_waste'))
            )

            Landfill_waste = {month: 0 for month in range(1, 13)}
            for entry in monthly_Landfill_waste:
                Landfill_waste[entry['DatePicker__month']] = entry['total_Landfill_waste']

            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            line_chart_data = [
                {
                    "month": datetime(1900, month, 1).strftime('%b'),
                    "Landfill_waste": Landfill_waste[month]
                }
                for month in month_order
            ]

            # Prepare facility data for donut chart
            facility_Landfill_waste = (
                waste_data
                .values('facility__facility_name')
                .annotate(total_Landfill_waste=Sum('Landfill_waste'))
                .order_by('-total_Landfill_waste')
            )

            total_Landfill_waste = sum(entry['total_Landfill_waste'] for entry in facility_Landfill_waste)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_Landfill_waste'] / total_Landfill_waste * 100) if total_Landfill_waste else 0,
                }
                for entry in facility_Landfill_waste
            ]

            response_data = {
                "year": year,
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            print(f"Error: {str(e)}")
            print("Traceback:", traceback.format_exc())
            return Response(
                {'error': f'An error occurred while processing your request: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_latest_available_year(self, user):
        # Find the latest date across all models
        latest_water_date = Water.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_waste_date = Waste.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_energy_date = Energy.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_biodiversity_date = Biodiversity.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_logistices_date = Logistices.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']

        latest_date = max(
            filter(None, [latest_water_date, latest_waste_date, latest_energy_date, latest_biodiversity_date, latest_logistices_date]),
            default=None
        )

        if latest_date:
            return latest_date.year if latest_date.month >= 4 else latest_date.year - 1
        today = datetime.now()
        return today.year - 1 if today.month < 4 else today.year

    def get_fiscal_year_range(self, year):
        start_date = datetime(year, 4, 1)
        end_date = datetime(year + 1, 3, 31)
        return start_date, end_date

    def get_empty_response(self, year):
        month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
        line_chart_data = [{"month": datetime(1900, month, 1).strftime('%b'), "Landfill_waste": 0} for month in month_order]
        donut_chart_data = [{"facility_name": "No Facility", "percentage": 0}]
        return Response({
            "year": year,
            "line_chart_data": line_chart_data,
            "donut_chart_data": donut_chart_data
        }, status=status.HTTP_200_OK)

#Stacked Graphs Overview
class StackedWasteOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        try:
            filters = {'user': user}

            if facility_id and facility_id.lower() != 'all':
                if not Facility.objects.filter(facility_id=facility_id, user=user).exists():
                    return Response(
                        {'error': 'Invalid facility ID or not associated with the logged-in user.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                filters['facility__facility_id'] = facility_id

            if facility_location and facility_location.lower() != 'all':
                if not Facility.objects.filter(location__icontains=facility_location).exists():
                    return Response(
                        {'error': f'No facility found with location {facility_location}.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                filters['facility__location__icontains'] = facility_location

            if year:
                try:
                    year = int(year)
                    if year < 1900 or year > datetime.now().year + 10:
                        return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)
                except ValueError:
                    return Response({'error': 'Year must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Find the latest year across all models (Water, Waste, etc.)
                latest_water_date = Water.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_waste_date = Waste.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_energy_date = Energy.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_biodiversity_date = Biodiversity.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_logistices_date = Logistices.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']

                latest_date = max(
                    filter(None, [latest_water_date, latest_waste_date, latest_energy_date, latest_biodiversity_date, latest_logistices_date]),
                    default=None
                )
                if latest_date:
                    year = latest_date.year if latest_date.month >= 4 else latest_date.year - 1
                else:
                    # Default to the current fiscal year if no data exists
                    today = datetime.now()
                    year = today.year - 1 if today.month < 4 else today.year

            # Determine fiscal year range
            start_date = datetime(year, 4, 1)
            end_date = datetime(year + 1, 3, 31)
            filters['DatePicker__range'] = (start_date, end_date)

            waste_types = [
                'food_waste', 'solid_Waste', 'E_Waste', 'Biomedical_waste',
                'liquid_discharge', 'Recycle_waste', 'Landfill_waste', 'other_waste'
            ]

            # Initialize monthly data dictionary
            monthly_data = {month: {waste_type: 0 for waste_type in waste_types} for month in range(1, 13)}

            # Fetch and aggregate monthly data
            queryset = Waste.objects.filter(**filters)
            if queryset.exists():
                for waste_type in waste_types:
                    monthly_waste = (
                        queryset
                        .values('DatePicker__month')
                        .annotate(total=Coalesce(Sum(waste_type, output_field=FloatField()), Value(0, output_field=FloatField())))
                        .order_by('DatePicker__month')
                    )
                    for entry in monthly_waste:
                        month = entry['DatePicker__month']
                        monthly_data[month][waste_type] = entry['total']

            # Prepare response data in fiscal month order (April to March)
            stacked_bar_data = []
            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            for month in month_order:
                month_name = datetime(1900, month, 1).strftime('%b')
                stacked_bar_data.append({
                    "month": month_name,
                    **monthly_data[month]
                })

            response_data = {
                "facility_id": facility_id,
                "year": year,
                "facility_location": facility_location,
                "stacked_bar_data": stacked_bar_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error occurred: {e}") 
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#WasteOverview Donut chart
class WasteOverallDonutChartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        year = request.GET.get('year', None)  # Get the 'year' query parameter
        facility_id = request.GET.get('facility_id', 'all')
        facility_location = request.GET.get('facility_location', None)

        try:
            # Initialize filters with the user-specific data
            filters = {'user': user}

            if facility_id != 'all' and not Facility.objects.filter(facility_id=facility_id, user=user).exists():
                return Response({'error': 'Invalid facility ID or not associated with the logged-in user.'}, status=status.HTTP_400_BAD_REQUEST)
            elif facility_id != 'all':
                filters['facility__facility_id'] = facility_id

            # Facility location filtering
            if facility_location and facility_location.lower() != 'all':
                if not Facility.objects.filter(facility_location__icontains=facility_location).exists():
                    return Response({'error': f'No facility found with location {facility_location}.'}, status=status.HTTP_400_BAD_REQUEST)
                filters['facility__facility_location__icontains'] = facility_location

            # Year calculation
            if year:
                try:
                    year = int(year)
                    if year < 1900 or year > datetime.now().year + 10:
                        return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)
                except ValueError:
                    return Response({'error': 'Year must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Find the latest year across all models
                latest_water_date = Water.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_waste_date = Waste.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_energy_date = Energy.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_biodiversity_date = Biodiversity.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_logistics_date = Logistices.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']

                latest_date = max(filter(None, [latest_water_date, latest_waste_date, latest_energy_date, latest_biodiversity_date, latest_logistics_date]), default=None)
                if latest_date:
                    year = latest_date.year if latest_date.month >= 4 else latest_date.year - 1
                else:
                    # Default to the current fiscal year if no data exists
                    today = datetime.now()
                    year = today.year - 1 if today.month < 4 else today.year

            # Determine fiscal year range
            start_date = datetime(year, 4, 1)
            end_date = datetime(year + 1, 3, 31)
            filters['DatePicker__range'] = (start_date, end_date)

            # Query the Waste model with the filters applied
            queryset = Waste.objects.filter(**filters)

            if not queryset.exists():  # If no data is found, return zero values for all waste types
                waste_totals = {
                    'food_waste_total': 0.0,
                    'solid_Waste_total': 0.0,
                    'E_Waste_total': 0.0,
                    'Biomedical_waste_total': 0.0,
                    'other_waste_total': 0.0
                }
            else:
                # Aggregate waste totals for each waste type if data is found
                waste_totals = queryset.aggregate(
                    food_waste_total=Coalesce(Sum(Cast('food_waste', FloatField())), 0.0),
                    solid_Waste_total=Coalesce(Sum(Cast('solid_Waste', FloatField())), 0.0),
                    E_Waste_total=Coalesce(Sum(Cast('E_Waste', FloatField())), 0.0),
                    Biomedical_waste_total=Coalesce(Sum(Cast('Biomedical_waste', FloatField())), 0.0),
                    other_waste_total=Coalesce(Sum(Cast('other_waste', FloatField())), 0.0)
                )

            # Calculate the overall total waste
            overall_total = sum(waste_totals.values())

            # Calculate percentages for each waste type
            waste_percentages = {}
            for waste_type, total in waste_totals.items():
                waste_percentages[waste_type] = (total / overall_total) * 100 if overall_total else 0

            # Format the response data
            response_data = {
                "year": year,
                "facility_id": facility_id,
                "facility_location": facility_location,
                "waste_percentages": waste_percentages
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            # Log the error for debugging purposes
            print(f"Error occurred: {e}")
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#SenT to Landfill Overview Piechart
class SentToLandfillOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get_fiscal_year_dates(self, year):
        start_date = datetime(year, 4, 1)  # Fiscal year starts on April 1
        end_date = datetime(year + 1, 3, 31)  # Ends on March 31 of the next year
        return start_date, end_date

    def get(self, request):
        user = request.user

        # Get parameters from the request
        year = request.GET.get('year', None)
        facility_id = request.GET.get('facility_id', 'all')
        facility_location = request.GET.get('facility_location', 'all')
        
        try:
            # Validate facility ID
            if facility_id.lower() != 'all' and not Facility.objects.filter(facility_id=facility_id, user=user).exists():
                return Response({'error': 'Invalid facility ID or not associated with the logged-in user.'}, status=status.HTTP_400_BAD_REQUEST)

            # Validate and determine fiscal year
            if year:
                try:
                    year = int(year)
                    if year < 1900 or year > datetime.now().year + 10:
                        return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)
                except ValueError:
                    return Response({'error': 'Year must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Find the latest year across all models
                latest_water_date = Water.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_waste_date = Waste.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_energy_date = Energy.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_biodiversity_date = Biodiversity.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_logistics_date = Logistices.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']

                latest_date = max(filter(None, [latest_water_date, latest_waste_date, latest_energy_date, latest_biodiversity_date, latest_logistics_date]), default=None)

                if latest_date:
                    year = latest_date.year if latest_date.month >= 4 else latest_date.year - 1
                else:
                    # Default to the current fiscal year if no data exists
                    today = datetime.now()
                    year = today.year - 1 if today.month < 4 else today.year

            start_date, end_date = self.get_fiscal_year_dates(year)

            # Initialize filters
            filters = {'user': user, 'DatePicker__range': (start_date, end_date)}

            # Apply facility ID filter
            if facility_id.lower() != 'all':
                filters['facility__facility_id'] = facility_id

            # Apply facility location filter
            if facility_location.lower() != 'all':
                filters['facility__facility_location__icontains'] = facility_location

            # Start with the base queryset
            queryset = Waste.objects.filter(**filters)

            if not queryset.exists():
                # Return zero data if no matching records
                response_data = {
                    "landfill_percentage": 0,
                    "remaining_percentage": 0
                }
                return Response(
                    {
                        "year": year,
                        "sentToLandFill": response_data
                    },
                    status=status.HTTP_200_OK
                )

            # Define waste fields for calculations
            overall_total_fields = [
                'food_waste', 'solid_Waste', 'E_Waste', 'Biomedical_waste', 'other_waste'
            ]

            # Calculate total 'Landfill_waste'
            Landfill_waste_total = queryset.aggregate(
                total=Coalesce(Sum(Cast('Landfill_waste', FloatField())), 0.0)
            )['total']

            # Calculate overall total waste
            overall_totals = queryset.aggregate(
                **{f"{waste_type}_total": Coalesce(Sum(Cast(waste_type, FloatField())), 0.0)
                   for waste_type in overall_total_fields}
            )
            overall_total = sum(overall_totals.values())

            # Calculate remaining waste and percentages
            remaining_waste_total = overall_total - Landfill_waste_total
            
            landfill_percentage = (Landfill_waste_total / overall_total) * 100 if overall_total else 0
            remaining_percentage = (remaining_waste_total / overall_total) * 100 if overall_total else 0

            # Prepare the response data
            response_data = {
                "landfill_percentage": round(landfill_percentage, 2),
                "remaining_percentage": round(remaining_percentage, 2)
            }

            return Response(
                {
                    "year": year,
                    "sentToLandFill": response_data
                },
                status=status.HTTP_200_OK
            )

        except ValueError:
            return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Error occurred: {e}")
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#Sent to Recycle Overview Piechart
class SentToRecycledOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get_fiscal_year_dates(self, year):
        start_date = datetime(year, 4, 1)  # Fiscal year starts on April 1
        end_date = datetime(year + 1, 3, 31)  # Ends on March 31 of the next year
        return start_date, end_date

    def get(self, request):
        user = request.user

        # Get parameters from the request
        year = request.GET.get('year', None)
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
    
        try:
            # Default to the current fiscal year if no year is provided
            if facility_id and facility_id.lower() != 'all' and not Facility.objects.filter(facility_id=facility_id, user=user).exists():
                return Response({'error': 'Invalid facility ID or not associated with the logged-in user.'}, status=status.HTTP_400_BAD_REQUEST)

            # Validate and determine fiscal year
            if year:
                try:
                    year = int(year)
                    if year < 1900 or year > datetime.now().year + 10:
                        return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)
                except ValueError:
                    return Response({'error': 'Year must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Find the latest year across all models
                latest_water_date = Water.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_waste_date = Waste.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_energy_date = Energy.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_biodiversity_date = Biodiversity.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_logistics_date = Logistices.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']

                latest_date = max(filter(None, [latest_water_date, latest_waste_date, latest_energy_date, latest_biodiversity_date, latest_logistics_date]), default=None)

                if latest_date:
                    year = latest_date.year if latest_date.month >= 4 else latest_date.year - 1
                else:
                    # Default to the current fiscal year if no data exists
                    today = datetime.now()
                    year = today.year - 1 if today.month < 4 else today.year

            start_date, end_date = self.get_fiscal_year_dates(year)

            # Initialize filters
            filters = {'user': user, 'DatePicker__range': (start_date, end_date)}

            # Start with the base queryset
            queryset = Waste.objects.filter(**filters)

            # Apply facility_id filter if provided and not 'all'
            if facility_id and facility_id.lower() != 'all':
                queryset = queryset.filter(facility__facility_id=facility_id)

            # Apply facility_location filter if provided and not 'all'
            if facility_location and facility_location.lower() != 'all':
                queryset = queryset.filter(facility__facility_location__icontains=facility_location)

            if not queryset.exists():
                # Return zero data if no matching records
                response_data = {
                    "recycle_percentage": 0,
                    "remaining_percentage": 0
                }
                return Response(
                    {
                        "year":year,
                        "SentToRecycle": response_data
                    },
                    status=status.HTTP_200_OK
                )

            # Define waste fields for calculations
            overall_total_fields = [
                'food_waste', 'solid_Waste', 'E_Waste', 'Biomedical_waste', 'other_waste'
            ]

        # Calculate total 'Landfill_waste'
            Recycle_waste_total = queryset.aggregate(
                total=Coalesce(Sum(Cast('Recycle_waste', FloatField())), 0.0)
            )['total']

            # Calculate overall total waste
            overall_totals = queryset.aggregate(
                **{f"{waste_type}_total": Coalesce(Sum(Cast(waste_type, FloatField())), 0.0)
                for waste_type in overall_total_fields}
            )
            overall_total = sum(overall_totals.values())

            # Calculate remaining waste and percentages
            remaining_waste_total = overall_total - Recycle_waste_total
        
            recycle_percentage = (Recycle_waste_total / overall_total) * 100 if overall_total else 0
            remaining_percentage = (remaining_waste_total / overall_total) * 100 if overall_total else 0

            # Prepare the response data
            response_data = {
                "recycle_percentage": round(recycle_percentage, 2),
                "remaining_percentage": round(remaining_percentage, 2)
            }

            return Response(
                {
                    "year":year,
                    "SentToRecycle": response_data
                },
                status=status.HTTP_200_OK
            )

        except ValueError:
            return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Error occurred: {e}")
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


'''Waste Overviewgraphs and Individual Line charts and donut charts Ends'''


'''Energy  Overview Cards ,Graphs and Individual line charts and donut charts Starts'''
#Energy Overview Cards
class EnergyViewCard_Over(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', 'all')
        facility_location = request.GET.get('facility_location')
        year = request.GET.get('year')

        try:
            # Validate facility_id
            if facility_id != 'all' and not Facility.objects.filter(facility_id=facility_id, user=user).exists():
                return Response({'error': 'Invalid facility ID or not associated with the logged-in user.'}, status=status.HTTP_400_BAD_REQUEST)

            # Validate year
            if year:
                try:
                    year = int(year)
                    if year < 1900 or year > datetime.now().year + 10:
                        return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)
                except ValueError:
                    return Response({'error': 'Year must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Find the latest year across all models (Water, Waste, etc.)
                latest_water_date = Water.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_waste_date = Waste.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_energy_date = Energy.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_biodiversity_date = Biodiversity.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_logistices_date = Logistices.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                
                
                latest_date = max(filter(None, [latest_water_date, latest_waste_date,latest_energy_date,latest_biodiversity_date,latest_logistices_date]), default=None)
                
                if latest_date:
                    year = latest_date.year if latest_date.month >= 4 else latest_date.year - 1
                else:
                    # Default to the current fiscal year if no data exists
                    today = datetime.now()
                    year = today.year - 1 if today.month < 4 else today.year

            start_date = datetime(year, 4, 1)
            end_date = datetime(year + 1, 3, 31)

            # Query energy data
            energy_data = Energy.objects.filter(user=user, DatePicker__range=(start_date, end_date))

            if facility_id != 'all':
                energy_data = energy_data.filter(facility__facility_id=facility_id)

            if facility_location:
                energy_data = energy_data.filter(facility__location__icontains=facility_location)

            energy_fields = [
                'hvac', 'production', 'stp', 'admin_block',
                'utilities', 'others', 'renewable_solar', 'renewable_other', 'coking_coal', 
                'coke_oven_coal', 'natural_gas', 'diesel', 'biomass_wood', 'biomass_other_solid'
            ]

            response_data = {
                'year': year,
                'overall_energy_totals': {}
            }

            if not energy_data.exists():
                # Populate only specific fields with zero values when no data exists
                zero_fields = ['hvac', 'production', 'stp', 'admin_block', 'utilities', 'others']
                response_data['overall_energy_totals'] = {
                    f"overall_{field}": 0.0 for field in zero_fields
                }
                response_data['overall_energy_totals']['overall_fuel_used_in_operations'] = 0.0
                response_data['overall_energy_totals']['overall_renewable_energy'] = 0.0
            else:
                # Initialize counters for renewable energy and fuel usage totals
                fuel_used_in_operations_total = 0
                renewable_energy_total = 0

                for field in energy_fields:
                    # Aggregate total for each field
                    overall_total = energy_data.aggregate(total=Sum(field))['total'] or 0

                    # Add renewable energy (sum of renewable_solar and renewable_other)
                    if field in ['renewable_solar', 'renewable_other']:
                        renewable_energy_total += overall_total

                    # Add to fuel usage totals
                    if field in ['coke_oven_coal', 'coking_coal', 'natural_gas', 'diesel', 'biomass_wood', 'biomass_other_solid']:
                        fuel_used_in_operations_total += overall_total

                    # Include other fields in the response
                    if field not in ['renewable_solar', 'renewable_other', 'coke_oven_coal', 'coking_coal', 'natural_gas', 'diesel', 'biomass_wood', 'biomass_other_solid']:
                        response_data['overall_energy_totals'][f"overall_{field}"] = overall_total

                # Set the calculated totals for renewable energy and fuel used in operations
                response_data['overall_energy_totals']['overall_fuel_used_in_operations'] = fuel_used_in_operations_total
                response_data['overall_energy_totals']['overall_renewable_energy'] = renewable_energy_total

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            print(error_message)
            return Response({'error': error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#HVAC Line Charts and Donut Chart 
class HVACOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        try:
            if year:
                try:
                    year = int(year)
                    if year < 1900 or year > datetime.now().year + 10:
                        return Response({'error': 'Invalid year parameter.'}, status=400)
                except ValueError:
                    return Response({'error': 'Year must be an integer.'}, status=400)
            else:
                year = self.get_latest_available_year(user)

            start_date, end_date = self.get_fiscal_year_range(year)

            filters = {
                'user': user,
                'DatePicker__range': (start_date.date(), end_date.date())
            }
            if facility_id and facility_id.lower() != 'all':
                filters['facility__facility_id'] = facility_id
            if facility_location:
                filters['facility__location__icontains'] = facility_location

            energy_data = Energy.objects.filter(**filters)
            if not energy_data.exists():
                return self.get_empty_response(year)

            monthly_hvac = (
                energy_data
                .values('DatePicker__month')
                .annotate(total_hvac=Sum('hvac'))
            )

            hvac = {month: 0 for month in range(1, 13)}
            for entry in monthly_hvac:
                hvac[entry['DatePicker__month']] = entry['total_hvac']

            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            line_chart_data = [
                {
                    "month": datetime(1900, month, 1).strftime('%b'),
                    "hvac": hvac[month]
                }
                for month in month_order
            ]

            # Prepare facility data for donut chart
            facility_hvac = (
                energy_data
                .values('facility__facility_name')
                .annotate(total_hvac=Sum('hvac'))
                .order_by('-total_hvac')
            )

            total_hvac = sum(entry['total_hvac'] for entry in facility_hvac)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_hvac'] / total_hvac * 100) if total_hvac else 0,
                }
                for entry in facility_hvac
            ]

            response_data = {
                "year": year,
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            print(f"Error: {str(e)}")
            print("Traceback:", traceback.format_exc())
            return Response(
                {'error': f'An error occurred while processing your request: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_latest_available_year(self, user):
        # Find the latest date across all models
        latest_water_date = Water.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_waste_date = Waste.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_energy_date = Energy.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_biodiversity_date = Biodiversity.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_logistices_date = Logistices.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']

        latest_date = max(
            filter(None, [latest_water_date, latest_waste_date, latest_energy_date, latest_biodiversity_date, latest_logistices_date]),
            default=None
        )

        if latest_date:
            return latest_date.year if latest_date.month >= 4 else latest_date.year - 1
        today = datetime.now()
        return today.year - 1 if today.month < 4 else today.year

    def get_fiscal_year_range(self, year):
        start_date = datetime(year, 4, 1)
        end_date = datetime(year + 1, 3, 31)
        return start_date, end_date

    def get_empty_response(self, year):
        month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
        line_chart_data = [{"month": datetime(1900, month, 1).strftime('%b'), "hvac": 0} for month in month_order]
        donut_chart_data = [{"facility_name": "No Facility", "percentage": 0}]
        return Response({
            "year": year,
            "line_chart_data": line_chart_data,
            "donut_chart_data": donut_chart_data
        }, status=status.HTTP_200_OK)

#ProductionLine Charts and Donut charts
class ProductionOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        try:
            if year:
                try:
                    year = int(year)
                    if year < 1900 or year > datetime.now().year + 10:
                        return Response({'error': 'Invalid year parameter.'}, status=400)
                except ValueError:
                    return Response({'error': 'Year must be an integer.'}, status=400)
            else:
                year = self.get_latest_available_year(user)

            start_date, end_date = self.get_fiscal_year_range(year)

            filters = {
                'user': user,
                'DatePicker__range': (start_date.date(), end_date.date())
            }
            if facility_id and facility_id.lower() != 'all':
                filters['facility__facility_id'] = facility_id
            if facility_location:
                filters['facility__location__icontains'] = facility_location

            energy_data = Energy.objects.filter(**filters)
            if not energy_data.exists():
                return self.get_empty_response(year)

            monthly_production = (
                energy_data
                .values('DatePicker__month')
                .annotate(total_production=Sum('production'))
            )

            production = {month: 0 for month in range(1, 13)}
            for entry in monthly_production:
                production[entry['DatePicker__month']] = entry['total_production']

            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            line_chart_data = [
                {
                    "month": datetime(1900, month, 1).strftime('%b'),
                    "production": production[month]
                }
                for month in month_order
            ]

            # Prepare facility data for donut chart
            facility_production = (
                energy_data
                .values('facility__facility_name')
                .annotate(total_production=Sum('production'))
                .order_by('-total_production')
            )

            total_production = sum(entry['total_production'] for entry in facility_production)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_production'] / total_production * 100) if total_production else 0,
                }
                for entry in facility_production
            ]

            response_data = {
                "year": year,
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            print(f"Error: {str(e)}")
            print("Traceback:", traceback.format_exc())
            return Response(
                {'error': f'An error occurred while processing your request: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_latest_available_year(self, user):
        # Find the latest date across all models
        latest_water_date = Water.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_waste_date = Waste.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_energy_date = Energy.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_biodiversity_date = Biodiversity.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_logistices_date = Logistices.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']

        latest_date = max(
            filter(None, [latest_water_date, latest_waste_date, latest_energy_date, latest_biodiversity_date, latest_logistices_date]),
            default=None
        )

        if latest_date:
            return latest_date.year if latest_date.month >= 4 else latest_date.year - 1
        today = datetime.now()
        return today.year - 1 if today.month < 4 else today.year

    def get_fiscal_year_range(self, year):
        start_date = datetime(year, 4, 1)
        end_date = datetime(year + 1, 3, 31)
        return start_date, end_date

    def get_empty_response(self, year):
        month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
        line_chart_data = [{"month": datetime(1900, month, 1).strftime('%b'), "production": 0} for month in month_order]
        donut_chart_data = [{"facility_name": "No Facility", "percentage": 0}]
        return Response({
            "year": year,
            "line_chart_data": line_chart_data,
            "donut_chart_data": donut_chart_data
        }, status=status.HTTP_200_OK)

#STP Overview line charts and donut charts
class StpOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        try:
            if year:
                try:
                    year = int(year)
                    if year < 1900 or year > datetime.now().year + 10:
                        return Response({'error': 'Invalid year parameter.'}, status=400)
                except ValueError:
                    return Response({'error': 'Year must be an integer.'}, status=400)
            else:
                year = self.get_latest_available_year(user)

            start_date, end_date = self.get_fiscal_year_range(year)

            filters = {
                'user': user,
                'DatePicker__range': (start_date.date(), end_date.date())
            }
            if facility_id and facility_id.lower() != 'all':
                filters['facility__facility_id'] = facility_id
            if facility_location:
                filters['facility__location__icontains'] = facility_location

            energy_data = Energy.objects.filter(**filters)
            if not energy_data.exists():
                return self.get_empty_response(year)

            monthly_stp = (
                energy_data
                .values('DatePicker__month')
                .annotate(total_stp=Sum('stp'))
            )

            stp = {month: 0 for month in range(1, 13)}
            for entry in monthly_stp:
                stp[entry['DatePicker__month']] = entry['total_stp']

            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            line_chart_data = [
                {
                    "month": datetime(1900, month, 1).strftime('%b'),
                    "stp": stp[month]
                }
                for month in month_order
            ]

            # Prepare facility data for donut chart
            facility_stp = (
                energy_data
                .values('facility__facility_name')
                .annotate(total_stp=Sum('stp'))
                .order_by('-total_stp')
            )

            total_stp = sum(entry['total_stp'] for entry in facility_stp)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_stp'] / total_stp * 100) if total_stp else 0,
                }
                for entry in facility_stp
            ]

            response_data = {
                "year": year,
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            print(f"Error: {str(e)}")
            print("Traceback:", traceback.format_exc())
            return Response(
                {'error': f'An error occurred while processing your request: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_latest_available_year(self, user):
        # Find the latest date across all models
        latest_water_date = Water.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_waste_date = Waste.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_energy_date = Energy.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_biodiversity_date = Biodiversity.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_logistices_date = Logistices.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']

        latest_date = max(
            filter(None, [latest_water_date, latest_waste_date, latest_energy_date, latest_biodiversity_date, latest_logistices_date]),
            default=None
        )

        if latest_date:
            return latest_date.year if latest_date.month >= 4 else latest_date.year - 1
        today = datetime.now()
        return today.year - 1 if today.month < 4 else today.year

    def get_fiscal_year_range(self, year):
        start_date = datetime(year, 4, 1)
        end_date = datetime(year + 1, 3, 31)
        return start_date, end_date

    def get_empty_response(self, year):
        month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
        line_chart_data = [{"month": datetime(1900, month, 1).strftime('%b'), "stp": 0} for month in month_order]
        donut_chart_data = [{"facility_name": "No Facility", "percentage": 0}]
        return Response({
            "year": year,
            "line_chart_data": line_chart_data,
            "donut_chart_data": donut_chart_data
        }, status=status.HTTP_200_OK)

#Admin_block Overview Linecharts and donut charts
class Admin_BlockOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        try:
            if year:
                try:
                    year = int(year)
                    if year < 1900 or year > datetime.now().year + 10:
                        return Response({'error': 'Invalid year parameter.'}, status=400)
                except ValueError:
                    return Response({'error': 'Year must be an integer.'}, status=400)
            else:
                year = self.get_latest_available_year(user)

            start_date, end_date = self.get_fiscal_year_range(year)
            filters = {
                'user': user,
                'DatePicker__range': (start_date.date(), end_date.date())
            }
            if facility_id and facility_id.lower() != 'all':
                filters['facility__facility_id'] = facility_id
            if facility_location:
                filters['facility__location__icontains'] = facility_location

            energy_data = Energy.objects.filter(**filters)
            if not energy_data.exists():
                return self.get_empty_response(year)

            monthly_admin_block = (
                energy_data
                .values('DatePicker__month')
                .annotate(total_admin_block=Sum('admin_block'))
            )

            admin_block = {month: 0 for month in range(1, 13)}
            for entry in monthly_admin_block:
                admin_block[entry['DatePicker__month']] = entry['total_admin_block']

            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            line_chart_data = [
                {
                    "month": datetime(1900, month, 1).strftime('%b'),
                    "admin_block": admin_block[month]
                }
                for month in month_order
            ]

            # Prepare facility data for donut chart
            facility_admin_block = (
                energy_data
                .values('facility__facility_name')
                .annotate(total_admin_block=Sum('admin_block'))
                .order_by('-total_admin_block')
            )

            total_admin_block = sum(entry['total_admin_block'] for entry in facility_admin_block)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_admin_block'] / total_admin_block * 100) if total_admin_block else 0,
                }
                for entry in facility_admin_block
            ]

            response_data = {
                "year": year,
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            print(f"Error: {str(e)}")
            print("Traceback:", traceback.format_exc())
            return Response(
                {'error': f'An error occurred while processing your request: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_latest_available_year(self, user):
        # Find the latest date across all models
        latest_water_date = Water.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_waste_date = Waste.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_energy_date = Energy.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_biodiversity_date = Biodiversity.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_logistices_date = Logistices.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']

        latest_date = max(
            filter(None, [latest_water_date, latest_waste_date, latest_energy_date, latest_biodiversity_date, latest_logistices_date]),
            default=None
        )

        if latest_date:
            return latest_date.year if latest_date.month >= 4 else latest_date.year - 1
        today = datetime.now()
        return today.year - 1 if today.month < 4 else today.year

    def get_fiscal_year_range(self, year):
        start_date = datetime(year, 4, 1)
        end_date = datetime(year + 1, 3, 31)
        return start_date, end_date

    def get_empty_response(self, year):
        month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
        line_chart_data = [{"month": datetime(1900, month, 1).strftime('%b'), "admin_block": 0} for month in month_order]
        donut_chart_data = [{"facility_name": "No Facility", "percentage": 0}]
        return Response({
            "year": year,
            "line_chart_data": line_chart_data,
            "donut_chart_data": donut_chart_data
        }, status=status.HTTP_200_OK)

#Utilities_OverView Linecharts and Donut Charts
class Utilities_OverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        try:
            if year:
                try:
                    year = int(year)
                    if year < 1900 or year > datetime.now().year + 10:
                        return Response({'error': 'Invalid year parameter.'}, status=400)
                except ValueError:
                    return Response({'error': 'Year must be an integer.'}, status=400)
            else:
                year = self.get_latest_available_year(user)

            start_date, end_date = self.get_fiscal_year_range(year)

            filters = {
                'user': user,
                'DatePicker__range': (start_date.date(), end_date.date())
            }
            if facility_id and facility_id.lower() != 'all':
                filters['facility__facility_id'] = facility_id
            if facility_location:
                filters['facility__location__icontains'] = facility_location

            energy_data = Energy.objects.filter(**filters)
            if not energy_data.exists():
                return self.get_empty_response(year)

            monthly_utilities = (
                energy_data
                .values('DatePicker__month')
                .annotate(total_utilities=Sum('utilities'))
            )

            utilities = {month: 0 for month in range(1, 13)}
            for entry in monthly_utilities:
                utilities[entry['DatePicker__month']] = entry['total_utilities']

            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            line_chart_data = [
                {
                    "month": datetime(1900, month, 1).strftime('%b'),
                    "utilities": utilities[month]
                }
                for month in month_order
            ]

            # Prepare facility data for donut chart
            facility_utilities = (
                energy_data
                .values('facility__facility_name')
                .annotate(total_utilities=Sum('utilities'))
                .order_by('-total_utilities')
            )

            total_utilities = sum(entry['total_utilities'] for entry in facility_utilities)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_utilities'] / total_utilities * 100) if total_utilities else 0,
                }
                for entry in facility_utilities
            ]

            response_data = {
                "year": year,
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            print(f"Error: {str(e)}")
            print("Traceback:", traceback.format_exc())
            return Response(
                {'error': f'An error occurred while processing your request: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_latest_available_year(self, user):
        # Find the latest date across all models
        latest_water_date = Water.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_waste_date = Waste.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_energy_date = Energy.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_biodiversity_date = Biodiversity.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_logistices_date = Logistices.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']

        latest_date = max(
            filter(None, [latest_water_date, latest_waste_date, latest_energy_date, latest_biodiversity_date, latest_logistices_date]),
            default=None
        )

        if latest_date:
            return latest_date.year if latest_date.month >= 4 else latest_date.year - 1
        today = datetime.now()
        return today.year - 1 if today.month < 4 else today.year

    def get_fiscal_year_range(self, year):
        start_date = datetime(year, 4, 1)
        end_date = datetime(year + 1, 3, 31)
        return start_date, end_date

    def get_empty_response(self, year):
        month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
        line_chart_data = [{"month": datetime(1900, month, 1).strftime('%b'), "utilities": 0} for month in month_order]
        donut_chart_data = [{"facility_name": "No Facility", "percentage": 0}]
        return Response({
            "year": year,
            "line_chart_data": line_chart_data,
            "donut_chart_data": donut_chart_data
        }, status=status.HTTP_200_OK)

# Others Overview Linecharts andDonut charts
class Others_OverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        try:
            if year:
                try:
                    year = int(year)
                    if year < 1900 or year > datetime.now().year + 10:
                        return Response({'error': 'Invalid year parameter.'}, status=400)
                except ValueError:
                    return Response({'error': 'Year must be an integer.'}, status=400)
            else:
                year = self.get_latest_available_year(user)

            start_date, end_date = self.get_fiscal_year_range(year)

            filters = {
                'user': user,
                'DatePicker__range': (start_date.date(), end_date.date())
            }
            if facility_id and facility_id.lower() != 'all':
                filters['facility__facility_id'] = facility_id
            if facility_location:
                filters['facility__location__icontains'] = facility_location

            energy_data = Energy.objects.filter(**filters)
            if not energy_data.exists():
                return self.get_empty_response(year)

            monthly_others = (
                energy_data
                .values('DatePicker__month')
                .annotate(total_others=Sum('others'))
            )

            others = {month: 0 for month in range(1, 13)}
            for entry in monthly_others:
                others[entry['DatePicker__month']] = entry['total_others']

            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            line_chart_data = [
                {
                    "month": datetime(1900, month, 1).strftime('%b'),
                    "others": others[month]
                }
                for month in month_order
            ]

            # Prepare facility data for donut chart
            facility_others = (
                energy_data
                .values('facility__facility_name')
                .annotate(total_others=Sum('others'))
                .order_by('-total_others')
            )

            total_others = sum(entry['total_others'] for entry in facility_others)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_others'] / total_others * 100) if total_others else 0,
                }
                for entry in facility_others
            ]

            response_data = {
                "year": year,
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            print(f"Error: {str(e)}")
            print("Traceback:", traceback.format_exc())
            return Response(
                {'error': f'An error occurred while processing your request: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_latest_available_year(self, user):
        # Find the latest date across all models
        latest_water_date = Water.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_waste_date = Waste.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_energy_date = Energy.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_biodiversity_date = Biodiversity.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_logistices_date = Logistices.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']

        latest_date = max(
            filter(None, [latest_water_date, latest_waste_date, latest_energy_date, latest_biodiversity_date, latest_logistices_date]),
            default=None
        )

        if latest_date:
            return latest_date.year if latest_date.month >= 4 else latest_date.year - 1
        today = datetime.now()
        return today.year - 1 if today.month < 4 else today.year

    def get_fiscal_year_range(self, year):
        start_date = datetime(year, 4, 1)
        end_date = datetime(year + 1, 3, 31)
        return start_date, end_date

    def get_empty_response(self, year):
        month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
        line_chart_data = [{"month": datetime(1900, month, 1).strftime('%b'), "others": 0} for month in month_order]
        donut_chart_data = [{"facility_name": "No Facility", "percentage": 0}]
        return Response({
            "year": year,
            "line_chart_data": line_chart_data,
            "donut_chart_data": donut_chart_data
        }, status=status.HTTP_200_OK)

#Renewable_EnergyOverview Line Charts And Donut Charts
# class Renewable_EnergyOverView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         user = request.user
#         facility_id = request.GET.get('facility_id', None)
#         facility_location = request.GET.get('facility_location', None)
#         year = request.GET.get('year', None)

#         try:
#             # Initialize filters
#             filters = {'user': user}

#             # Determine fiscal year range
#             if facility_id and facility_id.lower() != 'all':
#                 if not Facility.objects.filter(facility_id=facility_id, user=user).exists():
#                     return Response(
#                         {'error': 'Invalid facility ID or not associated with the logged-in user.'},
#                         status=status.HTTP_400_BAD_REQUEST
#                     )
#                 filters['facility__facility_id'] = facility_id

#             # Facility Location validation and filtering
#             if facility_location and facility_location.lower() != 'all':
#                 if not Facility.objects.filter(location__icontains=facility_location).exists():
#                     return Response(
#                         {'error': f'No facility found with location {facility_location}.'},
#                         status=status.HTTP_400_BAD_REQUEST
#                     )
#                 filters['facility__location__icontains'] = facility_location

#             # Year validation and filtering
#             if year:
#                 try:
#                     year = int(year)
#                     if year < 1900 or year > datetime.now().year + 10:
#                         return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)
#                 except ValueError:
#                     return Response({'error': 'Year must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)
#             else:
#                 # Find the latest year across all models (Water, Waste, etc.)
#                 latest_water_date = Water.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
#                 latest_waste_date = Waste.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
#                 latest_energy_date = Energy.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
#                 latest_biodiversity_date = Biodiversity.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
#                 latest_logistices_date = Logistices.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']

#                 latest_date = max(
#                     filter(None, [latest_water_date, latest_waste_date, latest_energy_date, latest_biodiversity_date, latest_logistices_date]),
#                     default=None
#                 )
#                 if latest_date:
#                     year = latest_date.year if latest_date.month >= 4 else latest_date.year - 1
#                 else:
#                     # Default to the current fiscal year if no data exists
#                     today = datetime.now()
#                     year = today.year - 1 if today.month < 4 else today.year

#             # Determine fiscal year range
#             start_date = datetime(year, 4, 1)
#             end_date = datetime(year + 1, 3, 31)
#             filters['DatePicker__range'] = (start_date, end_date)

#             # Apply additional filters for facility
#             if facility_id and facility_id.lower() != 'all':
#                 filters['facility__facility_id'] = facility_id
#             if facility_location:
#                 filters['facility__facility_location__icontains'] = facility_location

#             # Query monthly renewable energy data
#             monthly_renewable_energy = (
#                 Energy.objects.filter(**filters)
#                 .values('DatePicker__month')
#                 .annotate(
#                     total_solar=Sum('renewable_solar'),
#                     total_other=Sum('renewable_other')
#                 )
#                 .order_by('DatePicker__month')
#             )

#             # Map data to fiscal year months
#             renewable_energy = defaultdict(float)
#             for entry in monthly_renewable_energy:
#                 month = entry['DatePicker__month']
#                 total_energy = entry['total_solar'] + entry['total_other']
#                 renewable_energy[month] = total_energy

#             # Prepare line chart data
#             month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
#             line_chart_data = []
#             for month in month_order:
#                 month_name = datetime(1900, month, 1).strftime('%b')
#                 line_chart_data.append({
#                     "month": month_name,
#                     "renewable_energy": renewable_energy.get(month, 0)
#                 })

#             # Query facility-wise renewable energy data
#             facility_filters = {
#                 'user': user,
#                 'DatePicker__range': (start_date, end_date)
#             }
#             if facility_id and facility_id.lower() != 'all':
#                 facility_filters['facility__facility_id'] = facility_id

#             facility_renewable_energy = (
#                 Energy.objects.filter(**facility_filters)
#                 .values('facility__facility_name')
#                 .annotate(total_renewable_energy=Sum('renewable_solar') + Sum('renewable_other'))
#                 .order_by('-total_renewable_energy')
#             )

#             # Calculate total renewable energy for percentage calculations
#             total_renewable_energy = sum(entry['total_renewable_energy'] for entry in facility_renewable_energy)

#             # Prepare donut chart data
#             donut_chart_data = [
#                 {
#                     "facility_name": entry['facility__facility_name'],
#                     "percentage": (entry['total_renewable_energy'] / total_renewable_energy * 100) if total_renewable_energy else 0,
#                 }
#                 for entry in facility_renewable_energy
#             ]

#             # Prepare and return response
#             response_data = {
#                 "year": year,
#                 "line_chart_data": line_chart_data,
#                 "donut_chart_data": donut_chart_data
#             }

#             return Response(response_data, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response(
#                 {'error': f'An error occurred while processing your request: {str(e)}'},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )

class Renewable_EnergyOverView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        try:
            # Initialize filters
            filters = {'user': user}

            # Determine fiscal year range
            if facility_id and facility_id.lower() != 'all':
                if not Facility.objects.filter(facility_id=facility_id, user=user).exists():
                    return Response(
                        {'error': 'Invalid facility ID or not associated with the logged-in user.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                filters['facility__facility_id'] = facility_id

            # Facility Location validation and filtering
            if facility_location and facility_location.lower() != 'all':
                if not Facility.objects.filter(location__icontains=facility_location).exists():
                    return Response(
                        {'error': f'No facility found with location {facility_location}.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                filters['facility__location__icontains'] = facility_location

            # Year validation and filtering
            if year:
                try:
                    year = int(year)
                    if year < 1900 or year > datetime.now().year + 10:
                        return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)
                except ValueError:
                    return Response({'error': 'Year must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Find the latest year across all models (Water, Waste, etc.)
                latest_water_date = Water.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_waste_date = Waste.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_energy_date = Energy.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_biodiversity_date = Biodiversity.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_logistices_date = Logistices.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']

                latest_date = max(
                    filter(None, [latest_water_date, latest_waste_date, latest_energy_date, latest_biodiversity_date, latest_logistices_date]),
                    default=None
                )
                if latest_date:
                    year = latest_date.year if latest_date.month >= 4 else latest_date.year - 1
                else:
                    # Default to the current fiscal year if no data exists
                    today = datetime.now()
                    year = today.year - 1 if today.month < 4 else today.year

            # Determine fiscal year range
            start_date = datetime(year, 4, 1)
            end_date = datetime(year + 1, 3, 31)
            filters['DatePicker__range'] = (start_date, end_date)

            # Query monthly renewable energy data
            monthly_renewable_energy = (
                Energy.objects.filter(**filters)
                .values('DatePicker__month')
                .annotate(
                    total_solar=Sum('renewable_solar'),
                    total_other=Sum('renewable_other')
                )
                .order_by('DatePicker__month')
            )

            # Map data to fiscal year months
            renewable_energy = defaultdict(float)
            for entry in monthly_renewable_energy:
                month = entry['DatePicker__month']
                total_energy = entry['total_solar'] + entry['total_other']
                renewable_energy[month] = total_energy

            # Prepare line chart data
            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            line_chart_data = []
            for month in month_order:
                month_name = datetime(1900, month, 1).strftime('%b')
                line_chart_data.append({
                    "month": month_name,
                    "renewable_energy": renewable_energy.get(month, 0)
                })

            # Query facility-wise renewable energy data
            facility_filters = {
                'user': user,
                'DatePicker__range': (start_date, end_date)
            }
            if facility_id and facility_id.lower() != 'all':
                facility_filters['facility__facility_id'] = facility_id

            facility_renewable_energy = (
                Energy.objects.filter(**facility_filters)
                .values('facility__facility_name')
                .annotate(total_renewable_energy=Sum('renewable_solar') + Sum('renewable_other'))
                .order_by('-total_renewable_energy')
            )

            # Calculate total renewable energy for percentage calculations
            total_renewable_energy = sum(entry['total_renewable_energy'] for entry in facility_renewable_energy)

            # Get a list of all facilities for the user
            all_facilities = Facility.objects.filter(user=user)

            # Prepare donut chart data with facilities having zero values if no renewable energy data is available
            donut_chart_data = []
            for facility in all_facilities:
                # Check if the facility has data, if not set it to 0
                facility_data = next((entry for entry in facility_renewable_energy if entry['facility__facility_name'] == facility.facility_name), None)
                total_energy = facility_data['total_renewable_energy'] if facility_data else 0
                donut_chart_data.append({
                    "facility_name": facility.facility_name,
                    "percentage": (total_energy / total_renewable_energy * 100) if total_renewable_energy else 0,
                })

            # Prepare and return response
            response_data = {
                "year": year,
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': f'An error occurred while processing your request: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

#Fuel Used in Opeartions Line Chart and donut chart
# class Fuel_Used_OperationsOverView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         user = request.user
#         facility_id = request.GET.get('facility_id', None)
#         facility_location = request.GET.get('facility_location', None)
#         year = request.GET.get('year', None)

#         try:
#             filters = {'user': user}
            
#             # If year is not provided, get the latest available year based on the Energy model
#             if not year:
#                 latest_energy = Energy.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))
#                 if latest_energy['latest_date']:
#                     latest_date = latest_energy['latest_date']
#                     year = latest_date.year if latest_date.month >= 4 else latest_date.year - 1
#                 else:
#                     # Default to the current fiscal year if no data exists
#                     today = datetime.now()
#                     year = today.year if today.month >= 4 else today.year - 1

#             year = int(year)
#             start_date = datetime(year, 4, 1)
#             end_date = datetime(year + 1, 3, 31)

#             filters['DatePicker__range'] = (start_date, end_date)

#             # Apply facility filters if provided
#             if facility_id and facility_id.lower() != 'all':
#                 filters['facility__facility_id'] = facility_id
#             if facility_location:
#                 filters['facility__facility_location__icontains'] = facility_location

#             # Query monthly fuel used in operations data
#             monthly_fuel_used_in_operations = (
#                 Energy.objects.filter(**filters)
#                 .values('DatePicker__month')
#                 .annotate(total_fuel_used_in_operations=Sum('coking_coal') + Sum('coke_oven_coal') + Sum('natural_gas') + Sum('diesel') + Sum('biomass_wood') + Sum('biomass_other_solid'))
#                 .order_by('DatePicker__month')
#             )

#             # Prepare line chart data with zero defaults
#             line_chart_data = []
#             fuel_used_in_operations = defaultdict(float)

#             # Map retrieved data to months
#             for entry in monthly_fuel_used_in_operations:
#                 fuel_used_in_operations[entry['DatePicker__month']] = entry['total_fuel_used_in_operations']

#             # Define the month order (April to March)
#             month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
#             today = datetime.now()
#             for month in month_order:
#                 month_name = datetime(1900, month, 1).strftime('%b')

#                 if year == today.year and month > today.month:
#                     fuel_used_in_operations[month] = 0  # No data yet for future months of the current year
#                 else:
                    
#                     line_chart_data.append({
#                     "month": month_name,
#                     "fuel_used_in_operations": fuel_used_in_operations.get(month, 0)
#                 })


#             # Facility-wise fuel used in operations query for donut chart data
#             facility_filters = {
#                 'user': user,
#                 'DatePicker__range': (start_date, end_date)
#             }
#             if facility_id and facility_id.lower() != 'all':
#                 facility_filters['facility__facility_id'] = facility_id
#             facility_fuel_used_in_operations = (
#                 Energy.objects.filter(**facility_filters)
#                 .values('facility__facility_name')
#                 .annotate(total_fuel_used_in_operations=Sum('coking_coal') + Sum('coke_oven_coal') + Sum('natural_gas') + Sum('diesel') + Sum('biomass_wood') + Sum('biomass_other_solid'))
#                 .order_by('-total_fuel_used_in_operations')
#             )

#             # Prepare donut chart data
#             total_fuel_used_in_operations = sum(entry['total_fuel_used_in_operations'] for entry in facility_fuel_used_in_operations)
#             donut_chart_data = [
#                 {
#                     "facility_name": entry['facility__facility_name'],
#                     "percentage": (entry['total_fuel_used_in_operations'] / total_fuel_used_in_operations * 100) if total_fuel_used_in_operations else 0,
#                 }
#                 for entry in facility_fuel_used_in_operations
#             ]

#             response_data = {
#                 "year":year,
#                 "line_chart_data": line_chart_data,
#                 "donut_chart_data": donut_chart_data
#             }

#             return Response(response_data, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response(
#                 {'error': f'An error occurred while processing your request: {str(e)}'},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )

class Fuel_Used_OperationsOverView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        try:
            filters = {'user': user}
            
            # Facility ID validation and filtering
            if facility_id and facility_id.lower() != 'all':
                if not Facility.objects.filter(facility_id=facility_id, user=user).exists():
                    return Response(
                        {'error': 'Invalid facility ID or not associated with the logged-in user.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                filters['facility__facility_id'] = facility_id

            # Facility Location validation and filtering
            if facility_location and facility_location.lower() != 'all':
                if not Facility.objects.filter(location__icontains=facility_location).exists():
                    return Response(
                        {'error': f'No facility found with location {facility_location}.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                filters['facility__location__icontains'] = facility_location

            # Year validation and filtering
            if year:
                try:
                    year = int(year)
                    if year < 1900 or year > datetime.now().year + 10:
                        return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)
                except ValueError:
                    return Response({'error': 'Year must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Find the latest year across all models (Water, Waste, etc.)
                latest_water_date = Water.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_waste_date = Waste.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_energy_date = Energy.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_biodiversity_date = Biodiversity.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_logistices_date = Logistices.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']

                latest_date = max(
                    filter(None, [latest_water_date, latest_waste_date, latest_energy_date, latest_biodiversity_date, latest_logistices_date]),
                    default=None
                )
                if latest_date:
                    year = latest_date.year if latest_date.month >= 4 else latest_date.year - 1
                else:
                    # Default to the current fiscal year if no data exists
                    today = datetime.now()
                    year = today.year - 1 if today.month < 4 else today.year

            # Determine fiscal year range
            start_date = datetime(year, 4, 1)
            end_date = datetime(year + 1, 3, 31)
            filters['DatePicker__range'] = (start_date, end_date)

            # Query monthly fuel used in operations data
            monthly_fuel_used_in_operations = (
                Energy.objects.filter(**filters)
                .values('DatePicker__month')
                .annotate(total_fuel_used_in_operations=Sum('coking_coal') + Sum('coke_oven_coal') + Sum('natural_gas') + Sum('diesel') + Sum('biomass_wood') + Sum('biomass_other_solid'))
                .order_by('DatePicker__month')
            )

            # Prepare line chart data with zero defaults
            line_chart_data = []
            fuel_used_in_operations = defaultdict(float)

            # Map retrieved data to months
            for entry in monthly_fuel_used_in_operations:
                fuel_used_in_operations[entry['DatePicker__month']] = entry['total_fuel_used_in_operations']

            # Define the month order (April to March)
            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            today = datetime.now()
            for month in month_order:
                month_name = datetime(1900, month, 1).strftime('%b')

                if year == today.year and month > today.month:
                    fuel_used_in_operations[month] = 0  # No data yet for future months of the current year
                else:
                    line_chart_data.append({
                        "month": month_name,
                        "fuel_used_in_operations": fuel_used_in_operations.get(month, 0)
                    })

            # Facility-wise fuel used in operations query for donut chart data
            facility_fuel_used_in_operations = (
                Energy.objects.filter(**filters)
                .values('facility__facility_name')
                .annotate(total_fuel_used_in_operations=Sum('coking_coal') + Sum('coke_oven_coal') + Sum('natural_gas') + Sum('diesel') + Sum('biomass_wood') + Sum('biomass_other_solid'))
                .order_by('-total_fuel_used_in_operations')
            )

            # Prepare donut chart data, including zero data for facilities with no fuel usage
            total_fuel_used_in_operations = sum(entry['total_fuel_used_in_operations'] for entry in facility_fuel_used_in_operations)
            donut_chart_data = []

            # Get a list of all facilities for the user
            all_facilities = Facility.objects.filter(user=user)

            # Ensure all facilities are included in the donut chart, with 0% for those with no data
            for facility in all_facilities:
                # Find the fuel used in operations for each facility, or set it to 0 if no data exists
                facility_data = next((entry for entry in facility_fuel_used_in_operations if entry['facility__facility_name'] == facility.facility_name), None)
                total_fuel = facility_data['total_fuel_used_in_operations'] if facility_data else 0
                donut_chart_data.append({
                    "facility_name": facility.facility_name,
                    "percentage": (total_fuel / total_fuel_used_in_operations * 100) if total_fuel_used_in_operations else 0,
                })

            response_data = {
                "year": year,
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': f'An error occurred while processing your request: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

#StackedEnergyOverview 
class StackedEnergyOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        try:
            filters = {'user': user}

            if facility_id and facility_id.lower() != 'all':
                if not Facility.objects.filter(facility_id=facility_id, user=user).exists():
                    return Response(
                        {'error': 'Invalid facility ID or not associated with the logged-in user.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                filters['facility__facility_id'] = facility_id

            if facility_location and facility_location.lower() != 'all':
                if not Facility.objects.filter(location__icontains=facility_location).exists():
                    return Response(
                        {'error': f'No facility found with location {facility_location}.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                filters['facility__location__icontains'] = facility_location

            if year:
                try:
                    year = int(year)
                    if year < 1900 or year > datetime.now().year + 10:
                        return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)
                except ValueError:
                    return Response({'error': 'Year must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Find the latest year across all models (Water, Waste, etc.)
                latest_water_date = Water.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_waste_date = Waste.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_energy_date = Energy.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_biodiversity_date = Biodiversity.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_logistices_date = Logistices.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']

                latest_date = max(
                    filter(None, [latest_water_date, latest_waste_date, latest_energy_date, latest_biodiversity_date, latest_logistices_date]),
                    default=None
                )
                if latest_date:
                    year = latest_date.year if latest_date.month >= 4 else latest_date.year - 1
                else:
                    # Default to the current fiscal year if no data exists
                    today = datetime.now()
                    year = today.year - 1 if today.month < 4 else today.year

            # Determine fiscal year range
            start_date = datetime(year, 4, 1)
            end_date = datetime(year + 1, 3, 31)
            filters['DatePicker__range'] = (start_date, end_date)

            energy_types = [
                'hvac', 'production', 'stp', 'admin_block', 'utilities', 
                'others', 'renewable_energy'
            ]


            monthly_data = {month: {energy_type: 0 for energy_type in energy_types} for month in range(1, 13)}

            for energy_type in energy_types:
                queryset = Energy.objects.filter(**filters)

                if energy_type == 'renewable_energy':
                    monthly_energy = (
                        queryset
                        .values('DatePicker__month')
                        .annotate(
                            total=Coalesce(
                                Sum('renewable_solar') + Sum('renewable_other'),
                                Value(0, output_field=FloatField())
                            )
                        )
                        .order_by('DatePicker__month')
                    )
                else:
                    monthly_energy = (
                        queryset
                        .values('DatePicker__month')
                        .annotate(total=Coalesce(Sum(energy_type, output_field=FloatField()), Value(0, output_field=FloatField())))
                        .order_by('DatePicker__month')
                    )

                for entry in monthly_energy:
                    month = entry['DatePicker__month']
                    monthly_data[month][energy_type] = entry['total']

            
            stacked_bar_data = []
            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            for month in month_order:
                month_name = datetime(1900, month, 1).strftime('%b')
                stacked_bar_data.append({
                    "month": month_name,
                    **monthly_data[month] 
                })

            response_data = {
                "facility_id": facility_id,
                "year": year,
                "facility_location": facility_location,
                "stacked_bar_data": stacked_bar_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error occurred: {e}") 
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#EnergyAnalyticsView With Pie Chart And Donut CHart
# class EnergyAnalyticsView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         user = request.user
#         year = request.GET.get('year', None)
#         facility_id = request.GET.get('facility_id', 'all')
#         facility_location = request.GET.get('facility_location', None)

#         try:
#             filters = {'user': user}

#             today = datetime.now()
            
#             if not year:
#                 latest_energy = Energy.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))
#                 if latest_energy['latest_date']:
#                     latest_date = latest_energy['latest_date']
#                     year = latest_date.year if latest_date.month >= 4 else latest_date.year - 1
#                 else:
#                     # Default to the current fiscal year if no data exists
#                     today = datetime.now()
#                     year = today.year if today.month >= 4 else today.year - 1

#             year = int(year)
#             start_date = datetime(year, 4, 1)
#             end_date = datetime(year + 1, 3, 31)

#             filters['DatePicker__range'] = (start_date, end_date)

#             if facility_id.lower() != 'all':
#                 try:
#                     Facility.objects.get(facility_id=facility_id)
#                     filters['facility__facility_id'] = facility_id
#                 except Facility.DoesNotExist:
#                     return Response({'error': f'Facility with ID {facility_id} does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

#             if facility_location and facility_location.lower() != 'all':
#                 if not Facility.objects.filter(facility_location__icontains=facility_location).exists():
#                     return Response({'error': f'No facility found with location {facility_location}.'}, status=status.HTTP_400_BAD_REQUEST)
#                 filters['facility__facility_location__icontains'] = facility_location

#             energy_aggregate = Energy.objects.filter(**filters).aggregate(
#                 total_hvac=Coalesce(Sum('hvac', output_field=FloatField()), 0.0),
#                 total_production=Coalesce(Sum('production', output_field=FloatField()), 0.0),
#                 total_stp=Coalesce(Sum('stp', output_field=FloatField()), 0.0),
#                 total_admin_block=Coalesce(Sum('admin_block', output_field=FloatField()), 0.0),
#                 total_utilities=Coalesce(Sum('utilities', output_field=FloatField()), 0.0),
#                 total_others=Coalesce(Sum('others', output_field=FloatField()), 0.0),
#                 total_renewable_solar=Coalesce(Sum('renewable_solar', output_field=FloatField()), 0.0),
#                 total_renewable_other=Coalesce(Sum('renewable_other', output_field=FloatField()), 0.0)
#             )

#             if not energy_aggregate:
#                 energy_aggregate = {key: 0.0 for key in energy_aggregate}

#             total_renewable_energy = energy_aggregate['total_renewable_solar'] + energy_aggregate['total_renewable_other']
#             total_non_renewable_energy = (
#                 energy_aggregate['total_hvac'] +
#                 energy_aggregate['total_production'] +
#                 energy_aggregate['total_stp'] +
#                 energy_aggregate['total_admin_block'] +
#                 energy_aggregate['total_utilities'] +
#                 energy_aggregate['total_others']
#             )
#             total_energy = total_non_renewable_energy + total_renewable_energy

#             renewable_energy_percentage = (total_renewable_energy / total_energy * 100) if total_energy > 0 else 0
#             remaining_energy_percentage = (total_non_renewable_energy / total_energy * 100) if total_energy > 0 else 0
#             pie_chart_data = [
#                 {"label": "Renewable Energy", "value": renewable_energy_percentage},
#                 {"label": "Remaining Energy", "value": remaining_energy_percentage}
#             ]

#             energy_percentages = {}
#             overall_total = total_non_renewable_energy
#             for key, total in {
#                 "hvac_total": energy_aggregate['total_hvac'],
#                 "production_total": energy_aggregate['total_production'],
#                 "stp_total": energy_aggregate['total_stp'],
#                 "admin_block_total": energy_aggregate['total_admin_block'],
#                 "utilities_total": energy_aggregate['total_utilities'],
#                 "others_total": energy_aggregate['total_others']
#             }.items():
#                 energy_percentages[key] = (total / overall_total * 100) if overall_total else 0

#             # Final response data combining pie and donut chart information
#             response_data = {
#                 "facility_id": facility_id,
#                 "year": year,
#                 "facility_location": facility_location,
#                 "pie_chart_data": pie_chart_data,
#                 "energy_percentages": {key: round(value, 2) for key, value in energy_percentages.items()}

#             }

#             return Response(response_data, status=status.HTTP_200_OK)

#         except Exception as e:
#             print(f"Error occurred: {e}")
#             return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class EnergyAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        year = request.GET.get('year', None)
        facility_id = request.GET.get('facility_id', 'all')
        facility_location = request.GET.get('facility_location', None)

        try:
            filters = {'user': user}

            today = datetime.now()
            
            # Validate year and set default if not provided
            if year:
                try:
                    year = int(year)
                    if year < 1900 or year > datetime.now().year + 10:
                        return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)
                except ValueError:
                    return Response({'error': 'Year must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Find the latest year across all models (Water, Waste, etc.)
                latest_water_date = Water.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_waste_date = Waste.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_energy_date = Energy.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_biodiversity_date = Biodiversity.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_logistices_date = Logistices.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']

                latest_date = max(
                    filter(None, [latest_water_date, latest_waste_date, latest_energy_date, latest_biodiversity_date, latest_logistices_date]),
                    default=None
                )
                if latest_date:
                    year = latest_date.year if latest_date.month >= 4 else latest_date.year - 1
                else:
                    # Default to the current fiscal year if no data exists
                    today = datetime.now()
                    year = today.year - 1 if today.month < 4 else today.year

            # Determine fiscal year range
            start_date = datetime(year, 4, 1)
            end_date = datetime(year + 1, 3, 31)
            filters['DatePicker__range'] = (start_date, end_date)

            # Facility ID validation and filtering
            if facility_id.lower() != 'all':
                if not Facility.objects.filter(facility_id=facility_id, user=user).exists():
                    return Response(
                        {'error': 'Invalid facility ID or not associated with the logged-in user.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                filters['facility__facility_id'] = facility_id

            # Facility Location validation and filtering
            if facility_location and facility_location.lower() != 'all':
                if not Facility.objects.filter(location__icontains=facility_location, user=user).exists():
                    return Response(
                        {'error': f'No facility found with location {facility_location} or associated with the logged-in user.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                filters['facility__location__icontains'] = facility_location

            # Querying the Energy model with the filters
            energy_aggregate = Energy.objects.filter(**filters).aggregate(
                total_hvac=Coalesce(Sum('hvac', output_field=FloatField()), 0.0),
                total_production=Coalesce(Sum('production', output_field=FloatField()), 0.0),
                total_stp=Coalesce(Sum('stp', output_field=FloatField()), 0.0),
                total_admin_block=Coalesce(Sum('admin_block', output_field=FloatField()), 0.0),
                total_utilities=Coalesce(Sum('utilities', output_field=FloatField()), 0.0),
                total_others=Coalesce(Sum('others', output_field=FloatField()), 0.0),
                total_renewable_solar=Coalesce(Sum('renewable_solar', output_field=FloatField()), 0.0),
                total_renewable_other=Coalesce(Sum('renewable_other', output_field=FloatField()), 0.0)
            )

            if not energy_aggregate:
                energy_aggregate = {key: 0.0 for key in energy_aggregate}

            # Calculate total energy values
            total_renewable_energy = energy_aggregate['total_renewable_solar'] + energy_aggregate['total_renewable_other']
            total_non_renewable_energy = (
                energy_aggregate['total_hvac'] +
                energy_aggregate['total_production'] +
                energy_aggregate['total_stp'] +
                energy_aggregate['total_admin_block'] +
                energy_aggregate['total_utilities'] +
                energy_aggregate['total_others']
            )
            total_energy = total_non_renewable_energy + total_renewable_energy

            # Calculate percentages
            renewable_energy_percentage = (total_renewable_energy / total_energy * 100) if total_energy > 0 else 0
            remaining_energy_percentage = (total_non_renewable_energy / total_energy * 100) if total_energy > 0 else 0
            pie_chart_data = [
                {"label": "Renewable Energy", "value": renewable_energy_percentage},
                {"label": "Remaining Energy", "value": remaining_energy_percentage}
            ]

            energy_percentages = {}
            overall_total = total_non_renewable_energy
            for key, total in {
                "hvac_total": energy_aggregate['total_hvac'],
                "production_total": energy_aggregate['total_production'],
                "stp_total": energy_aggregate['total_stp'],
                "admin_block_total": energy_aggregate['total_admin_block'],
                "utilities_total": energy_aggregate['total_utilities'],
                "others_total": energy_aggregate['total_others']
            }.items():
                energy_percentages[key] = (total / overall_total * 100) if overall_total else 0

            # Final response data combining pie and donut chart information
            response_data = {
                "facility_id": facility_id,
                "year": year,
                "facility_location": facility_location,
                "pie_chart_data": pie_chart_data,
                "energy_percentages": {key: round(value, 2) for key, value in energy_percentages.items()}
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error occurred: {e}")
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

'''Energy  Overview Cards ,Graphs and Individual line charts and donut charts Ends'''

'''Water Overview Cards ,Graphs and Individual Line Charts and donut Charts Starts'''
#Water Card OverView
class WaterViewCard_Over(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', 'all')
        facility_location = request.GET.get('facility_location')
        year = request.GET.get('year')

        try:
            # Validate facility ID
            if facility_id != 'all' and not Facility.objects.filter(facility_id=facility_id, user=user).exists():
                return Response({'error': 'Invalid facility ID or not associated with the logged-in user.'}, status=status.HTTP_400_BAD_REQUEST)

            # Determine fiscal year range
            if year:
                try:
                    year = int(year)
                    if year < 1900 or year > datetime.now().year + 10:
                        return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)
                except ValueError:
                    return Response({'error': 'Year must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Find the latest year across all models (Water, Waste, etc.)
                latest_water_date = Water.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_waste_date = Waste.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_energy_date = Energy.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_biodiversity_date = Biodiversity.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_logistices_date = Logistices.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                
                
                latest_date = max(filter(None, [latest_water_date, latest_waste_date,latest_energy_date,latest_biodiversity_date,latest_logistices_date]), default=None)
                if latest_date:
                    year = latest_date.year if latest_date.month >= 4 else latest_date.year - 1
                else:
                    # Default to the current fiscal year if no data exists
                    today = datetime.now()
                    year = today.year - 1 if today.month < 4 else today.year

            start_date = datetime(year, 4, 1)
            end_date = datetime(year + 1, 3, 31)

            # Query water data
            water_data = Water.objects.filter(user=user, DatePicker__range=(start_date, end_date))

            if facility_id != 'all':
                water_data = water_data.filter(facility__facility_id=facility_id)

            if facility_location:
                water_data = water_data.filter(facility__location__icontains=facility_location)

            # Water fields for aggregation
            water_fields = [
                'Generated_Water', 'Recycled_Water', 'Softener_usage', 'Boiler_usage', 'otherUsage'
            ]

            # Calculate overall totals
            overall_totals = {
                f"overall_{field}": water_data.aggregate(total=Sum(field))['total'] or 0 for field in water_fields
            }

            if not water_data.exists():
                response_data = {
                    'year': year,
                    'message': f"No data available for the year {year}.",
                    'overall_water_totals': {f"overall_{field}": 0 for field in water_fields},
                }
            else:
                response_data = {
                    'year': year,
                    'overall_water_totals': overall_totals,
                }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            print(error_message)
            return Response({'error': error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#GeneratedWater Overview Line Charts and Donut Chart
class Generated_WaterOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        try:
            if year:
                try:
                    year = int(year)
                    if year < 1900 or year > datetime.now().year + 10:
                        return Response({'error': 'Invalid year parameter.'}, status=400)
                except ValueError:
                    return Response({'error': 'Year must be an integer.'}, status=400)
            else:
                year = self.get_latest_available_year(user)

            start_date, end_date = self.get_fiscal_year_range(year)

            filters = {
                'user': user,
                'DatePicker__range': (start_date.date(), end_date.date())
            }
            if facility_id and facility_id.lower() != 'all':
                filters['facility__facility_id'] = facility_id
            if facility_location:
                filters['facility__location__icontains'] = facility_location

            water_data = Water.objects.filter(**filters)
            if not water_data.exists():
                return self.get_empty_response(year)

            monthly_Generated_Water = (
                water_data
                .values('DatePicker__month')
                .annotate(total_Generated_Water=Sum('Generated_Water'))
            )

            Generated_Water = {month: 0 for month in range(1, 13)}
            for entry in monthly_Generated_Water:
                Generated_Water[entry['DatePicker__month']] = entry['total_Generated_Water']

            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            line_chart_data = [
                {
                    "month": datetime(1900, month, 1).strftime('%b'),
                    "Generated_Water": Generated_Water[month]
                }
                for month in month_order
            ]

            # Prepare facility data for donut chart
            facility_Generated_Water = (
                water_data
                .values('facility__facility_name')
                .annotate(total_Generated_Water=Sum('Generated_Water'))
                .order_by('-total_Generated_Water')
            )

            total_Generated_Water = sum(entry['total_Generated_Water'] for entry in facility_Generated_Water)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_Generated_Water'] / total_Generated_Water * 100) if total_Generated_Water else 0,
                }
                for entry in facility_Generated_Water
            ]

            response_data = {
                "year": year,
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=200)

        except Exception as e:
            import traceback
            print(f"Error: {str(e)}")
            print("Traceback:", traceback.format_exc())
            return Response(
                {'error': f'An error occurred while processing your request: {str(e)}'},
                status=500
            )

    def get_latest_available_year(self, user):
        # Find the latest date across all models
        latest_water_date = Water.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_waste_date = Waste.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_energy_date = Energy.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_biodiversity_date = Biodiversity.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_logistices_date = Logistices.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']

        latest_date = max(
            filter(None, [latest_water_date, latest_waste_date, latest_energy_date, latest_biodiversity_date, latest_logistices_date]),
            default=None
        )

        if latest_date:
            return latest_date.year if latest_date.month >= 4 else latest_date.year - 1
        today = datetime.now()
        return today.year - 1 if today.month < 4 else today.year

    def get_fiscal_year_range(self, year):
        start_date = datetime(year, 4, 1)
        end_date = datetime(year + 1, 3, 31)
        return start_date, end_date

    def get_empty_response(self, year):
        month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
        line_chart_data = [{"month": datetime(1900, month, 1).strftime('%b'), "Generated_Water": 0} for month in month_order]
        donut_chart_data = [{"facility_name": "No Facility", "percentage": 0}]
        return Response({
            "year": year,
            "line_chart_data": line_chart_data,
            "donut_chart_data": donut_chart_data
        }, status=200)

#Recycle Water Overview line charts and Donut chart
class Recycle_WaterOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        try:
            if year:
                try:
                    year = int(year)
                    if year < 1900 or year > datetime.now().year + 10:
                        return Response({'error': 'Invalid year parameter.'}, status=400)
                except ValueError:
                    return Response({'error': 'Year must be an integer.'}, status=400)
            else:
                year = self.get_latest_available_year(user)

            start_date, end_date = self.get_fiscal_year_range(year)

            filters = {
                'user': user,
                'DatePicker__range': (start_date.date(), end_date.date())
            }
            if facility_id and facility_id.lower() != 'all':
                filters['facility__facility_id'] = facility_id
            if facility_location:
                filters['facility__location__icontains'] = facility_location

            water_data = Water.objects.filter(**filters)
            if not water_data.exists():
                return self.get_empty_response(year)

            monthly_Recycled_Water = (
                water_data
                .values('DatePicker__month')
                .annotate(total_Recycled_Water=Sum('Recycled_Water'))
            )

            Recycled_Water = {month: 0 for month in range(1, 13)}
            for entry in monthly_Recycled_Water:
                Recycled_Water[entry['DatePicker__month']] = entry['total_Recycled_Water']

            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            line_chart_data = [
                {
                    "month": datetime(1900, month, 1).strftime('%b'),
                    "Recycled_Water": Recycled_Water[month]
                }
                for month in month_order
            ]

            # Prepare facility data for donut chart
            facility_Recycled_Water = (
                water_data
                .values('facility__facility_name')
                .annotate(total_Recycled_Water=Sum('Recycled_Water'))
                .order_by('-total_Recycled_Water')
            )

            total_Recycled_Water = sum(entry['total_Recycled_Water'] for entry in facility_Recycled_Water)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_Recycled_Water'] / total_Recycled_Water * 100) if total_Recycled_Water else 0,
                }
                for entry in facility_Recycled_Water
            ]

            response_data = {
                "year": year,
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            print(f"Error: {str(e)}")
            print("Traceback:", traceback.format_exc())
            return Response(
                {'error': f'An error occurred while processing your request: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_latest_available_year(self, user):
        # Find the latest date across all models
        latest_water_date = Water.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_waste_date = Waste.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_energy_date = Energy.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_biodiversity_date = Biodiversity.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_logistices_date = Logistices.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']

        latest_date = max(
            filter(None, [latest_water_date, latest_waste_date, latest_energy_date, latest_biodiversity_date, latest_logistices_date]),
            default=None
        )

        if latest_date:
            return latest_date.year if latest_date.month >= 4 else latest_date.year - 1
        today = datetime.now()
        return today.year - 1 if today.month < 4 else today.year

    
    def get_fiscal_year_range(self, year):
        start_date = datetime(year, 4, 1)
        end_date = datetime(year + 1, 3, 31)
        return start_date, end_date

    def get_empty_response(self, year):
        month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
        line_chart_data = [{"month": datetime(1900, month, 1).strftime('%b'), "Recycled_Water": 0} for month in month_order]
        donut_chart_data = [{"facility_name": "No Facility", "percentage": 0}]
        return Response({
            "year": year,
            "line_chart_data": line_chart_data,
            "donut_chart_data": donut_chart_data
        }, status=status.HTTP_200_OK)

#SoftenSoftener_usage overview line chart and donut chart
class Softener_usageOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        try:
            if year:
                try:
                    year = int(year)
                    if year < 1900 or year > datetime.now().year + 10:
                        return Response({'error': 'Invalid year parameter.'}, status=400)
                except ValueError:
                    return Response({'error': 'Year must be an integer.'}, status=400)
            else:
                year = self.get_latest_available_year(user)

            start_date, end_date = self.get_fiscal_year_range(year)

            filters = {
                'user': user,
                'DatePicker__range': (start_date.date(), end_date.date())
            }
            if facility_id and facility_id.lower() != 'all':
                filters['facility__facility_id'] = facility_id
            if facility_location:
                filters['facility__location__icontains'] = facility_location

            water_data = Water.objects.filter(**filters)
            if not water_data.exists():
                return self.get_empty_response(year)

            monthly_Softener_usage = (
                water_data
                .values('DatePicker__month')
                .annotate(total_Softener_usage=Sum('Softener_usage'))
            )

            Softener_usage = {month: 0 for month in range(1, 13)}
            for entry in monthly_Softener_usage:
                Softener_usage[entry['DatePicker__month']] = entry['total_Softener_usage']

            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            line_chart_data = [
                {
                    "month": datetime(1900, month, 1).strftime('%b'),
                    "Softener_usage": Softener_usage[month]
                }
                for month in month_order
            ]

            # Prepare facility data for donut chart
            facility_Softener_usage = (
                water_data
                .values('facility__facility_name')
                .annotate(total_Softener_usage=Sum('Softener_usage'))
                .order_by('-total_Softener_usage')
            )

            total_Softener_usage = sum(entry['total_Softener_usage'] for entry in facility_Softener_usage)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_Softener_usage'] / total_Softener_usage * 100) if total_Softener_usage else 0,
                }
                for entry in facility_Softener_usage
            ]

            response_data = {
                "year": year,
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            print(f"Error: {str(e)}")
            print("Traceback:", traceback.format_exc())
            return Response(
                {'error': f'An error occurred while processing your request: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_latest_available_year(self, user):
        # Find the latest date across all models
        latest_water_date = Water.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_waste_date = Waste.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_energy_date = Energy.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_biodiversity_date = Biodiversity.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_logistices_date = Logistices.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']

        latest_date = max(
            filter(None, [latest_water_date, latest_waste_date, latest_energy_date, latest_biodiversity_date, latest_logistices_date]),
            default=None
        )

        if latest_date:
            return latest_date.year if latest_date.month >= 4 else latest_date.year - 1
        today = datetime.now()
        return today.year - 1 if today.month < 4 else today.year

    
    def get_fiscal_year_range(self, year):
        start_date = datetime(year, 4, 1)
        end_date = datetime(year + 1, 3, 31)
        return start_date, end_date

    def get_empty_response(self, year):
        month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
        line_chart_data = [{"month": datetime(1900, month, 1).strftime('%b'), "Softener_usage": 0} for month in month_order]
        donut_chart_data = [{"facility_name": "No Facility", "percentage": 0}]
        return Response({
            "year": year,
            "line_chart_data": line_chart_data,
            "donut_chart_data": donut_chart_data
        }, status=status.HTTP_200_OK)

#Boiler_usage Overview line chart and Donut Chart
class Boiler_usageOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        try:
            if year:
                try:
                    year = int(year)
                    if year < 1900 or year > datetime.now().year + 10:
                        return Response({'error': 'Invalid year parameter.'}, status=400)
                except ValueError:
                    return Response({'error': 'Year must be an integer.'}, status=400)
            else:
                year = self.get_latest_available_year(user)

            start_date, end_date = self.get_fiscal_year_range(year)

            filters = {
                'user': user,
                'DatePicker__range': (start_date.date(), end_date.date())
            }
            if facility_id and facility_id.lower() != 'all':
                filters['facility__facility_id'] = facility_id
            if facility_location:
                filters['facility__location__icontains'] = facility_location

            water_data = Water.objects.filter(**filters)
            if not water_data.exists():
                return self.get_empty_response(year)

            monthly_Boiler_usage = (
                water_data
                .values('DatePicker__month')
                .annotate(total_Boiler_usage=Sum('Boiler_usage'))
            )

            Boiler_usage = {month: 0 for month in range(1, 13)}
            for entry in monthly_Boiler_usage:
                Boiler_usage[entry['DatePicker__month']] = entry['total_Boiler_usage']

            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            line_chart_data = [
                {
                    "month": datetime(1900, month, 1).strftime('%b'),
                    "Boiler_usage": Boiler_usage[month]
                }
                for month in month_order
            ]

            # Prepare facility data for donut chart
            facility_Boiler_usage = (
                water_data
                .values('facility__facility_name')
                .annotate(total_Boiler_usage=Sum('Boiler_usage'))
                .order_by('-total_Boiler_usage')
            )

            total_Boiler_usage = sum(entry['total_Boiler_usage'] for entry in facility_Boiler_usage)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_Boiler_usage'] / total_Boiler_usage * 100) if total_Boiler_usage else 0,
                }
                for entry in facility_Boiler_usage
            ]

            response_data = {
                "year": year,
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            print(f"Error: {str(e)}")
            print("Traceback:", traceback.format_exc())
            return Response(
                {'error': f'An error occurred while processing your request: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_latest_available_year(self, user):
        # Find the latest date across all models
        latest_water_date = Water.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_waste_date = Waste.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_energy_date = Energy.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_biodiversity_date = Biodiversity.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_logistices_date = Logistices.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']

        latest_date = max(
            filter(None, [latest_water_date, latest_waste_date, latest_energy_date, latest_biodiversity_date, latest_logistices_date]),
            default=None
        )

        if latest_date:
            return latest_date.year if latest_date.month >= 4 else latest_date.year - 1
        today = datetime.now()
        return today.year - 1 if today.month < 4 else today.year


    def get_fiscal_year_range(self, year):
        start_date = datetime(year, 4, 1)
        end_date = datetime(year + 1, 3, 31)
        return start_date, end_date

    def get_empty_response(self, year):
        month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
        line_chart_data = [{"month": datetime(1900, month, 1).strftime('%b'), "Boiler_usage": 0} for month in month_order]
        donut_chart_data = [{"facility_name": "No Facility", "percentage": 0}]
        return Response({
            "year": year,
            "line_chart_data": line_chart_data,
            "donut_chart_data": donut_chart_data
        }, status=status.HTTP_200_OK)

#otherUsage overview line chart and Donut chart
class otherUsage_OverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        try:
            
            if year:
                try:
                    year = int(year)
                    if year < 1900 or year > datetime.now().year + 10:
                        return Response({'error': 'Invalid year parameter.'}, status=400)
                except ValueError:
                    return Response({'error': 'Year must be an integer.'}, status=400)
            else:
                year = self.get_latest_available_year(user)

            start_date, end_date = self.get_fiscal_year_range(year)

            filters = {
                'user': user,
                'DatePicker__range': (start_date.date(), end_date.date())
            }
            if facility_id and facility_id.lower() != 'all':
                filters['facility__facility_id'] = facility_id
            if facility_location:
                filters['facility__location__icontains'] = facility_location

            water_data = Water.objects.filter(**filters)
            if not water_data.exists():
                return self.get_empty_response(year)

            monthly_otherUsage = (
                water_data
                .values('DatePicker__month')
                .annotate(total_otherUsage=Sum('otherUsage'))
            )

            otherUsage = {month: 0 for month in range(1, 13)}
            for entry in monthly_otherUsage:
                otherUsage[entry['DatePicker__month']] = entry['total_otherUsage']

            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            line_chart_data = [
                {
                    "month": datetime(1900, month, 1).strftime('%b'),
                    "otherUsage": otherUsage[month]
                }
                for month in month_order
            ]

            # Prepare facility data for donut chart
            facility_otherUsage = (
                water_data
                .values('facility__facility_name')
                .annotate(total_otherUsage=Sum('otherUsage'))
                .order_by('-total_otherUsage')
            )

            total_otherUsage = sum(entry['total_otherUsage'] for entry in facility_otherUsage)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_otherUsage'] / total_otherUsage * 100) if total_otherUsage else 0,
                }
                for entry in facility_otherUsage
            ]

            response_data = {
                "year": year,
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            print(f"Error: {str(e)}")
            print("Traceback:", traceback.format_exc())
            return Response(
                {'error': f'An error occurred while processing your request: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_latest_available_year(self, user):
        # Find the latest date across all models
        latest_water_date = Water.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_waste_date = Waste.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_energy_date = Energy.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_biodiversity_date = Biodiversity.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
        latest_logistices_date = Logistices.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']

        latest_date = max(
            filter(None, [latest_water_date, latest_waste_date, latest_energy_date, latest_biodiversity_date, latest_logistices_date]),
            default=None
        )

        if latest_date:
            return latest_date.year if latest_date.month >= 4 else latest_date.year - 1
        today = datetime.now()
        return today.year - 1 if today.month < 4 else today.year

    def get_fiscal_year_range(self, year):
        start_date = datetime(year, 4, 1)
        end_date = datetime(year + 1, 3, 31)
        return start_date, end_date

    def get_empty_response(self, year):
        month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
        line_chart_data = [{"month": datetime(1900, month, 1).strftime('%b'), "otherUsage": 0} for month in month_order]
        donut_chart_data = [{"facility_name": "No Facility", "percentage": 0}]
        return Response({
            "year": year,
            "line_chart_data": line_chart_data,
            "donut_chart_data": donut_chart_data
        }, status=status.HTTP_200_OK)

#Stacked Graph Overview 
class StackedWaterOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        try:
            filters = {'user': user}

            if facility_id and facility_id.lower() != 'all':
                if not Facility.objects.filter(facility_id=facility_id, user=user).exists():
                    return Response(
                        {'error': 'Invalid facility ID or not associated with the logged-in user.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                filters['facility__facility_id'] = facility_id

            if facility_location and facility_location.lower() != 'all':
                if not Facility.objects.filter(location__icontains=facility_location).exists():
                    return Response(
                        {'error': f'No facility found with location {facility_location}.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                filters['facility__location__icontains'] = facility_location

            if year:
                try:
                    year = int(year)
                    if year < 1900 or year > datetime.now().year + 10:
                        return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)
                except ValueError:
                    return Response({'error': 'Year must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Find the latest year across all models (Water, Waste, etc.)
                latest_water_date = Water.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_waste_date = Waste.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_energy_date = Energy.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_biodiversity_date = Biodiversity.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_logistices_date = Logistices.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']

                latest_date = max(
                    filter(None, [latest_water_date, latest_waste_date, latest_energy_date, latest_biodiversity_date, latest_logistices_date]),
                    default=None
                )
                if latest_date:
                    year = latest_date.year if latest_date.month >= 4 else latest_date.year - 1
                else:
                    # Default to the current fiscal year if no data exists
                    today = datetime.now()
                    year = today.year - 1 if today.month < 4 else today.year

            # Determine fiscal year range
            start_date = datetime(year, 4, 1)
            end_date = datetime(year + 1, 3, 31)
            filters['DatePicker__range'] = (start_date, end_date)

            water_types = [
                'Generated_Water', 'Recycled_Water', 'Softener_usage', 'Boiler_usage', 'otherUsage'
            ]

            monthly_data = {month: {water_type: 0 for water_type in water_types} for month in range(1, 13)}

            for water_type in water_types:
                queryset = Water.objects.filter(**filters)

                monthly_water = (
                    queryset
                    .values('DatePicker__month')
                    .annotate(
                        total=Coalesce(Sum(water_type, output_field=FloatField()), Value(0, output_field=FloatField()))
                    )
                    .order_by('DatePicker__month')
                )

                for entry in monthly_water:
                    month = entry['DatePicker__month']
                    monthly_data[month][water_type] = entry['total']

            stacked_bar_data = []
            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            for month in month_order:
                month_name = datetime(1900, month, 1).strftime('%b')
                stacked_bar_data.append({
                    "month": month_name,
                    **monthly_data[month]
                })

            response_data = {
                "facility_id": facility_id,
                "year": year,
                "facility_location": facility_location,
                "stacked_bar_data": stacked_bar_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error occurred: {e}")
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#Water Anaytics Donut Chart And Line Graph
class WaterAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        year = request.GET.get('year', None)
        facility_id = request.GET.get('facility_id', 'all')
        facility_location = request.GET.get('facility_location', None)

        try:
            filters = {'user': user}

            # Validate facility ID
            if facility_id != 'all' and not Facility.objects.filter(facility_id=facility_id, user=user).exists():
                return Response({'error': 'Invalid facility ID or not associated with the logged-in user.'}, status=status.HTTP_400_BAD_REQUEST)
            elif facility_id != 'all':
                filters['facility__facility_id'] = facility_id

            # Facility location filtering
            if facility_location and facility_location.lower() != 'all':
                if not Facility.objects.filter(facility_location__icontains=facility_location).exists():
                    return Response({'error': f'No facility found with location {facility_location}.'}, status=status.HTTP_400_BAD_REQUEST)
                filters['facility__facility_location__icontains'] = facility_location

            # Year calculation
            if year:
                try:
                    year = int(year)
                    if year < 1900 or year > datetime.now().year + 10:
                        return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)
                except ValueError:
                    return Response({'error': 'Year must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Find the latest year across all models
                latest_water_date = Water.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_waste_date = Waste.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_energy_date = Energy.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_biodiversity_date = Biodiversity.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_logistics_date = Logistices.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']

                latest_date = max(filter(None, [latest_water_date, latest_waste_date, latest_energy_date, latest_biodiversity_date, latest_logistics_date]), default=None)
                if latest_date:
                    year = latest_date.year if latest_date.month >= 4 else latest_date.year - 1
                else:
                    # Default to the current fiscal year if no data exists
                    today = datetime.now()
                    year = today.year - 1 if today.month < 4 else today.year

            # Determine fiscal year range
            start_date = datetime(year, 4, 1)
            end_date = datetime(year + 1, 3, 31)
            filters['DatePicker__range'] = (start_date, end_date)

            # Query Water data
            queryset = Water.objects.filter(**filters)
            if not queryset.exists():
                return Response({
                    "year": year,
                    "facility_id": facility_id,
                    "facility_location": facility_location,
                    "donut_chart_data": {
                        "Softener_Usage": 0,
                        "Boiler_Usage": 0,
                        "Other_Usage": 0
                    },
                    "pie_chart_data": [
                        {"label": "Recycled Water", "value": 0},
                        {"label": "Remaining Water", "value": 0}
                    ]
                }, status=status.HTTP_200_OK)

            # Aggregations
            water_totals = queryset.aggregate(
                Softener_usage_total=Coalesce(Sum(Cast('Softener_usage', FloatField())), 0.0),
                Boiler_usage_total=Coalesce(Sum(Cast('Boiler_usage', FloatField())), 0.0),
                otherUsage_total=Coalesce(Sum(Cast('otherUsage', FloatField())), 0.0),
                Generated_Water_total=Coalesce(Sum(Cast('Generated_Water', FloatField())), 0.0),
                Recycled_Water_total=Coalesce(Sum(Cast('Recycled_Water', FloatField())), 0.0)
            )

            # Normalize donut chart percentages
            total_usage = (
                water_totals['Softener_usage_total'] +
                water_totals['Boiler_usage_total'] +
                water_totals['otherUsage_total']
            )
            water_percentages = {
                "Softener_Usage": (water_totals['Softener_usage_total'] / total_usage * 100) if total_usage else 0,
                "Boiler_Usage": (water_totals['Boiler_usage_total'] / total_usage * 100) if total_usage else 0,
                "Other_Usage": (water_totals['otherUsage_total'] / total_usage * 100) if total_usage else 0
            }

            # Pie chart data
            generated_recycled_total = (
                water_totals['Generated_Water_total'] +
                water_totals['Recycled_Water_total']
            )
            recycled_water = water_totals['Recycled_Water_total']
            remaining_water = generated_recycled_total - recycled_water
            pie_chart_data = [
                {"label": "Recycled Water", "value": (recycled_water / generated_recycled_total * 100) if generated_recycled_total else 0},
                {"label": "Remaining Water", "value": (remaining_water / generated_recycled_total * 100) if generated_recycled_total else 0}
            ]

            return Response({
                "year": year,
                "facility_id": facility_id,
                "facility_location": facility_location,
                "donut_chart_data": {key: round(value, 2) for key, value in water_percentages.items()},
                "pie_chart_data": pie_chart_data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logging.error(f"Error in WaterAnalyticsView: {e}")
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

'''Water Overview Cards ,Graphs and Individual Line Charts and donut Charts Ends'''

# '''Biodiversity Overview Cards Starts'''

# class BiodiversityMetricsGraphsView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         user = request.user
#         facility_id = request.GET.get('facility_id', 'all')

#         try:
#             # Filters for user and facility
#             filters = {'user': user}
#             if facility_id != 'all':
#                 filters['facility__facility_id'] = facility_id

#             # Query all data for the user and facility
#             all_years_data = Biodiversity.objects.filter(**filters)

#             if not all_years_data.exists():
#                 return Response(
#                     {
#                         "facility_id": facility_id,
#                         "year": None,
#                         "current_year_metrics": {
#                             "total_trees": 0,
#                             "carbon_offset": 0,
#                             "green_belt_density": 0,
#                             "trees_per_capita": 0,
#                             "new_trees_planted": 0,
#                             "biomass": 0,
#                             "co2_sequestration_rate": 0,
#                         },
#                         "Offset_year": [
#                             {"year": 0, "carbon_offset": 0}
#                         ],
#                         "Green_Belt_Density": [
#                             {"year": 0, "green_belt_density": 0}
#                         ],
#                         "Trees_Per_Capita": [
#                             {"year": 0, "trees_per_capita": 0}
#                         ],
#                     },
#                     status=status.HTTP_200_OK,
#                 )

#             # Get the latest date if no year is specified
#             latest_date = all_years_data.aggregate(latest_date=Max('DatePicker'))['latest_date']
#             if not latest_date:
#                 return Response({'error': 'No data available in the database.'}, status=status.HTTP_404_NOT_FOUND)

#             # Get the fiscal year for the latest data
#             latest_year = self.get_fiscal_year(latest_date)
#             year = request.GET.get('year', latest_year)

#             try:
#                 year = int(year)
#             except ValueError:
#                 return Response({'error': 'Invalid year provided.'}, status=status.HTTP_400_BAD_REQUEST)

#             # Define fiscal year ranges for filtering
#             start_date = datetime(year, 4, 1)  # Start of fiscal year (April 1st)
#             end_date = datetime(year + 1, 3, 31)  # End of fiscal year (March 31st)

#             # Filter data for the current year
#             current_year_data = all_years_data.filter(DatePicker__gte=start_date, DatePicker__lte=end_date)
#             prev_year_data = all_years_data.filter(DatePicker__year=year - 1, DatePicker__month__gte=4)  # Data from previous fiscal year

#             # Aggregate yearly metrics
#             yearly_data = {}
#             for entry in all_years_data.values('DatePicker', 'width', 'height', 'no_trees', 'totalArea', 'head_count'):
#                 entry_year = self.get_fiscal_year(entry['DatePicker'])
#                 if entry_year not in yearly_data:
#                     yearly_data[entry_year] = {'no_trees': 0, 'width': 0, 'height': 0, 'totalArea': 0, 'head_count': 0}
#                 yearly_data[entry_year]['no_trees'] += entry['no_trees'] or 0
#                 yearly_data[entry_year]['width'] += entry['width'] or 0
#                 yearly_data[entry_year]['height'] += entry['height'] or 0
#                 yearly_data[entry_year]['totalArea'] += entry['totalArea'] or 0
#                 yearly_data[entry_year]['head_count'] += entry['head_count'] or 0

#             # Compute metrics for each year
#             results = []
#             for entry_year, data in yearly_data.items():
#                 total_trees = data['no_trees']
#                 carbon_offset = 0.00006 * (data['width'] ** 2) * data['height'] * total_trees
#                 green_belt_density = (total_trees / data['totalArea']) * 10000 if data['totalArea'] > 0 else 0
#                 trees_per_capita = total_trees / data['head_count'] if data['head_count'] > 0 else 0
#                 results.append({
#                     'year': entry_year,
#                     'carbon_offset': carbon_offset,
#                     'green_belt_density': green_belt_density,
#                     'trees_per_capita': trees_per_capita,
#                 })

#             # Sort results by year
#             results.sort(key=lambda x: x['year'])
#             results = results[:5]  # Limit to 5 most recent years

#             # Prepare chart data in the requested structure
#             offset_year_data = [{"year": r['year'], "carbon_offset": r['carbon_offset']} for r in results]
#             green_belt_density_data = [{"year": r['year'], "green_belt_density": r['green_belt_density']} for r in results]
#             trees_per_capita_data = [{"year": r['year'], "trees_per_capita": r['trees_per_capita']} for r in results]

#             # Prepare metrics for the current year
#             total_trees = green_belt_density = trees_per_capita = new_trees_planted = biomass = 0
#             carbon_offset = co2_sequestration_rate = 0

#             if current_year_data.exists():
#                 total_trees, green_belt_density, trees_per_capita, new_trees_planted = self.calculate_metrics(current_year_data)
#                 carbon_offset = self.calculate_co2(current_year_data)
#                 biomass = self.calculate_biomass(current_year_data)
#                 co2_sequestration_rate = self.calculate_co2_sequestration_rate(all_years_data, current_year_data)
            
#             # Response structure
#             response_data = {
#                 "facility_id": facility_id,
#                 "year": year,
#                 "current_year_metrics": {
#                     "total_trees": total_trees,
#                     "carbon_offset": carbon_offset,
#                     "green_belt_density": green_belt_density,
#                     "trees_per_capita": trees_per_capita,
#                     "new_trees_planted": new_trees_planted,
#                     "biomass": biomass,
#                     "co2_sequestration_rate": co2_sequestration_rate,
#                 },
#                 "Offset_year": offset_year_data,
#                 "Green_Belt_Density": green_belt_density_data,
#                 "Trees_Per_Capita": trees_per_capita_data,
#             }

#             return Response(response_data, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def get_fiscal_year(self, date):
#         """Returns the fiscal year based on a given date."""
#         if date.month >= 4:
#             return date.year
#         return date.year - 1

#     def calculate_co2(self, data):
#         return sum(
#             0.00006 *
#             (entry['width'] or 0) ** 2 *
#             (entry['height'] or 0) *
#             (entry['no_trees'] or 0)
#             for entry in data.values('width', 'height', 'no_trees')
#         )

#     def calculate_biomass(self, data):
#         return sum(
#             0.0998 *
#             (entry['width'] or 0) ** 2 *
#             (entry['height'] or 0)
#             for entry in data.values('width', 'height')
#         )

#     def calculate_metrics(self, data):
#         aggregated = data.aggregate(
#             total_trees=Sum('no_trees'),
#             total_area=Sum('totalArea'),
#             head_count=Sum('head_count'),
#             new_trees_planted=Sum('new_trees_planted')
#         )
#         total_trees = aggregated.get('total_trees', 0)
#         total_area = aggregated.get('total_area', 0)
#         head_count = aggregated.get('head_count', 0)
#         new_trees_planted = aggregated.get('new_trees_planted', 0)

#         green_belt_density = (total_trees / total_area) * 10000 if total_area > 0 else 0
#         trees_per_capita = total_trees / head_count if head_count > 0 else 0

#         return total_trees, green_belt_density, trees_per_capita, new_trees_planted

#     def calculate_co2_sequestration_rate(self, all_years_data, current_year_data):
#         # Get the current year from the current year's data
#         current_year = current_year_data.first().DatePicker.year

#         # Fetch data for the previous year
#         prev_year_data = all_years_data.filter(DatePicker__year=current_year - 1)

#         # Calculate CO2 sequestration rate
#         current_year_co2 = self.calculate_co2(current_year_data)
#         prev_year_co2 = self.calculate_co2(prev_year_data) if prev_year_data.exists() else 0

#         # Return the difference, or current_year_co2 if there's no previous year data
#         return current_year_co2 - prev_year_co2

class BiodiversityMetricsGraphsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', 'all')
        facility_location = request.GET.get('facility_location', 'all')
        year = request.GET.get('year')

        try:
            # Filters for user and optional parameters
            filters = {'user': user}

            if facility_id and facility_id.lower() != 'all':
                if not Facility.objects.filter(facility_id=facility_id, user=user).exists():
                    return Response(
                        {'error': 'Invalid facility ID or not associated with the logged-in user.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                filters['facility__facility_id'] = facility_id

            if facility_location and facility_location.lower() != 'all':
                if not Facility.objects.filter(location__icontains=facility_location).exists():
                    return Response(
                        {'error': f'No facility found with location {facility_location}.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                filters['facility__location__icontains'] = facility_location

            if year:
                try:
                    year = int(year)
                    if year < 1900 or year > datetime.now().year + 10:
                        return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)
                except ValueError:
                    return Response({'error': 'Year must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Find the latest year across all related models
                latest_water_date = Water.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_waste_date = Waste.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_energy_date = Energy.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_biodiversity_date = Biodiversity.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_logistices_date = Logistices.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']

                latest_date = max(
                    filter(None, [latest_water_date, latest_waste_date, latest_energy_date, latest_biodiversity_date, latest_logistices_date]),
                    default=None
                )
                if latest_date:
                    year = latest_date.year if latest_date.month >= 4 else latest_date.year - 1
                else:
                    # Default to the current fiscal year if no data exists
                    today = datetime.now()
                    year = today.year - 1 if today.month < 4 else today.year

            # Determine fiscal year range
            start_date = datetime(year, 4, 1)
            end_date = datetime(year + 1, 3, 31)
            filters['DatePicker__range'] = (start_date, end_date)

            # Query all data for the user with the filters
            all_years_data = Biodiversity.objects.filter(**filters)

            if not all_years_data.exists():
                return Response(
                    {
                        "facility_id": facility_id,
                        "year": year,
                        "current_year_metrics": {
                            "total_trees": 0,
                            "carbon_offset": 0,
                            "green_belt_density": 0,
                            "trees_per_capita": 0,
                            "new_trees_planted": 0,
                            "biomass": 0,
                            "co2_sequestration_rate": 0,
                        },
                        "Offset_year": [{"year": 0, "carbon_offset": 0}],
                        "Green_Belt_Density": [{"year": 0, "green_belt_density": 0}],
                        "Trees_Per_Capita": [{"year": 0, "trees_per_capita": 0}],
                    },
                    status=status.HTTP_200_OK,
                )

            # Aggregate yearly metrics
            yearly_data = {}
            for entry in all_years_data.values('DatePicker', 'width', 'height', 'no_trees', 'totalArea', 'head_count'):
                entry_year = self.get_fiscal_year(entry['DatePicker'])
                if entry_year not in yearly_data:
                    yearly_data[entry_year] = {'no_trees': 0, 'width': 0, 'height': 0, 'totalArea': 0, 'head_count': 0}
                yearly_data[entry_year]['no_trees'] += entry['no_trees'] or 0
                yearly_data[entry_year]['width'] += entry['width'] or 0
                yearly_data[entry_year]['height'] += entry['height'] or 0
                yearly_data[entry_year]['totalArea'] += entry['totalArea'] or 0
                yearly_data[entry_year]['head_count'] += entry['head_count'] or 0

            # Compute metrics for each year
            results = []
            for entry_year, data in yearly_data.items():
                total_trees = data['no_trees']
                carbon_offset = 0.00006 * (data['width'] ** 2) * data['height'] * total_trees
                green_belt_density = (total_trees / data['totalArea']) * 10000 if data['totalArea'] > 0 else 0
                trees_per_capita = total_trees / data['head_count'] if data['head_count'] > 0 else 0
                results.append({
                    'year': entry_year,
                    'carbon_offset': carbon_offset,
                    'green_belt_density': green_belt_density,
                    'trees_per_capita': trees_per_capita,
                })

            # Sort results by year
            results.sort(key=lambda x: x['year'])
            results = results[:5]  # Limit to 5 most recent years

            # Prepare chart data in the requested structure
            offset_year_data = [{"year": r['year'], "carbon_offset": r['carbon_offset']} for r in results]
            green_belt_density_data = [{"year": r['year'], "green_belt_density": r['green_belt_density']} for r in results]
            trees_per_capita_data = [{"year": r['year'], "trees_per_capita": r['trees_per_capita']} for r in results]

            # Prepare metrics for the current year
            total_trees, green_belt_density, trees_per_capita, new_trees_planted = self.calculate_metrics(all_years_data.filter(**filters))
            carbon_offset = self.calculate_co2(all_years_data.filter(**filters))
            biomass = self.calculate_biomass(all_years_data.filter(**filters))
            co2_sequestration_rate = self.calculate_co2_sequestration_rate(all_years_data)

            # Response structure
            response_data = {
                "facility_id": facility_id,
                "year": year,
                "current_year_metrics": {
                    "total_trees": total_trees,
                    "carbon_offset": carbon_offset,
                    "green_belt_density": green_belt_density,
                    "trees_per_capita": trees_per_capita,
                    "new_trees_planted": new_trees_planted,
                    "biomass": biomass,
                    "co2_sequestration_rate": co2_sequestration_rate,
                },
                "Offset_year": offset_year_data,
                "Green_Belt_Density": green_belt_density_data,
                "Trees_Per_Capita": trees_per_capita_data,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_fiscal_year(self, date):
        """Returns the fiscal year based on a given date."""
        if date.month >= 4:
            return date.year
        return date.year - 1

    def calculate_co2(self, data):
        return sum(
            0.00006 *
            (entry['width'] or 0) ** 2 *
            (entry['height'] or 0) *
            (entry['no_trees'] or 0)
            for entry in data.values('width', 'height', 'no_trees')
        )

    def calculate_biomass(self, data):
        return sum(
            0.0998 *
            (entry['width'] or 0) ** 2 *
            (entry['height'] or 0)
            for entry in data.values('width', 'height')
        )

    def calculate_metrics(self, data):
        aggregated = data.aggregate(
            total_trees=Sum('no_trees'),
            total_area=Sum('totalArea'),
            head_count=Sum('head_count'),
            new_trees_planted=Sum('new_trees_planted')
        )
        total_trees = aggregated.get('total_trees', 0)
        total_area = aggregated.get('total_area', 0)
        head_count = aggregated.get('head_count', 0)
        new_trees_planted = aggregated.get('new_trees_planted', 0)

        green_belt_density = (total_trees / total_area) * 10000 if total_area > 0 else 0
        trees_per_capita = total_trees / head_count if head_count > 0 else 0

        return total_trees, green_belt_density, trees_per_capita, new_trees_planted

    def calculate_co2_sequestration_rate(self, all_years_data):
        # Get the latest fiscal year
        latest_year = self.get_fiscal_year(datetime.now())
        current_year_data = all_years_data.filter(DatePicker__year=latest_year)
        prev_year_data = all_years_data.filter(DatePicker__year=latest_year - 1)

        current_year_co2 = self.calculate_co2(current_year_data)
        prev_year_co2 = self.calculate_co2(prev_year_data) if prev_year_data.exists() else 0

        return current_year_co2 - prev_year_co2

'''Biodiversity Overview Cards Ends'''

'''LOgistices overview Graphs starts'''

# class LogisticesOverviewAndGraphs(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         user = request.user
#         facility_id = request.GET.get('facility_id', 'all')
#         year = request.GET.get('year')

#         try:
#             # Determine the fiscal year if no year is specified
#             if not year:
#                 # Get the latest date from the Logistices model for the user
#                 latest_date = Logistices.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                
#                 if latest_date:
#                     # Determine the fiscal year for the latest available date
#                     year = latest_date.year if latest_date.month >= 4 else latest_date.year - 1
#                 else:
#                     # Default to the current year if no data is available
#                     year = datetime.now().year
#             else:
#                 year = int(year)

#             # Define fiscal year ranges
#             start_date = datetime(year, 4, 1)
#             end_date = datetime(year + 1, 3, 31)

#             # Filters
#             filters = {'user': user, 'DatePicker__range': (start_date, end_date)}
#             if facility_id != 'all':
#                 filters['facility__facility_id'] = facility_id

#             # Query data for the current fiscal year
#             current_year_data = Logistices.objects.filter(**filters)

#             # If no data exists, set all fields to 0
#             if not current_year_data.exists():
#                 return Response({
#                     "year": year,
#                     "facility_id": facility_id,
#                     "logistices_totals": {
#                         "total_vehicles": 0,
#                         "total_trips": 0,
#                         "total_km_travelled": 0.0,
#                         "total_fuel_consumed": 0.0
#                     },
#                     "bar_chart_data": [
#                         {"month": datetime(1900, month, 1).strftime('%b'), "Co2": 0.0}
#                         for month in list(range(4, 13)) + list(range(1, 4))
#                     ],
#                     "donut_chart_data": [{"facility_name": "No Facility", "percentage": 0}],
#                     "logistices_fuel_comparison": {
#                         "cargo": [
#                             {"month": datetime(1900, month, 1).strftime('%b'), "cargo": 0.0}
#                             for month in list(range(4, 13)) + list(range(1, 4))
#                         ],
#                         "staff": [
#                             {"month": datetime(1900, month, 1).strftime('%b'), "staff": 0.0}
#                             for month in list(range(4, 13)) + list(range(1, 4))
#                         ]
#                     }
#                 }, status=200)

#             # Aggregating totals for the overview
#             total_vehicles = current_year_data.aggregate(
#                 total_vehicles=Coalesce(Sum('No_Vehicles'), Value(0))
#             )['total_vehicles']

#             total_trips = current_year_data.aggregate(
#                 total_trips=Coalesce(Sum('No_Trips'), Value(0))
#             )['total_trips']

#             total_km_travelled = current_year_data.aggregate(
#                 total_km_travelled=Coalesce(Sum('km_travelled'), Value(0.0))
#             )['total_km_travelled']

#             total_fuel_consumed = current_year_data.aggregate(
#                 total_fuel_consumed=Coalesce(Sum('fuel_consumption'), Value(0.0))
#             )['total_fuel_consumed']

#             # Monthly Fuel Consumption
#             monthly_data = current_year_data.annotate(month=ExtractMonth('DatePicker')).values('month').annotate(
#                 total_fuel=Coalesce(Sum('fuel_consumption', output_field=FloatField()), Value(0.0, output_field=FloatField()))
#             )
#             monthly_fuel = {d['month']: d['total_fuel'] for d in monthly_data}

#             # Facility-wise Fuel Consumption
#             facility_data = current_year_data.values('facility__facility_name').annotate(
#                 total_fuel=Coalesce(Sum('fuel_consumption', output_field=FloatField()), Value(0.0, output_field=FloatField()))
#             )

#             # Calculate percentages for the donut chart
#             total_fuel = sum(d['total_fuel'] for d in facility_data) or 1  # Avoid division by zero
#             donut_chart_data = [
#                 {"facility_name": d['facility__facility_name'], "percentage": round((d['total_fuel'] / total_fuel) * 100, 2)}
#                 for d in facility_data
#             ]
#             if not donut_chart_data:
#                 donut_chart_data = [{"facility_name": "No Facility", "percentage": 0}]

#             # Logistices Types Fuel Consumption
#             type_month_data = current_year_data.annotate(month=ExtractMonth('DatePicker')).values(
#                 'month', 'logistices_types'
#             ).annotate(
#                 total_fuel=Coalesce(Sum('fuel_consumption', output_field=FloatField()), Value(0.0, output_field=FloatField()))
#             )

#             # Define the month order from April to March
#             month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]

#             # Fill missing months with zeros for graphs
#             all_months = range(1, 13)
#             monthly_fuel = {month: monthly_fuel.get(month, 0.0) for month in all_months}
#             cargo_data = {month: 0.0 for month in all_months}  # Initialize to 0 for each month
#             staff_data = {month: 0.0 for month in all_months}  # Initialize to 0 for each month

#             # Process logistices types data and update cargo and staff data
#             for data in type_month_data:
#                 month = data['month']
#                 logistices_type = data['logistices_types']  # Ensure this matches the correct field names
#                 fuel_consumed = data['total_fuel']

#                 if logistices_type == 'Cargo':  # Ensure 'cargo' matches the correct string in the data
#                     cargo_data[month] = fuel_consumed
#                 elif logistices_type == 'Staff':  # Ensure 'staff_logistices' matches the correct string in the data
#                     staff_data[month] = fuel_consumed

#             # Prepare the data for the line chart
#             bar_chart_data = [
#                 {"month": datetime(1900, month, 1).strftime('%b'), "Fuel_Consumption": monthly_fuel[month]}
#                 for month in month_order
#             ]

#             # Prepare the data for comparing logistices types
#             cargo_data_with_names = [
#                 {"month": datetime(1900, month, 1).strftime('%b'), "cargo": cargo_data[month]}
#                 for month in month_order
#             ]
#             staff_data_with_names = [
#                 {"month": datetime(1900, month, 1).strftime('%b'), "staff": staff_data[month]}
#                 for month in month_order
#             ]

#             # Structure the final response
#             data = {
#                 "year": year,
#                 "facility_id": facility_id,
#                 "logistices_totals": {
#                     "total_vehicles": total_vehicles,
#                     "total_trips": total_trips,
#                     "total_km_travelled": total_km_travelled,
#                     "total_fuel_consumed": total_fuel_consumed
#                 },
#                 "bar_chart_data": bar_chart_data,  # Line Chart
#                 "donut_chart_data": donut_chart_data,  # Donut Chart
#                 "logistices_fuel_comparison": {  # Bar Graph (Fuel Consumption by Logistices Type)
#                     "cargo": cargo_data_with_names,
#                     "staff": staff_data_with_names
#                 }
#             }

#             return Response(data, status=200)

#         except ValueError:
#             return Response({"error": "Invalid year format."}, status=400)

#         except Exception as e:
#             return Response({"error": str(e)}, status=500)

class LogisticesOverviewAndGraphs(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', 'all')
        facility_location = request.GET.get('facility_location', 'all')
        year = request.GET.get('year')

        try:
            # Base filters
            filters = {'user': user}

            # Validate and apply facility_id filter
            if facility_id and facility_id.lower() != 'all':
                if not Facility.objects.filter(facility_id=facility_id, user=user).exists():
                    return Response(
                        {'error': 'Invalid facility ID or not associated with the logged-in user.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                filters['facility__facility_id'] = facility_id

            # Validate and apply facility_location filter
            if facility_location and facility_location.lower() != 'all':
                if not Facility.objects.filter(location__icontains=facility_location).exists():
                    return Response(
                        {'error': f'No facility found with location {facility_location}.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                filters['facility__location__icontains'] = facility_location

            # Validate or determine the fiscal year
            if year:
                try:
                    year = int(year)
                    if year < 1900 or year > datetime.now().year + 10:
                        return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)
                except ValueError:
                    return Response({'error': 'Year must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Determine the latest year across all models
                latest_dates = [
                    Water.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date'],
                    Waste.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date'],
                    Energy.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date'],
                    Biodiversity.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date'],
                    Logistices.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                ]
                latest_date = max(filter(None, latest_dates), default=None)

                if latest_date:
                    year = latest_date.year if latest_date.month >= 4 else latest_date.year - 1
                else:
                    # Default to the current fiscal year if no data exists
                    today = datetime.now()
                    year = today.year - 1 if today.month < 4 else today.year

            # Define fiscal year range
            start_date = datetime(year, 4, 1)
            end_date = datetime(year + 1, 3, 31)
            filters['DatePicker__range'] = (start_date, end_date)

            # Query data for the current fiscal year
            current_year_data = Logistices.objects.filter(**filters)

            # Handle case when no data exists
            if not current_year_data.exists():
                return Response({
                    "year": year,
                    "facility_id": facility_id,
                    "logistices_totals": {
                        "total_vehicles": 0,
                        "total_trips": 0,
                        "total_km_travelled": 0.0,
                        "total_fuel_consumed": 0.0
                    },
                    "bar_chart_data": [
                        {"month": datetime(1900, month, 1).strftime('%b'), "Fuel_Consumption": 0.0}
                        for month in list(range(4, 13)) + list(range(1, 4))
                    ],
                    "donut_chart_data": [{"facility_name": "No Facility", "percentage": 0}],
                    "logistices_fuel_comparison": {
                        "cargo": [
                            {"month": datetime(1900, month, 1).strftime('%b'), "cargo": 0.0}
                            for month in list(range(4, 13)) + list(range(1, 4))
                        ],
                        "staff": [
                            {"month": datetime(1900, month, 1).strftime('%b'), "staff": 0.0}
                            for month in list(range(4, 13)) + list(range(1, 4))
                        ]
                    }
                }, status=200)

            # Aggregating totals for the overview
            total_vehicles = current_year_data.aggregate(
                total_vehicles=Coalesce(Sum('No_Vehicles'), Value(0))
            )['total_vehicles']

            total_trips = current_year_data.aggregate(
                total_trips=Coalesce(Sum('No_Trips'), Value(0))
            )['total_trips']

            total_km_travelled = current_year_data.aggregate(
                total_km_travelled=Coalesce(Sum('km_travelled'), Value(0.0))
            )['total_km_travelled']

            total_fuel_consumed = current_year_data.aggregate(
                total_fuel_consumed=Coalesce(Sum('fuel_consumption'), Value(0.0))
            )['total_fuel_consumed']

            # Monthly Fuel Consumption
            monthly_data = current_year_data.annotate(month=ExtractMonth('DatePicker')).values('month').annotate(
                total_fuel=Coalesce(Sum('fuel_consumption', output_field=FloatField()), Value(0.0, output_field=FloatField()))
            )
            monthly_fuel = {d['month']: d['total_fuel'] for d in monthly_data}

            # Facility-wise Fuel Consumption
            facility_data = current_year_data.values('facility__facility_name').annotate(
                total_fuel=Coalesce(Sum('fuel_consumption', output_field=FloatField()), Value(0.0, output_field=FloatField()))
            )

            # Calculate percentages for the donut chart
            total_fuel = sum(d['total_fuel'] for d in facility_data) or 1  # Avoid division by zero
            donut_chart_data = [
                {"facility_name": d['facility__facility_name'], "percentage": round((d['total_fuel'] / total_fuel) * 100, 2)}
                for d in facility_data
            ]

            # Logistices Types Fuel Consumption
            type_month_data = current_year_data.annotate(month=ExtractMonth('DatePicker')).values(
                'month', 'logistices_types'
            ).annotate(
                total_fuel=Coalesce(Sum('fuel_consumption', output_field=FloatField()), Value(0.0, output_field=FloatField()))
            )

            # Define the month order from April to March
            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]

            # Fill missing months with zeros for graphs
            all_months = range(1, 13)
            monthly_fuel = {month: monthly_fuel.get(month, 0.0) for month in all_months}
            cargo_data = {month: 0.0 for month in all_months}
            staff_data = {month: 0.0 for month in all_months}

            # Process logistices types data and update cargo and staff data
            for data in type_month_data:
                month = data['month']
                logistices_type = data['logistices_types']
                fuel_consumed = data['total_fuel']

                if logistices_type == 'Cargo':
                    cargo_data[month] = fuel_consumed
                elif logistices_type == 'Staff':
                    staff_data[month] = fuel_consumed

            # Prepare the data for the line chart
            bar_chart_data = [
                {"month": datetime(1900, month, 1).strftime('%b'), "Fuel_Consumption": monthly_fuel[month]}
                for month in month_order
            ]

            # Prepare the data for comparing logistices types
            cargo_data_with_names = [
                {"month": datetime(1900, month, 1).strftime('%b'), "cargo": cargo_data[month]}
                for month in month_order
            ]
            staff_data_with_names = [
                {"month": datetime(1900, month, 1).strftime('%b'), "staff": staff_data[month]}
                for month in month_order
            ]

            # Structure the final response
            data = {
                "year": year,
                "facility_id": facility_id,
                "logistices_totals": {
                    "total_vehicles": total_vehicles,
                    "total_trips": total_trips,
                    "total_km_travelled": total_km_travelled,
                    "total_fuel_consumed": total_fuel_consumed
                },
                "bar_chart_data": bar_chart_data,
                "donut_chart_data": donut_chart_data,
                "logistices_fuel_comparison": {
                    "cargo": cargo_data_with_names,
                    "staff": staff_data_with_names
                }
            }

            return Response(data, status=200)

        except ValueError:
            return Response({"error": "Invalid year format."}, status=400)

        except Exception as e:
            return Response({"error": str(e)}, status=500)

'''LOgistices overview Graphs ends'''
# '''Emissions Calculations starts'''
# class EmissionCalculations(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         user = request.user
#         year = request.GET.get('year', None)
#         facility_id = request.GET.get('facility_id', 'all')
#         facility_location = request.GET.get('facility_location', None)

#         try:
#             filters = {'user': user}
#             today = datetime.now()

#             # Year calculation
#             if year:
#                 try:
#                     year = int(year)
#                 except ValueError:
#                     return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)
#             else:
#                 # Get latest dates from all relevant models
#                 latest_energy_date = Energy.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
#                 latest_water_date = Water.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
#                 latest_waste_date = Waste.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
#                 latest_logistices_date = Logistices.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']

#                 # If there are no records, default to current year
#                 latest_dates = [latest_energy_date, latest_water_date, latest_waste_date, latest_logistices_date]
#                 latest_date = max(filter(None, latest_dates), default=None)

#                 if latest_date:
#                     # Get the fiscal year from the latest available date
#                     year = latest_date.year if latest_date.month >= 4 else latest_date.year - 1
#                 else:
#                     # If no data exists, default to the current fiscal year
#                     year = today.year if today.month >= 4 else today.year - 1

#             # Fiscal year range
#             start_date, end_date = (
#                 (datetime(year, 4, 1), datetime(year + 1, 3, 31))
#                 if today.month >= 4
#                 else (datetime(year - 1, 4, 1), datetime(year, 3, 31))
#             )
#             filters['DatePicker__range'] = (start_date, end_date)

#             # Facility ID filtering
#             if facility_id.lower() != 'all':
#                 if not Facility.objects.filter(facility_id=facility_id).exists():
#                     return Response({'error': f'Facility with ID {facility_id} does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
#                 filters['facility__facility_id'] = facility_id

#             # Facility location filtering
#             if facility_location and facility_location.lower() != 'all':
#                 if not Facility.objects.filter(facility_location__icontains=facility_location).exists():
#                     return Response({'error': f'No facility found with location {facility_location}.'}, status=status.HTTP_400_BAD_REQUEST)
#                 filters['facility__facility_location__icontains'] = facility_location

#             # Fetch energy, water, waste, and logistices data
#             energy_data = Energy.objects.filter(**filters)
#             water_data = Water.objects.filter(**filters)
#             waste_data = Waste.objects.filter(**filters)
#             logistices_data = Logistices.objects.filter(**filters)

#             # Check if data exists, if not set all emissions to zero
#             if not any([energy_data, water_data, waste_data, logistices_data]):
#                 return Response({
#                     'year': year,
#                     'line_chart_data': [
#                         {"month": datetime(1900, month, 1).strftime('%b'), "total_emissions": 0}
#                         for month in list(range(4, 13)) + list(range(1, 4))
#                     ]
#                 }, status=status.HTTP_200_OK)

#             # Energy Emission factors
#             electricity_factor = 0.82
#             fuel_factors = {
#                 'coking_coal': 2.66,
#                 'coke_oven_coal': 3.1,
#                 'natural_gas': 2.7,
#                 'diesel': 2.91 * 1000,  # Diesel in liters, convert to kg
#                 'biomass_wood': 1.75,
#                 'biomass_other_solid': 1.16
#             }
#             petrol_factor = 2.29 * 1000
#             diesel_factor = 2.91 * 1000

#             # Monthly totals (ordered by fiscal year: April - March)
#             month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
#             monthly_total_emissions = {}

#             for month in month_order:  # Loop over fiscal months
#                 # Filter data for the specific month
#                 monthly_energy = energy_data.filter(DatePicker__month=month)
#                 monthly_water = water_data.filter(DatePicker__month=month)
#                 monthly_waste = waste_data.filter(DatePicker__month=month)
#                 monthly_logistices = logistices_data.filter(DatePicker__month=month)

#                 # Calculate electricity emissions
#                 hvac_sum = monthly_energy.aggregate(total=Coalesce(Sum('hvac'), 0.0))['total'] or 0
#                 production_sum = monthly_energy.aggregate(total=Coalesce(Sum('production'), 0.0))['total'] or 0
#                 stp_sum = monthly_energy.aggregate(total=Coalesce(Sum('stp'), 0.0))['total'] or 0
#                 admin_block_sum = monthly_energy.aggregate(total=Coalesce(Sum('admin_block'), 0.0))['total'] or 0
#                 utilities_sum = monthly_energy.aggregate(total=Coalesce(Sum('utilities'), 0.0))['total'] or 0
#                 others_sum = monthly_energy.aggregate(total=Coalesce(Sum('others'), 0.0))['total'] or 0

#                 electricity_emissions = (
#                     hvac_sum + production_sum + stp_sum + admin_block_sum + utilities_sum + others_sum
#                 ) * electricity_factor

#                 # Calculate fuel emissions
#                 fuel_emissions = sum([ 
#                     (monthly_energy.aggregate(total=Coalesce(Sum('coking_coal'), 0.0))['total'] or 0) * fuel_factors['coking_coal'],
#                     (monthly_energy.aggregate(total=Coalesce(Sum('coke_oven_coal'), 0.0))['total'] or 0) * fuel_factors['coke_oven_coal'],
#                     (monthly_energy.aggregate(total=Coalesce(Sum('natural_gas'), 0.0))['total'] or 0) * fuel_factors['natural_gas'],
#                     (monthly_energy.aggregate(total=Coalesce(Sum('diesel'), 0.0))['total'] or 0) * fuel_factors['diesel'],
#                     (monthly_energy.aggregate(total=Coalesce(Sum('biomass_wood'), 0.0))['total'] or 0) * fuel_factors['biomass_wood'],
#                     (monthly_energy.aggregate(total=Coalesce(Sum('biomass_other_solid'), 0.0))['total'] or 0) * fuel_factors['biomass_other_solid']
#                 ])
#                 total_energy_emissions = electricity_emissions + fuel_emissions

#                 # Calculate water usage Emissions
#                 total_water = monthly_water.aggregate(
#                     total=Coalesce(Sum('Generated_Water'), 0.0)
#                     + Coalesce(Sum('Recycled_Water'), 0.0)
#                     + Coalesce(Sum('Softener_usage'), 0.0)
#                     + Coalesce(Sum('Boiler_usage'), 0.0)
#                     + Coalesce(Sum('otherUsage'), 0.0)
#                 )['total']
                
#                 total_water_emissions = total_water * 0.46
                
#                 # Calculate waste emissions
#                 total_waste_emissions = sum([
#                     (monthly_waste.aggregate(total=Coalesce(Sum('Landfill_waste'), 0.0))['total'] or 0) * 300,
#                     (monthly_waste.aggregate(total=Coalesce(Sum('Recycle_waste'), 0.0))['total'] or 0) * 10
#                 ])
                
#                 # Calculate Logistices emissions
#                 total_logistices_emissions = sum([
#                     (monthly_logistices.filter(Typeof_fuel='diesel').aggregate(
#                         total=Coalesce(Sum('fuel_consumption'), 0.0))['total'] or 0) * diesel_factor,
#                     (monthly_logistices.filter(Typeof_fuel='petrol').aggregate(
#                         total=Coalesce(Sum('fuel_consumption'), 0.0))['total'] or 0) * petrol_factor
#                 ])
                
#                 # Total emissions (energy + water + waste + logistices)
#                 total_emissions = total_energy_emissions + total_water_emissions + total_waste_emissions + total_logistices_emissions
                
#                 # Store monthly emissions data
#                 monthly_total_emissions[month] = total_emissions

#             # Prepare the response data for line chart
#             line_chart_data = []
#             for month in month_order:
#                 month_name = datetime(1900, month, 1).strftime('%b')  # Get month name
#                 line_chart_data.append({
#                     "month": month_name,
#                     "total_emissions": monthly_total_emissions.get(month, 0)
#                 })

#             response_data = {
#                 'year': year,
#                 'line_chart_data': line_chart_data
#             }

#             return Response(response_data, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class EmissionCalculations(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        year = request.GET.get('year', None)
        facility_id = request.GET.get('facility_id', 'all')
        facility_location = request.GET.get('facility_location', None)

        try:
            filters = {'user': user}
            today = datetime.now()

            # Facility ID filtering
            if facility_id and facility_id.lower() != 'all':
                if not Facility.objects.filter(facility_id=facility_id, user=user).exists():
                    return Response(
                        {'error': 'Invalid facility ID or not associated with the logged-in user.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                filters['facility__facility_id'] = facility_id

            # Facility location filtering
            if facility_location and facility_location.lower() != 'all':
                if not Facility.objects.filter(location__icontains=facility_location).exists():
                    return Response(
                        {'error': f'No facility found with location {facility_location}.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                filters['facility__location__icontains'] = facility_location

            # Year filtering
            if year:
                try:
                    year = int(year)
                    if year < 1900 or year > datetime.now().year + 10:
                        return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)
                except ValueError:
                    return Response({'error': 'Year must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Find the latest year across all models (Water, Waste, etc.)
                latest_water_date = Water.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_waste_date = Waste.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_energy_date = Energy.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_biodiversity_date = Biodiversity.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_logistices_date = Logistices.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']

                latest_date = max(
                    filter(None, [latest_water_date, latest_waste_date, latest_energy_date, latest_biodiversity_date, latest_logistices_date]),
                    default=None
                )
                if latest_date:
                    year = latest_date.year if latest_date.month >= 4 else latest_date.year - 1
                else:
                    # Default to the current fiscal year if no data exists
                    year = today.year - 1 if today.month < 4 else today.year

            # Determine fiscal year range
            start_date = datetime(year, 4, 1)
            end_date = datetime(year + 1, 3, 31)
            filters['DatePicker__range'] = (start_date, end_date)

            # Fetch energy, water, waste, and logistices data
            energy_data = Energy.objects.filter(**filters)
            water_data = Water.objects.filter(**filters)
            waste_data = Waste.objects.filter(**filters)
            logistices_data = Logistices.objects.filter(**filters)

            # Check if data exists, if not set all emissions to zero
            if not any([energy_data, water_data, waste_data, logistices_data]):
                return Response({
                    'year': year,
                    'line_chart_data': [
                        {"month": datetime(1900, month, 1).strftime('%b'), "total_emissions": 0}
                        for month in list(range(4, 13)) + list(range(1, 4))
                    ]
                }, status=status.HTTP_200_OK)

            # Energy Emission factors
            electricity_factor = 0.82
            fuel_factors = {
                'coking_coal': 2.66,
                'coke_oven_coal': 3.1,
                'natural_gas': 2.7,
                'diesel': 2.91 * 1000,  # Diesel in liters, convert to kg
                'biomass_wood': 1.75,
                'biomass_other_solid': 1.16
            }
            petrol_factor = 2.29 * 1000
            diesel_factor = 2.91 * 1000

            # Monthly totals (ordered by fiscal year: April - March)
            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            monthly_total_emissions = {}

            for month in month_order:  # Loop over fiscal months
                # Filter data for the specific month
                monthly_energy = energy_data.filter(DatePicker__month=month)
                monthly_water = water_data.filter(DatePicker__month=month)
                monthly_waste = waste_data.filter(DatePicker__month=month)
                monthly_logistices = logistices_data.filter(DatePicker__month=month)

                # Calculate electricity emissions
                electricity_emissions = (
                    sum([
                        monthly_energy.aggregate(total=Coalesce(Sum(field), 0.0))['total'] or 0
                        for field in ['hvac', 'production', 'stp', 'admin_block', 'utilities', 'others']
                    ]) * electricity_factor
                )

                # Calculate fuel emissions
                fuel_emissions = sum([
                    (monthly_energy.aggregate(total=Coalesce(Sum(fuel), 0.0))['total'] or 0) * factor
                    for fuel, factor in fuel_factors.items()
                ])
                total_energy_emissions = electricity_emissions + fuel_emissions

                # Calculate water usage emissions
                total_water = sum([
                    monthly_water.aggregate(total=Coalesce(Sum(field), 0.0))['total'] or 0
                    for field in ['Generated_Water', 'Recycled_Water', 'Softener_usage', 'Boiler_usage', 'otherUsage']
                ])
                total_water_emissions = total_water * 0.46

                # Calculate waste emissions
                total_waste_emissions = sum([
                    (monthly_waste.aggregate(total=Coalesce(Sum(field), 0.0))['total'] or 0) * factor
                    for field, factor in [('Landfill_waste', 300), ('Recycle_waste', 10)]
                ])

                # Calculate logistices emissions
                total_logistices_emissions = sum([
                    (monthly_logistices.filter(Typeof_fuel=fuel_type).aggregate(
                        total=Coalesce(Sum('fuel_consumption'), 0.0))['total'] or 0) * factor
                    for fuel_type, factor in [('diesel', diesel_factor), ('petrol', petrol_factor)]
                ])

                # Total emissions
                total_emissions = total_energy_emissions + total_water_emissions + total_waste_emissions + total_logistices_emissions

                # Store monthly emissions data
                monthly_total_emissions[month] = total_emissions

            # Prepare the response data for line chart
            line_chart_data = []
            for month in month_order:
                month_name = datetime(1900, month, 1).strftime('%b')  # Get month name
                line_chart_data.append({
                    "month": month_name,
                    "total_emissions": monthly_total_emissions.get(month, 0)
                })

            response_data = {
                'year': year,
                'line_chart_data': line_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
# '''Emissions Calculations starts'''

'''YearFilter Starts'''
class YearFacilityDataAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            facility_id = request.query_params.get('facility_id', 'all')

            # Validate facility
            if facility_id != 'all' and not Facility.objects.filter(facility_id=facility_id, user=user).exists():
                return Response(
                    {'error': 'Invalid facility ID or not associated with the logged-in user.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Map categories to models (but we will only be interested in the fiscal years)
            model_serializer_map = {
                'waste': Waste,
                'energy': Energy,
                'water': Water,
                'biodiversity': Biodiversity,
                'logistics': Logistices,
            }

            # Fetch fiscal years from all categories (models)
            fiscal_years_set = set()
            for model in model_serializer_map.values():
                queryset = model.objects.filter(user=user)
                if facility_id != 'all':
                    queryset = queryset.filter(facility__facility_id=facility_id)

                # Map each record's year to the fiscal year
                for record in queryset.values('DatePicker'):
                    record_date = record['DatePicker']
                    if record_date:
                        record_year = record_date.year
                        record_month = record_date.month
                        
                        # Adjust year based on fiscal year (April to March)
                        fiscal_year = record_year if record_month >= 4 else record_year - 1
                        fiscal_years_set.add(fiscal_year)

            # If no fiscal years found, default to 0
            if not fiscal_years_set:
                years_list = [{"year": 0}]
            else:
                # Convert set to list and sort the fiscal years
                years_list = [{"year": year} for year in sorted(list(fiscal_years_set), reverse=True)]

            return Response({
                "facility_id": facility_id,
                "available_years": years_list
            }, status=status.HTTP_200_OK)

        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            print(error_message)  # For debugging purposes, consider using a logger in production
            return Response({'error': error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

'''YearFilter Ends'''

