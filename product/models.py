from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None):
        if not username:
            raise ValueError('Kullanıcı adı gereklidir')
        user = self.model(username=username, email=email)
        user.set_password(password)  # Şifreyi hash'leyerek kaydediyoruz
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None):
        user = self.create_user(username, email, password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    team = models.ForeignKey('Team', null=True, blank=True, on_delete=models.SET_NULL)  # team alanı eklendi

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []  # sadece kullanıcı adı yeterli

    objects = UserManager()

    def __str__(self):
        return self.username


class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    can_manage_parts = models.BooleanField(default=False)
    allowed_part_types = models.JSONField(default=list)

    def __str__(self):
        return self.name



class AircraftModel(models.Model):
    name = models.CharField(max_length=100) 
    
    def __str__(self):
        return self.name

class Part(models.Model):
    part_type = models.CharField(max_length=100)  
    part_name = models.CharField(max_length=100)  
    aircraft_model = models.ForeignKey(AircraftModel, on_delete=models.CASCADE)  
    team = models.ForeignKey(Team, on_delete=models.CASCADE)  # Doğrudan ForeignKey olarak 'team' ilişkisinin kullanımı
    part_id = models.AutoField(primary_key=True)  # Otomatik artan bir id
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.part_name


class Assembly(models.Model):
    aircraft_model = models.ForeignKey('AircraftModel', on_delete=models.CASCADE)
    parts = models.ManyToManyField(Part)
    assembly_date = models.DateTimeField(auto_now_add=True)
    is_listed = models.BooleanField(default=False) 

    def __str__(self):
        return f"{self.aircraft_model.name} - {self.assembly_date}"
