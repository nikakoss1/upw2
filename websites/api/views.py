# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from websites.api.serializers import (
    WebsiteCharacteristicSerializer,
    DubicarsCategorySerializer,
    UpdateSerializer,
    DubicarsPageSerializer,
    DubicarsAdCharacteristicSerializer,
    DubicarsAdInteriorDesignSerializer,
    DubicarsAdExteriorFeatureSerializer,
    DubicarsAdSecuritySerializer,
    DubicarsAdServiceSerializer,
    DubicarsAdFinanceSerializer,
    DubicarsAdWarrantySerializer,
    DubicarsTagSerializer,
    DubiscrapeImageSerializer,
    DubicarsAdSerializer,
    )
from websites.dubicars_models import (
    Website,
    DubicarsCategory,
    Update,
    DubicarsPage,
    DubicarsAdCharacteristic,
    DubicarsAdInteriorDesign,
    DubicarsAdExteriorFeature,
    DubicarsAdSecurity,
    DubicarsAdService,
    DubicarsAdFinance,
    DubicarsAdWarranty,
    DubicarsTag,
    DubicarsAd,
    DubiscrapeImage,
    AdError,
    )
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from rest_framework import generics, mixins
from rest_framework import permissions
from rest_framework.views import APIView
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status, viewsets


class DubicarsAdRetrieveAPIView(generics.RetrieveAPIView):
    queryset = DubicarsAd.objects.all()
    serializer_class = DubicarsAdSerializer
    lookup_field = 'pk'


class DubicarsAdListAPIView(generics.ListAPIView):
    queryset = DubicarsAd.objects.all()
    serializer_class = DubicarsAdSerializer

