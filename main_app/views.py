from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.views.generic import ListView, DetailView 
from django.contrib.auth import login, authenticate
from .models import Patient, Doctor, Appointment, Prescription
from django.contrib.auth.models import User
from .forms import UserForm, PatientForm, PrescriptionForm, NewUserForm
import requests


# Create your views here.


def home(request):
    return render(request, 'home.html')

def dash_index(request):
    return render(request, 'dashboard/index.html')

def appointments_index(request):
    appointments = Appointment.objects.filter(user=request.user)
    return render(request, 'appointments/index.html', 
        {
            'appointments': appointments,
        })


def documents_index(request):
    return render(request, 'documents/index.html')


def prescriptions_index(request):
    prescriptions = Prescription.objects.all
    
    
    prescription_form = PrescriptionForm()

    return render(request, 'prescriptions/index.html',
        {
            'prescriptions': prescriptions,
            'prescription_form': prescription_form,
            
        })


# User functionality

def update_profile(request):
    error_message = ''
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        patient_form = PatientForm(request.POST, instance = request.user.patient)
        if user_form.is_valid() and patient_form.is_valid():
            user_form.save()
            patient_form.save()
            return redirect('index')
        else:
            error_message = 'Invalid entries - please try again'
    else: 
        user_form = UserForm(instance=request.user)
        patient_form = PatientForm(instance=request.user.patient)
    return render(request, 'dashboard/profile.html', {
        'user_form': user_form,
        'patient_form': patient_form
    })


def signup(request):
    error_message = ''
    if request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
        else: 
            error_message = 'Invalid sign-up - try again'
    form = NewUserForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'registration/signup.html', context)


class AppointmentDetail(DetailView):
    model = Appointment
    template_name = 'appointments/detail.html'

class AppointmentCreate(CreateView):
    model = Appointment
    fields = ['date', 'doctor']

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class AppointmentUpdate(UpdateView):
    model = Appointment
    fields = ['date', 'doctor']

class AppointmentDelete(DeleteView):
    model = Appointment
    success_url = '/appointments/'

class PrescriptionCreate(CreateView):
    model = Prescription
    # fields = ['name', 'size']
    form_class = PrescriptionForm
    template_name = "prescriptions/prescription_form.html"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class PrescriptionUpdate(UpdateView):
    model = Prescription
    fields = ['size', 'instructions', 'notes', 'prescribed', 'doctor']


def update_prescription(request, user_id):
    
    form = PrescriptionForm(request.POST)

    if form.is_valid():
        update_prescription = form.save(commit=False)
        update_prescription.save()
    return redirect('/prescriptions', user_id=user_id)

def add_prescription(request, user_id):

    form = PrescriptionForm(request.POST)
    
    if form.is_valid():
        new_prescription = form.save(commit=False)
        # new_prescription.name = data[2]['DISPLAY_NAME'][0]
        # new_prescription.size = data[2]['STRENGTHS_AND_FORMS'][0][0]
        new_prescription.user_id = user_id
        new_prescription.save()
    return redirect('/prescriptions', user_id=user_id)


def provider_index(request):
    url = 'https://data.cms.gov/data-api/v1/dataset/92396110-2aed-4d63-a6a2-5d6207d46a29/data'
    response = requests.get(url)
    data = response.json()

    print(data)
    context = {
        'city' : data[0]['Rndrng_Prvdr_City'],
        'state' : data[0]['Rndrng_Prvdr_State_Abrvtn'],
        'last' : data[0]['Rndrng_Prvdr_Last_Org_Name'],
        'zip' : data[0]['Rndrng_Prvdr_Zip5'],
        'type' : data[0]['Rndrng_Prvdr_Type']
    }

    return render(request, 'provider/index.html', {'context':context})
