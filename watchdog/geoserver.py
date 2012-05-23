from watchdog.core import *
from geonode.maps.models import Layer
from django.conf import settings
from urllib import urlopen

def suite():
    return (
        #get_capabilities, 
        get_layer_capabilities,
    )
    
@check
def get_capabilities():
    Layer.objects.get_wms()
    
@check_many
def get_layer_capabilities():
    return (
        subcheck(_check_layer_capabilities,l.typename,l) 
        for l in Layer.objects.all().iterator()
    )
    
@check_many
def get_layer_has_latlon_bbox():
    return (
        subcheck(_check_layer,l.typename,l) for l in Layer.objects.all().iterator()
    )
    
def _check_layer_latlon_bbox(layer):
    if layer.resource.latlon_bbox is None:
        raise CheckFailed('missing bbox')
            
def _check_layer_capabilities(layer):
    try:
        layer.metadata()
        return
    except:
        pass
    url = settings.GEOSERVER_BASE_URL + "%s/%s/" % tuple(layer.typename.split(':'))
    url = url + "wms?request=getcapabilities&version=1.1.0"
    try:
        xml = urlopen(url).read()
    except Exception,ex:
        raise CheckFailed('error reading from url: %s , %s',url,ex)
    try:
        dom = fromstring(xml)
    except:
        raise CheckFailed('invalid xml:\n%s' % xml)