
from django.urls import   path
from .views import RegisterView, LoginView, DashboardView, LogoutView,WasteCreateView,WasteView,WasteEditView,WasteDeleteView,EnergyCreateView,EnergyView,EnergyEditView,EnergyDeleteView,WaterView,WaterCreateView,WaterEditView,WaterDeleteView,BiodiversityCreateView,BiodiversityView,BiodiversityEditView,BiodiversityDeleteView,FacilityCreateView,FacilityView,FacilityEditView,FacilityDeleteView,LogisticesCreateView,LogisticesView,LogisticesEditView,LogisticesDeleteView,FoodWasteOverviewView,SolidWasteOverviewView,E_WasteOverviewView,Biomedical_WasteOverviewView,Liquid_DischargeOverviewView,OthersOverviewView,Waste_Sent_For_RecycleOverviewView,Waste_Sent_For_LandFillOverviewView,StackedWasteOverviewView,WasteOverallDonutChartView,SentToLandfillOverviewView,SentToRecycledOverviewView,HVACOverviewView,ProductionOverviewView,StpOverviewView,Admin_BlockOverviewView,Utilities_OverviewView,WasteViewCard_Over,EnergyViewCard_Over,Others_OverviewView,Renewable_EnergyOverView,StackedEnergyOverviewView,OverallUsageView,Fuel_Used_OperationsOverView,WaterViewCard_Over,Generated_WaterOverviewView,Recycle_WaterOverviewView,Softener_usageOverviewView,Boiler_usageOverviewView,otherUsage_OverviewView,StackedWaterOverviewView,EnergyAnalyticsView,WaterAnalyticsView,BiodiversityMetricsGraphsView,LogisticesOverviewAndGraphs,EmissionCalculations,YearFacilityDataAPIView,OrganizationCreate,OrganizationView


from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
urlpatterns = [
   
   #JWT-Token Refresh Starts
   path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
   path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
   #JWT-Token Refresh Ends
   
   #Apis for Registration and Login  starts
   path('register/', RegisterView.as_view(), name='register'),
   path('login/', LoginView.as_view(), name='login'),
   path('dashboard/', DashboardView.as_view(), name='dashboard'),
   path('logout/', LogoutView.as_view(), name='logout'),
   #Apis for Registration and Login Ends
    
    #Apis For Organization_Registration Starts
   path('Organization_Create/',OrganizationCreate.as_view(),name='Organization_Create'),
   path('Organization_view/',OrganizationView.as_view(),name='Organization_view'),
   #Apis For Organization_Registration Ends
    
   #Apis for Facility Crud Operations Starts
   path('add_facility/',FacilityCreateView.as_view(),name='add_facility'),
   path('view_facility/',FacilityView.as_view(),name='view_facility'),
   path('update_facility/<str:facility_id>/',FacilityEditView.as_view(),name='update_facility'),
   path('delete_facility/<str:facility_id>/',FacilityDeleteView.as_view(),name='delete_facility'),
   #Apis for Facility Crud Operations Ends
     
   #Apis for Waste Crud Operations starts
   path('add_waste/', WasteCreateView.as_view(), name='add_waste'),
   path('view_waste/',WasteView.as_view(),name='view_waste'),
   path('waste_update/<str:waste_id>/', WasteEditView.as_view(), name='waste_update'),
   path('waste_delete/<str:waste_id>/', WasteDeleteView.as_view(), name='waste_delete'),
   #Apis for Waste Crud Operations Ends
   
   #Apis for Energy Crud Operations starts
   path('add_energy/',EnergyCreateView.as_view(),name='add_energy'),
   path('view_energy/',EnergyView.as_view(),name="view_energy"),
   path('energy_update/<str:energy_id>/', EnergyEditView.as_view(), name='energy_update'),
   path('energy_delete/<str:energy_id>/', EnergyDeleteView.as_view(), name='energy_delete'),
   #Apis for Energy Crud Operations Ends
    
   #Apis for Water Crud Operations starts
   path('add_water/',WaterCreateView.as_view(),name='add_water'),
   path('view_water/',WaterView.as_view(),name='View_water'),
   path('water_update/<str:water_id>/', WaterEditView.as_view(), name='water_update'),
   path('water_delete/<str:water_id>/', WaterDeleteView.as_view(), name='water_delete'),
   #Apis for Water Crud Operations Ends
     
   #Apis for Biodiversity Crud Operations starts
   path('add_biodiversity/',BiodiversityCreateView.as_view(),name='add_biodiversity'),
   path('view_biodiversity/',BiodiversityView.as_view(),name='view_biodiversity'),
   path('biodiversity_update/<str:biodiversity_id>/', BiodiversityEditView.as_view(), name='biodiversity_update'),
   path('biodiversity_delete/<str:biodiversity_id>/', BiodiversityDeleteView.as_view(), name='biodiversity_delete'),
   #Apis for Biodiversity Crud Operations Ends
    
   #Apis for Logistices Crud Operations starts
   path('add_logistices/',LogisticesCreateView.as_view(),name='add_logistices'),
   path('view_logistices/',LogisticesView.as_view(),name='add_logistices'),
   path('update_logistices/<str:logistices_id>/',LogisticesEditView.as_view(),name='add_logistices'),
   path('delete_logistices/<str:logistices_id>/',LogisticesDeleteView.as_view(),name='add_logistices'),
   #Apis for Logistices Crud Operations Ends
   
   #OverviewCard Total
   path('OverallUsageView/',OverallUsageView.as_view(),name='OverallUsageView'),
   
   #Apis for Waste overviewgraphs starts
   #Waste Overview
   path('WasteViewCard_Over/',WasteViewCard_Over.as_view(),name='WasteViewCard_Over'),
   path('FoodWasteOverviewView/',FoodWasteOverviewView.as_view(),name="FoodWasteOverview"),
   path('SolidWasteOverviewView/',SolidWasteOverviewView.as_view(),name="SolidWasteOverviewView"),
   path('E_WasteOverviewView/',E_WasteOverviewView.as_view(),name="E_WasteOverviewView"),
   path('Biomedical_WasteOverviewView/',Biomedical_WasteOverviewView.as_view(),name="Biomedical_WasteOverviewView"),
   path('Liquid_DischargeOverviewView/',Liquid_DischargeOverviewView.as_view(),name="Liquid_DischargeOverviewView"),
   path('OthersOverviewView/',OthersOverviewView.as_view(),name='OthersOverviewView'),
   path('Waste_Sent_For_RecycleOverviewView/',Waste_Sent_For_RecycleOverviewView.as_view(),name='Waste_Sent_For_RecycleOverviewView'),
   path('Waste_Sent_For_LandFillOverviewView/',Waste_Sent_For_LandFillOverviewView.as_view(),name='Waste_Sent_For_LandFillOverviewView'),
  
   
   #Apis For Stacked Graph,donuts Graphs Overview
   path('StackedWasteOverviewView/',StackedWasteOverviewView.as_view(),name='StackedWasteOverviewView'),
   path('WasteOverallDonutChartView/',WasteOverallDonutChartView.as_view(),name='WasteOverallDonutChartView'),
   path('SentToLandfillOverviewView/',SentToLandfillOverviewView.as_view(),name='Sent_To_Landfill_OverviewView'),
   path('SentToRecycledOverviewView/',SentToRecycledOverviewView.as_view(),name='SentToRecycledOverviewView'),
   #Apis for Waste overviewgraphs Ends
   

   #Apis For Energy overviewView
   path('EnergyViewCard_Over/',EnergyViewCard_Over.as_view(),name="EnergyViewCard_Over"),
   path('HVACOverviewView/',HVACOverviewView.as_view(),name='HVACOverviewView'),
   path('ProductionOverviewView/',ProductionOverviewView.as_view(),name='ProductionOverviewView'),
   path('StpOverviewView/',StpOverviewView.as_view(),name='StpOverviewView'),
   path('Admin_BlockOverviewView/',Admin_BlockOverviewView.as_view(),name='Admin_BlockOverviewView'),
   path('Utilities_OverviewView/',Utilities_OverviewView.as_view(),name='Utilities_OverviewView'),
   path('Others_OverviewView/',Others_OverviewView.as_view(),name="Others_OverviewView"),
   path('Renewable_EnergyOverView/',Renewable_EnergyOverView.as_view(),name='Renewable_EnergyOverView'),
   path('Fuel_Used_OperationsOverView/',Fuel_Used_OperationsOverView.as_view(),name="Fuel_Used_OperationsOverView"),
   #Apis For Stacked Graph,donuts Graphs Overview
   path('StackedEnergyOverviewView/',StackedEnergyOverviewView.as_view(),name='StackedEnergyOverviewView'),
   path('EnergyAnalyticsView/',EnergyAnalyticsView.as_view(),name="EnergyAnalyticsView"),
   
   
    #Apis for Water Overview
    path('WaterViewCard_Over/',WaterViewCard_Over.as_view(),name="WaterViewCard_Over"),
    path('Generated_WaterOverviewView/',Generated_WaterOverviewView.as_view(),name="Generated_WaterOverviewView"),
    path('Recycle_WaterOverviewView/',Recycle_WaterOverviewView.as_view(),name="Recycle_WaterOverviewView"),
    path('Softener_usageOverviewView/',Softener_usageOverviewView.as_view(),name="Softener_usageOverviewView"),
    path('Boiler_usageOverviewView/',Boiler_usageOverviewView.as_view(),name="Boiler_usageOverviewView"),
    path('otherUsage_OverviewView/',otherUsage_OverviewView.as_view(),name="otherUsage_OverviewView"),
    
    #APis For Stacked Graphs donut Graphs Overview
    path('StackedWaterOverviewView/',StackedWaterOverviewView.as_view(),name="StackedWaterOverviewView"),
    path('WaterAnalyticsView/',WaterAnalyticsView.as_view(),name="WaterAnalyticsView"),
    
    #Apis For Biodiversity Overview
    path('BiodiversityMetricsGraphsView/',BiodiversityMetricsGraphsView.as_view(),name="BiodiversityMetricsGraphsView"),
    #Apis For LogisticesOverviewGraph
    path('LogisticesOverviewAndGraphs/',LogisticesOverviewAndGraphs.as_view(),name="LogisticesOverviewAndGraphs"),
    #Api For Emissions Calculations
    path('EmissionCalculations/',EmissionCalculations.as_view(),name="EmissionCalculations"),
    #Apis For YearFacility
    path('YearFacilityDataAPIView/',YearFacilityDataAPIView.as_view(),name="YearFacilityDataAPIView"),

]
