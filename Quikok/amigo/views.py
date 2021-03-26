from django.shortcuts import render
# Create your views here.

def main_amigo(request):
    return render(request, 'amigo/main_amigo.html', {})