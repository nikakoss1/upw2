from rest_framework import pagination

class DubicarsAPIPagination(pagination.LimitOffsetPagination):
    page_size   =  100
    default_limit   = 10
    max_limit       = 100
    #limit_query_param = 'lim'