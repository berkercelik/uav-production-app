from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.http import HttpResponse
from .forms import RegisterForm, LoginForm
from .models import User, Team, Part, AircraftModel, Assembly
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import PartSerializer, AircraftModelSerializer
from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view



def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = User.objects.create_user(username=username, email=email, password=password)

        if user is not None:
            auth_login(request, user)  # Kullanıcıyı oturum açtır
            return redirect('dashboard')  # Başarılı giriş sonrası yönlendirme
        else:
            return render(request, 'product/register.html', {
                'error_message': 'Geçersiz kayıt bilgileri'  # Hata mesajı
            })        
    return render(request, 'product/register.html')


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')  # POST'tan username al
        password = request.POST.get('password')  # POST'tan password al
        
        print(f'Attempting to authenticate user: {username}')
        # Kullanıcıyı doğrulama
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)  # Kullanıcıyı oturum açtır
            return redirect('dashboard')  # Başarılı giriş sonrası yönlendirme
        else:
            return render(request, 'product/login.html', {
                'error_message': 'Geçersiz giriş bilgileri'  # Hata mesajı
            })
    
    return render(request, 'product/login.html')


def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')

    teams = Team.objects.all()
    success_message = None 

    team_name = None 
    if request.user.is_authenticated:  # Kullanıcı giriş yapmış mı kontrol et
        team = Team.objects.filter(id=request.user.team_id).first()  # Team tablosundan sorgu yap
        if team:
            team_name = team.name  # Eğer takım varsa, ismini al

    if request.method == 'POST':
        team_id = request.POST.get('team')
        if team_id:
            selected_team = Team.objects.get(id=team_id)  # Seçilen takım
            request.user.team = selected_team  # Kullanıcının takımını güncelle
            request.user.save()  # Değişiklikleri kaydet
            success_message = f"{selected_team.name}na atandınız."  # Başarı mesajı

    # Kullanıcının takımını kontrol et
    user_team = getattr(request.user, 'team', None)  # Kullanıcıya atanmış takım varsa al
    can_manage_parts = user_team.can_manage_parts if user_team else False  # Yetkisini kontrol et

    context = {
        'teams': teams,
        'success_message': success_message,
        'can_manage_parts': can_manage_parts,
        'team_name': team_name,
    }

    return render(request, 'product/dashboard.html', context)


def produce_part(request):
    if not request.user.is_authenticated:
        return redirect('login')

    aircraft_models_id = AircraftModel.objects.all()
    
    if request.method == 'POST':
        aircraft_model_id = request.POST.get('aircraft_model_id')
        part_type = request.POST.get('part_type')
        part_name = request.POST.get('part_name')
        
        part = Part.objects.create(
            aircraft_model_id=aircraft_model_id,
            part_type=part_type,
            part_name=part_name
        )
        
        return redirect('dashboard')

    return render(request, 'produce_part.html', {'aircraft_models': aircraft_models})

# def home(request):
#     if request.user.is_authenticated:
#         # Kullanıcı giriş yapmışsa farklı bir şablon göster
#         return render(request, 'users/dashboard.html', {'user': request.user})
#     else:
#         # Giriş yapmamış kullanıcılar için varsayılan anasayfa
#         listed_aircrafts = Assembly.objects.filter(is_listed=True)

#         # Veriyi home.html şablonuna gönder
#         return render(request, 'home.html', {'listed_aircrafts': listed_aircrafts})

def home(request):
    if request.user.is_authenticated:
        # Kullanıcı giriş yapmışsa farklı bir şablon göster
        listed_aircrafts = Assembly.objects.filter(is_listed=True)

        # Veriyi home.html şablonuna gönder
        return render(request, 'home.html', {'listed_aircrafts': listed_aircrafts})
    else:
        # Giriş yapmamış kullanıcılar için varsayılan anasayfa
        listed_aircrafts = Assembly.objects.filter(is_listed=True)

        # Veriyi home.html şablonuna gönder
        return render(request, 'home.html', {'listed_aircrafts': listed_aircrafts})

class PartListView(APIView):
    def get(self, request, *args, **kwargs):
        # Takım id ve parça türüne göre parçaları listele
        team_id = request.query_params.get('team_id')
        part_type = request.query_params.get('part_type')

        team = Team.objects.get(id=team_id)
        if team.can_manage_parts:
            parts = Part.objects.filter(team=team, part_type=part_type)
            return Response({"parts": [{"id": part.id, "name": part.part_name} for part in parts]})
        else:
            return Response({"message": "Geçersiz takım."}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def getData(request):
    person = {'name': 'test'}
    return Response(person)


class ListPartsView(APIView):
    def get(self, request, *args, **kwargs):
        team_id = request.query_params.get('team_id')  # 'team_id' parametresini GET isteğiyle alıyoruz

        if not team_id:
            return Response({"message": "Takım ID'si sağlanmalı."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            team = Team.objects.get(id=team_id)
        except Team.DoesNotExist:
            return Response({"message": "Geçersiz takım ID."}, status=status.HTTP_404_NOT_FOUND)

        # users_part veritabanındaki, takım id'si ile eşleşen tüm parçaları al
        parts = Part.objects.filter(team_id=team_id)

        # Parçaların verilerini yapılandırma
        parts_data = [
            {
                "id": part.part_id,
                "part_type": part.part_type,
                "part_name": part.part_name,
                "aircraft_model": part.aircraft_model.name,  # Aircraft model adı
            }
            for part in parts
        ]

        if not parts_data:
            return Response({"message": "Bu takım için uygun parça bulunamadı."}, status=status.HTTP_404_NOT_FOUND)

        return Response({"team_name": team.name, "parts": parts_data}, status=status.HTTP_200_OK)

class DeletePartView(APIView):
    def delete(self, request, part_id, *args, **kwargs):
        try:
            part = Part.objects.get(part_id=part_id)
        except Part.DoesNotExist:
            return Response({"message": "Geçersiz parça ID."}, status=status.HTTP_404_NOT_FOUND)
        
        # Parçayı sil
        part.delete()
        return Response({"message": "Parça başarıyla silindi."}, status=status.HTTP_200_OK)

class ProducePartView(APIView):
    def post(self, request, *args, **kwargs):
        part_type = request.data.get('part_type')
        part_name = request.data.get('part_name')
        aircraft_model = request.data.get('aircraft_model')
        team_id = request.data.get('team_id')  # Kullanıcıya ait takım id'si

        if not all([part_type, part_name, aircraft_model, team_id]):
            return Response({"message": "Tüm alanlar gereklidir."}, status=status.HTTP_400_BAD_REQUEST)

        # Geçerli model olup olmadığını kontrol et
        try:
            aircraft_model = AircraftModel.objects.get(id=aircraft_model)
        except AircraftModel.DoesNotExist:
            return Response({"message": "Geçersiz uçak modeli."}, status=status.HTTP_400_BAD_REQUEST)
        
        team = Team.objects.get(id=team_id)
        if not team.can_manage_parts:
            return Response({"message": "Bu takım parça üretemez."}, 
            status=status.HTTP_400_BAD_REQUEST)

        if team.name == 'Montaj Takımı':
            return Response({"message": "Montaj Takımı hiç bir parçayı üretemez."}, 
            status=status.HTTP_400_BAD_REQUEST)

        if part_type not in team.allowed_part_types:
            return Response(
                {"message": f"{team.name} bu tür parçayı üretemez: {part_type}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Yeni parça oluşturma
        part = Part.objects.create(
            part_type=part_type,
            part_name=part_name,
            aircraft_model=aircraft_model,
            team_id=team_id,
        )

        # Başarılı yanıt
        return Response({"message": f"{part_name} üretildi."}, status=status.HTTP_201_CREATED)


class AircraftProductionView(APIView):
    def post(self, request, *args, **kwargs):
        # Gelen uçak modeli ID'si
        aircraft_model_id = request.data.get("aircraft_model_id")

        # Uçak modelini kontrol et
        try:
            aircraft_model = AircraftModel.objects.get(id=aircraft_model_id)
        except AircraftModel.DoesNotExist:
            return Response({"message": "Geçersiz uçak modeli."}, status=status.HTTP_400_BAD_REQUEST)

        # Uçak modeline uygun parçaların isimleri
        required_part_names = [
            f"{aircraft_model.name} Kanadı",
            f"{aircraft_model.name} Gövdesi",
            f"{aircraft_model.name} Kuyruğu",
            f"{aircraft_model.name} Aviyonik",
        ]

        # Veritabanında parçaları sorgula, quantity=1 olanları al
        required_parts = []
        for part_name in required_part_names:
            part = Part.objects.filter(part_name=part_name, quantity__gte=1).first()  
            # 1 adet parça kullanmak için ilk bulunanı .first ile al
            if part:
                required_parts.append(part)

        # Eksik parçaları kontrol et
        missing_parts = [
            part_name for part_name in required_part_names
            if part_name not in [part.part_name for part in required_parts]
        ]

        if missing_parts:
            return Response(
                {
                    "message": "Eksik veya yetersiz parçalar var",
                    "missing_parts": missing_parts,  # Bu liste olmalı
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Parçaların quantity değerlerini güncelle, kullanıldıktan sonra 0 olur.
        for part in required_parts:
            part.quantity = 0
        Part.objects.bulk_update(required_parts, ["quantity"])

        # Assembly kaydını oluştur
        assembly = Assembly.objects.create(aircraft_model=aircraft_model)
        assembly.parts.set(required_parts)  # Parçaları ilişkilendir
        assembly.save()

        return Response(
            {"message": "Uçak başarıyla üretildi ve kaydedildi."},
            status=status.HTTP_200_OK,
        )

class AircraftListView(APIView):
    def get(self, request, *args, **kwargs):
        assemblies = Assembly.objects.all()
        aircraft_list = []
        for assembly in assemblies:
            aircraft = {
                'id': assembly.id,
                'aircraft_model': assembly.aircraft_model.name,
                'assembly_date': assembly.assembly_date,
                'parts': [{'part_name': part.part_name} for part in assembly.parts.all()],
                'is_listed': assembly.is_listed
            }
            aircraft_list.append(aircraft)
        
        return Response({'assemblies': aircraft_list}, status=status.HTTP_200_OK)
        
    def post(self, request, *args, **kwargs):
        aircraft_id = request.data.get('aircraft_id')
        try:
            assembly = Assembly.objects.get(id=aircraft_id)
            assembly.is_listed = True  # Uçağı listele
            assembly.save()
            return Response({"message": "Uçak başarıyla listeye alındı."}, status=status.HTTP_200_OK)
        except Assembly.DoesNotExist:
            return Response({"message": "Uçak bulunamadı."}, status=status.HTTP_404_NOT_FOUND)

class AircraftRemoveView(APIView):
    def post(self, request, *args, **kwargs):
        aircraft_id = request.data.get('aircraft_id')
        try:
            assembly = Assembly.objects.get(id=aircraft_id)
            assembly.is_listed = False  # Uçağı yayından kaldır
            assembly.save()
            return Response({"message": "Uçak başarıyla yayından kaldırıldı."}, status=status.HTTP_200_OK)
        except Assembly.DoesNotExist:
            return Response({"message": "Uçak bulunamadı."}, status=status.HTTP_404_NOT_FOUND)


