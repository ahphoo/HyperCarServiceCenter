from django.views import View
from django.shortcuts import render, redirect
from django.http.response import HttpResponse, Http404
from django.views.generic.base import TemplateView

# Global vars
line_of_cars = {
    "change_oil": [],
    "inflate_tires": [],
    "diagnostic": []
}
ticket_number = 0
ticket_time = 0
next_id = -1

class WelcomeView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse('<h2>Welcome to the Hypercar Service!</h2>')

class MenuView(View):
    services = {'change_oil': 'Change oil',
                  'inflate_tires': 'Inflate tires',
                  'diagnostic': 'Get diagnostic test'}

    def get(self, request, *args, **kwargs):
        return render(request, 'tickets/menu.html', context={'services': self.services})

class ServiceView(TemplateView):
    template_name = 'tickets/service.html'

    services_to_time = {
        "change_oil": {
            "time": 2
        },
        "inflate_tires": {
            "time": 5
        },
        "diagnostic": {
            "time": 30
        }
    }

    def get_context_data(self, **kwargs):
        global ticket_number, ticket_time, line_of_cars

        context = super().get_context_data(**kwargs)

        service_name = context['service_name']

        minutes_to_change_oil = 2 * len(line_of_cars['change_oil'])
        minutes_to_inflate_tires = 5 * len(line_of_cars['inflate_tires'])
        minutes_to_diagnostic = 30 * len(line_of_cars['diagnostic'])

        context['minutes_to_wait'] = 0

        if service_name == 'change_oil':
            context['minutes_to_wait'] += minutes_to_change_oil
        if service_name == 'inflate_tires':
            context['minutes_to_wait'] += minutes_to_inflate_tires + minutes_to_change_oil
        elif service_name == 'diagnostic':
            context['minutes_to_wait'] += minutes_to_diagnostic + minutes_to_inflate_tires + minutes_to_change_oil

        ticket_number += 1
        context['ticket_number'] = ticket_number

        line_of_cars[service_name].append(ticket_number)
        #print(line_of_cars)

        return context

class processingView(View):
    def get(self, request, *args, **kwargs):
        num_oil = len(line_of_cars['change_oil'])
        num_tires = len(line_of_cars['inflate_tires'])
        num_diagnostic = len(line_of_cars['diagnostic'])

        num_tickets = {'oil': num_oil, 'tires': num_tires, 'diagnostic': num_diagnostic}

        return render(request, 'tickets/processing.html', context={'num_tickets': num_tickets})

    def post(self, request, *args, **kwargs):
        global next_id

        if line_of_cars['change_oil']:
            next_id = line_of_cars['change_oil'][0]
            line_of_cars['change_oil'].pop(0)
        elif line_of_cars['inflate_tires']:
            next_id = line_of_cars['inflate_tires'][0]
            line_of_cars['inflate_tires'].pop(0)
        elif line_of_cars['diagnostic']:
            next_id = line_of_cars['diagnostic'][0]
            line_of_cars['diagnostic'].pop(0)
        else:
            next_id = -1

        return redirect('/next')

class nextView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'tickets/next.html', context={'number_of_ticket': next_id})
