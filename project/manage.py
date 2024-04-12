import json
import os
import threading
import time

from django.core import serializers
from django.http import JsonResponse, HttpResponse
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from peeringdb import resource, get_backend
from peeringdb.client import Client
from django.conf import settings

pdb = Client(cfg={
    "orm": {
        "backend": "django_peeringdb",
        "database": {
            "engine": "sqlite3",
            "name": "/data/peeringdb.sqlite3",
            "user": "",
            "password": "",
            "host": "",
            "port": "",
        },
        "migrate": True,
        "secret_key": "",
    },
    "sync": {
        "api_key": os.environ.get("PEERINGDB_API_KEY", ""),
        "only": [],
        "password": "",
        "strip_tz": 1,
        "timeout": 0,
        "url": "https://www.peeringdb.com/api",
        "user": "",
    }
})

settings.ALLOWED_HOSTS = ['*']
settings.ROOT_URLCONF = 'urls'
settings.SECRET_KEY = '1234567890'

sync = threading.Thread(target=pdb.updater.update_all, args=(resource.all_resources(),), daemon=True)
sync.start()
last_sync = time.time()

def model_to_jdict(model):
    d = json.loads(serializers.serialize("json", [model]))[0]
    resp = d["fields"]
    resp["id"] = d["pk"]
    return resp

def parse_args(request):
    args = {}
    for k, v in request.GET.items():
        if "__lt" in k:
            field_name = k.split("__lt")[0]
            args[field_name + "__lt"] = int(v)
        elif "__lte" in k:
            field_name = k.split("__lte")[0]
            args[field_name + "__lte"] = int(v)
        elif "__gt" in k:
            field_name = k.split("__gt")[0]
            args[field_name + "__gt"] = int(v)
        elif "__gte" in k:
            field_name = k.split("__gte")[0]
            args[field_name + "__gte"] = int(v)
        elif "__contains" in k:
            field_name = k.split("__contains")[0]
            args[field_name + "__contains"] = v
        elif "__in" in k:
            field_name = k.split("__in")[0]
            args[field_name + "__in"] = [item.strip() for item in v.split(",")]
        else:
            try:
                args[k] = int(v)
            except ValueError:
                args[k] = v
    return args

@csrf_exempt
def find_by_args(request, model):
    args = parse_args(request)
    if not args:
        return JsonResponse({"data": [model_to_jdict(i) for i in pdb.all(model)]})

    out = None
    for k, v in args.items():
        if out is None:
            b = get_backend()
            out = [model_to_jdict(i) for i in b.get_objects_by(b.get_concrete(model), k, v)]
            continue
        out = [i for i in out if i.get(k) == v]

    return JsonResponse({"data": out})

def metrics(request):
    total_orgs = len(pdb.all(resource.Organization))
    total_fac = len(pdb.all(resource.Facility))
    total_net = len(pdb.all(resource.Network))
    total_ix = len(pdb.all(resource.InternetExchange))
    total_campus = len(pdb.all(resource.Campus))
    total_carrier = len(pdb.all(resource.Carrier))
    total_carrierfac = len(pdb.all(resource.CarrierFacility))
    total_ixfac = len(pdb.all(resource.InternetExchangeFacility))
    total_ixlan = len(pdb.all(resource.InternetExchangeLan))
    total_ixpfx = len(pdb.all(resource.InternetExchangeLanPrefix))
    total_netfac = len(pdb.all(resource.NetworkFacility))
    total_netixlan = len(pdb.all(resource.NetworkIXLan))
    total_poc = len(pdb.all(resource.NetworkContact))

    metrics = f"""# HELP peeringdb_cache_entries Number of entries in the PeeringDB cache
# TYPE peeringdb_cache_entries counter
peeringdb_cache_entries{{model="orgs"}} {total_orgs}
peeringdb_cache_entries{{model="fac"}} {total_fac}
peeringdb_cache_entries{{model="net"}} {total_net}
peeringdb_cache_entries{{model="ix"}} {total_ix}
peeringdb_cache_entries{{model="campus"}} {total_campus}
peeringdb_cache_entries{{model="carrier"}} {total_carrier}
peeringdb_cache_entries{{model="carrierfac"}} {total_carrierfac}
peeringdb_cache_entries{{model="ixfac"}} {total_ixfac}
peeringdb_cache_entries{{model="ixlan"}} {total_ixlan}
peeringdb_cache_entries{{model="ixpfx"}} {total_ixpfx}
peeringdb_cache_entries{{model="netfac"}} {total_netfac}
peeringdb_cache_entries{{model="netixlan"}} {total_netixlan}
peeringdb_cache_entries{{model="poc"}} {total_poc}

# HELP peeringdb_sync_running Is a sync task running?
# TYPE peeringdb_sync_running gauge
peeringdb_sync_running {int(sync.is_alive())}

# HELP peeringdb_last_sync Epoch of last sync
# TYPE peeringdb_last_sync gauge
peeringdb_last_sync {int(last_sync)}
"""
    return HttpResponse(metrics, content_type="text/plain")

@csrf_exempt
def sync_start(request):
    global sync, last_sync
    if not sync.is_alive():
        rs = resource.all_resources()
        sync = threading.Thread(target=pdb.updater.update_all, args=(rs,), daemon=True)
        sync.start()
        last_sync = time.time()
        return JsonResponse({"started": True})
    return JsonResponse({"started": False}, status=409)

if __name__ == "__main__":
    import sys
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
