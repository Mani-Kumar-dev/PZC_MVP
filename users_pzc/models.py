# myapp/models.py
import uuid
from django.db import models
from django.utils import timezone 
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']  # Fields required when creating a superuser

    def __str__(self):
        return self.email

class Org_registration(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    Organization_Name = models.CharField(max_length=255)
    Business_executive_Name = models.CharField(max_length=255)
    Location = models.CharField( max_length=255,null=True,blank=True)
    Branch_ID = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    
    def __str__(self):
        return f"Organization: {self.organization_name} for {self.user.email}"
   

class Facility(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='facilities')
    facility_id = models.CharField(max_length=255, primary_key=True, editable=False)
    facility_name = models.CharField(max_length=255)
    facility_head = models.CharField(max_length=255)
    facility_location = models.CharField(max_length=255)
    facility_description = models.TextField()

    def __str__(self):
        return self.facility_name

    def save(self, *args, **kwargs):
        if not self.facility_id:
            self.facility_id = uuid.uuid4().hex[:8].upper()
        super().save(*args, **kwargs)
    
class Waste(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    waste_id =  models.CharField(max_length=255,primary_key=True, editable=False)
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)
    category = models.CharField(max_length=255)
    DatePicker = models.DateField(null=True,blank=True)
    food_waste = models.FloatField(default=0.0)
    solid_Waste = models.FloatField(default=0.0)
    E_Waste = models.FloatField(default=0.0)
    Biomedical_waste = models.FloatField(default=0.0)
    liquid_discharge = models.FloatField(default=0.0)
    other_waste = models.FloatField(default=0.0)
    Recycle_waste = models.FloatField(default=0.0)
    Landfill_waste = models.FloatField(default=0.0)
    overall_usage = models.FloatField(default=0.0, editable=False)

    def __str__(self):
        return f"Waste data for {self.user.email}"
    
    def save(self, *args, **kwargs):
        if not self.waste_id:
            self.waste_id = uuid.uuid4().hex[:8].upper()
        self.overall_usage = (self.food_waste + self.solid_Waste + self.E_Waste +
                              self.Biomedical_waste + self.other_waste)
        
        super().save(*args, **kwargs)


class Energy(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)
    energy_id =  models.CharField(max_length=255, primary_key=True, editable=False)
    category = models.CharField(max_length=255)
    DatePicker = models.DateField(null=True,blank=True)
    hvac=models.FloatField(default=0.0)
    production = models.FloatField(default=0.0)
    stp = models.FloatField(default=0.0)
    admin_block = models.FloatField(default=0.0)
    utilities = models.FloatField(default=0.0)
    others = models.FloatField(default=0.0)
    coking_coal = models.FloatField(default=0.0)
    coke_oven_coal = models.FloatField(default=0.0)
    natural_gas = models.FloatField(default=0.0)
    diesel = models.FloatField(default=0.0)
    biomass_wood = models.FloatField(default=0.0)
    biomass_other_solid = models.FloatField(default=0.0)
    renewable_solar = models.FloatField(default=0.0)
    renewable_other = models.FloatField(default=0.0)
    overall_usage = models.FloatField(default=0.0, editable=False)
    
    def __str__(self):
        return f"Energy data for {self.user.email}"
    def save(self,*args, **kwargs):
        if not self.energy_id:
            self.energy_id = uuid.uuid4().hex[:8].upper()
        self.overall_usage = (self.hvac + self.production + self.stp + self.admin_block + self.utilities + self.others)
        super(Energy,self).save(*args, **kwargs)

class Water(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)
    category = models.CharField(max_length=255)
    water_id =  models.CharField(max_length=20, unique=True, editable=False)
    DatePicker = models.DateField(null=True,blank=True)
    Generated_Water = models.FloatField(default=0.0)
    Recycled_Water = models.FloatField(default=0.0)
    Softener_usage = models.FloatField(default=0.0)
    Boiler_usage = models.FloatField(default=0.0)
    otherUsage = models.FloatField(default=0.0)
    overall_usage = models.FloatField(default=0.0, editable=False)
    
    def __str__(self):
        return f"Water data for {self.user.email}"
    def save(self, *args, **kwargs):
        if not self.water_id:
            self.water_id = uuid.uuid4().hex[:8].upper()
        self.overall_usage = (self.Generated_Water + self.Recycled_Water + self.Softener_usage + self.Boiler_usage + self.otherUsage)
        super(Water, self).save(*args, **kwargs)
    
class Biodiversity(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)
    category = models.CharField(max_length=255)
    biodiversity_id =  models.CharField(max_length=20, primary_key=True, editable=False)
    DatePicker = models.DateField(null=True,blank=True)
    no_trees=models.IntegerField(default=0)
    species = models.CharField(max_length=255)
    age = models.IntegerField(default=0)
    height = models.FloatField(default=0.0)
    width = models.FloatField(default=0.0)
    totalArea = models.FloatField(default=0.0)
    new_trees_planted = models.FloatField(default=0.0)
    head_count = models.FloatField(default=0.0)
    overall_Trees = models.FloatField(default=0.0, editable=False)

    
    def __str__(self):
        return f"biodiversity data for {self.user.email}"
    
    def save(self,*args, **kwargs):
        if not self.biodiversity_id:
            self.biodiversity_id = uuid.uuid4().hex[:8].upper()
        self.overall_Trees = (self.no_trees)
        super(Biodiversity,self).save(*args, **kwargs)
        
    
class Logistices(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)
    LOGISTICES_TYPE_CHOICES=[
        ('Staff','Staff'),
        ('Cargo','Cargo')
    ]
    FUEL_TYPE_CHOICES=[
        ('Diesel','Diesel'),
        ('Petrol','Petrol')
    ]
    category = models.CharField(max_length=255)
    DatePicker = models.DateField(null=True,blank=True)
    logistices_id =  models.CharField(max_length=20, primary_key=True, editable=False)
    logistices_types = models.CharField(max_length=255,choices=LOGISTICES_TYPE_CHOICES,default='staff_logistices')
    Typeof_fuel = models.CharField(max_length=255,choices=FUEL_TYPE_CHOICES,default='diesel')
    km_travelled =models.FloatField(default=0.0)
    No_Trips = models.IntegerField(null=True, blank=True)
    fuel_consumption = models.FloatField(default=0.0)
    No_Vehicles = models.IntegerField(null=True, blank=True)
    Spends_on_fuel = models.FloatField(default=0.0)
    total_fuelconsumption = models.FloatField(default=0.0, editable=False)
    def __str__(self):
        return f" data for {self.user.email}"
    
    def save(self,*args, **kwargs):
        if not self.logistices_id:
            self.logistices_id = uuid.uuid4().hex[:8].upper()
        self.total_fuelconsumption = (self.fuel_consumption)
        super(Logistices,self).save(*args, **kwargs)
    