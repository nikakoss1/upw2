# -*- coding: utf-8 -*-
from django.db.models import Q
from rest_framework import routers, serializers
from rest_framework import validators
from rest_framework.reverse import reverse as api_reverse
import datetime, re
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

today = datetime.date.today()

class WebsiteCharacteristicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Website
        fields = [
            'id',
            'name',
            'url',
            'content',
        ]

class DubicarsCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DubicarsCategory
        fields = [
            'id',
            'name',
            'url',
            'content',
            'parent',
            'seo_title',
            'seo_keywords',
            'seo_description',
            'seo_h1',
            'created',
            'updated',
        ]


class UpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Update
        fields = [
            'id',
            'website',
            'total_ads_number',
            'total_category_number',
            'total_pages_number',
            'total_ads_number',
            'total_updated_ads_number',
            'status',
            'current_stage',
            'created',
            'updated',
        ]


class DubicarsPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DubicarsPage
        fields = [
            'id',
            'url',
            'created',
            'updated',
        ]


class DubicarsAdCharacteristicSerializer(serializers.ModelSerializer):
    class Meta:
        model = DubicarsAdCharacteristic
        fields = [
            'id',
            'name',
            'value',
        ]


class DubicarsAdInteriorDesignSerializer(serializers.ModelSerializer):
    class Meta:
        model = DubicarsAdInteriorDesign
        fields = [
            'id',
            'name',
        ]


class DubicarsAdExteriorFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = DubicarsAdExteriorFeature
        fields = [
            'id',
            'name',
        ]


class DubicarsAdSecuritySerializer(serializers.ModelSerializer):
    class Meta:
        model = DubicarsAdSecurity
        fields = [
            'id',
            'name',
        ]


class DubicarsAdServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DubicarsAdService
        fields = [
            'id',
            'name',
        ]


class DubicarsAdFinanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DubicarsAdFinance
        fields = [
            'id',
            'name',
        ]


class DubicarsAdWarrantySerializer(serializers.ModelSerializer):
    class Meta:
        model = DubicarsAdWarranty
        fields = [
            'id',
            'name',
        ]


class DubicarsTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = DubicarsTag
        fields = [
            'id',
            'name',
        ]


class DubiscrapeImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DubiscrapeImage
        fields = [
            'id',
            'dubicar_ad',
            'image',
        ]


class DubicarsAdSerializer(serializers.ModelSerializer):
    category = DubicarsCategorySerializer(read_only=True, many=True)
    dubicar_ad_charact = DubicarsAdCharacteristicSerializer(read_only=True, many=True)
    dubicars_ad_exterior_design = DubicarsAdExteriorFeatureSerializer(read_only=True, many=True)
    dubicars_ad_interior_design = DubicarsAdInteriorDesignSerializer(read_only=True, many=True)
    dubicars_ad_security = DubicarsAdSecuritySerializer(read_only=True, many=True)
    dubicars_ad_finance = DubicarsAdFinanceSerializer(read_only=True, many=True)
    dubicars_ad_warranty = DubicarsAdWarrantySerializer(read_only=True, many=True)
    dubicars_ad_service = DubicarsAdServiceSerializer(read_only=True, many=True)
    dubicars_tags = DubicarsTagSerializer(read_only=True, many=True)
    dubiscrapeimage_set = DubiscrapeImageSerializer(read_only=True, many=True)
    class Meta:
        model = DubicarsAd
        fields = [
            'id',
            'name',
            'url',
            'short_desc',
            'price',
            'curr',
            'maps_coords',
            'desc',
            'phone',
            'seo_title',
            'seo_keywords',
            'seo_description',
            'seo_h1',
            'other_vendor_models',
            'similar_models',
            'category',
            'dubicar_ad_charact',
            'dubicars_ad_interior_design',
            'dubicars_ad_exterior_design',
            'dubicars_ad_security',
            'dubicars_ad_finance',
            'dubicars_ad_warranty',
            'dubicars_ad_service',
            'dubicars_tags',
            'dubiscrapeimage_set',
            'update',
            'created',
            'updated',
        ]



