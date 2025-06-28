from django.shortcuts import render, redirect


def index(request):
    return render(request, 'index.html')

def search(request):
    return redirect('de-defender')