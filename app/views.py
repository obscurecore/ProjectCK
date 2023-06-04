from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.views import View

from app.forms import ObjectForm
from app.models import User
from app.utils import get_price, get_price_history, neural_model, get_house_info

prediction_model = neural_model()

class Register(View):
    template_name='registration/register.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        data = request.POST
        if User.objects.filter(username=data.get('username')).exists():
            error = 'user already exist'
            return render(request, self.template_name, {'error': error})
        if data.get('password1') != data.get('password2'):
            error = 'password mismatch'
            return render(request, self.template_name, {'error': error})
        try:
            user = User(username=data.get('username'))
            user.set_password(data.get('password1'))
            user.save()
        except:
            error = 'error'
            return render(request, self.template_name, {'error': error})

        username = data.get('username')
        password = data.get('password1')
        user = authenticate(username=username, password=password)
        login(request, user)
        return redirect('main')


class MainView(View):

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('login')
        return render(request, 'main_page.html')

    def post(self, request):
        r = ObjectForm(request.POST)
        if r.is_valid():
            columns = prediction_model.get("features")
            data = r.cleaned_data
            f1 = [int(data.get("level")), int(data.get("levels")), int(data.get("rooms")), int(data.get("area")), int(data.get("kitchen_area")), 0]
            f2 = [0 for i in range(len(columns) - 6)]
            f = f1+f2
            if str(float(data.get("postal_code"))) in columns:
                f[columns.index(str(float(data.get("postal_code"))))] = 1
            f = [f]
            prices = get_price(address=r.cleaned_data.get("address"), rooms=r.cleaned_data.get("rooms"), area=r.cleaned_data.get("area"))
            if prices.get("error"):
                return render(request, 'result.html', {"message": "Нет данных по объекту"})

            price_history = get_price_history(address=r.cleaned_data.get("address"))
            my_prices = []
            my_prices.append(round(prediction_model.get("model").predict(f)[0][0]*price_history.get("city_coef")/1000000, 2))
            my_prices.append(round(prediction_model.get("model").predict(f)[0][0]*price_history.get("house_coef")/1000000, 2))
            my_prices.append(round(prediction_model.get("model").predict(f)[0][0]*price_history.get("district_coef")/1000000, 2))
            my_prices.sort()

            house_info = get_house_info(address=r.cleaned_data.get("address"))

            return render(request, 'result.html',
                          {"my_prices": my_prices, "price_history": price_history,
                           "house_info": house_info})
