# -*- coding: utf8 -*-
from datetime import time
from django.core.urlresolvers import reverse

from django.db import models
import json
from django.db.models import Q
from autoslug import AutoSlugField
from apps.schedule.models import Term

floors = [(0, 'Parter'), (1, 'I piętro'), (2, 'II Piętro'), (3, 'III piętro')]

class Classroom( models.Model ):
    """classroom in institute"""
    slug =  AutoSlugField(populate_from='number', unique_with='number')
    number = models.CharField( max_length = 20, verbose_name = 'numer sali' )
    building = models.CharField( max_length = 75, verbose_name = 'budynek', blank=True, default='' )
    capacity = models.PositiveSmallIntegerField(default=0, verbose_name='liczba miejsc')
    floor = models.IntegerField(choices=floors, null=True, blank=True)
    can_reserve = models.BooleanField(default=False)

    
    class Meta:
        verbose_name = 'sala'
        verbose_name_plural = 'sale'
        app_label = 'courses'

    def get_absolute_url(self):
        return reverse('events:classroom', args=[self.slug])
    
    def __unicode__(self):
        return self.number + ' ('+str(self.capacity)+')'

    @classmethod
    def get_by_number(cls, number):
        return cls.objects.get(number=number)

    @classmethod
    def get_by_id(cls, id):
        return cls.objects.get(id=id)

    @classmethod
    def get_by_slug(cls, slug):
        return cls.objects.get(slug=slug)


    @classmethod
    def get_terms_in_day(cls, date, ajax=False):
        rooms = cls.get_in_institute(reservation=True)
        terms = Term.objects.filter(day=date, room__in=rooms).select_related('room', 'event')

        if not ajax:
            return rooms

        result = {}

        for room in rooms:

            if not room.number in result:
                result[room.number] = {'id'       : room.id,
                                       'number'  : room.number,
                                       'capacity': room.capacity,
                                       'title': room.number,
                                       'terms': []}

        for term in terms:
            result[term.room.number]['terms'].append({'begin': ':'.join(str(term.start).split(':')[:2]),
                                         'end': ':'.join(str(term.end).split(':')[:2]),
                                         'title': term.event.title})


        return json.dumps(result)


    @classmethod
    def get_in_institute(cls, reservation=False):
        rooms = cls.objects.all()

        if reservation:
            rooms = rooms.filter(can_reserve=True).order_by('floor', 'number')

        return rooms