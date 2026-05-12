import random
import string
import uuid
import time
import threading

from flask import Flask, render_template, request, jsonify

from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.containerregistry import ContainerRegistryManagementClient
from azure.mgmt.containerregistry.models import Registry

app = Flask(__name__)
cred = DefaultAzureCredential()

# =========================
# STATE
# =========================
JOBS = {}
RG_STORE = {}


# =========================
# HELPERS
# =========================

def clean(x):
    return ''.join(c for c in x.lower() if c.isalnum())


def rg_name(u, e, o):
    return f"rg-{clean(u)}-{clean(e)}-{clean(o)}"


def storage_name(u, e, o):
    return f"st{clean(u+e+o)[:12]}{''.join(random.choices(string.digits, k=4))}"[:24]


def acr_name(u, e, o):
    return f"acr{clean(u+e+o)[:16]}{''.join(random.choices(string.digits, k=4))}"


# =========================
# JOB ENGINE
# =========================

def new_job():
    jid = str(uuid.uuid4())
    JOBS[jid] = {
        "status": "RUNNING",
        "progress": 0,
        "logs": [],
        "resources": [],
        "rg": None,
        "acr_login": None
    }
    return jid


def log(jid, msg):
    JOBS[jid]["logs"].append({
        "time": time.strftime("%H:%M:%S"),
        "msg": msg
    })


def add_resource(jid, t, n, s, e=""):
    JOBS[jid]["resources"].append({
        "type": t,
        "name": n,
        "status": s,
        "error": e
    })


# =========================
# DEPLOYMENT (UNCHANGED LOGIC)
# =========================

def deploy(job_id, sub, f):

    try:
        rg_client = ResourceManagementClient(cred, sub)
        st_client = StorageManagementClient(cred, sub)
        acr_client = ContainerRegistryManagementClient(cred, sub)

        u = f["usecase"]
        e = f["env"]
        owner = f["owner"]
        email = f["owner_email"]

        if not email or "@" not in email:
            raise ValueError("owner_email required")

        rg = rg_name(u, e, owner)
        JOBS[job_id]["rg"] = rg

        tags = {
            "usecase": u,
            "env": e,
            "owner": email
        }

        # =====================
        # RG
        # =====================
        log(job_id, f"Creating RG {rg}")

        rg_client.resource_groups.create_or_update(
            rg,
            {"location": f["location"], "tags": tags}
        )

        RG_STORE[rg] = {"time": time.strftime("%H:%M:%S")}

        add_resource(job_id, "Resource Group", rg, "SUCCESS")
        JOBS[job_id]["progress"] = 20

        # =====================
        # STORAGE
        # =====================
        st = storage_name(u, e, owner)

        log(job_id, f"Creating Storage {st}")

        st_client.storage_accounts.begin_create(
            rg,
            st,
            {
                "location": f["location"],
                "sku": {"name": f["storage_tier"]},
                "kind": "StorageV2"
            }
        ).result()

        add_resource(job_id, "Storage", st, "SUCCESS")
        JOBS[job_id]["progress"] = 60

        # =====================
        # ACR
        # =====================
        acr = acr_name(u, e, owner)

        log(job_id, f"Creating ACR {acr}")

        acr_client.registries.begin_create(
            rg,
            acr,
            Registry(
                location=f["location"],
                sku={"name": f["acr_sku"]},
                admin_user_enabled=True
            )
        ).result()

        add_resource(job_id, "ACR", acr, "SUCCESS")

        JOBS[job_id]["acr_login"] = f"{acr}.azurecr.io"

        JOBS[job_id]["progress"] = 100
        JOBS[job_id]["status"] = "DONE"

        log(job_id, "Deployment completed")

    except Exception as e:
        JOBS[job_id]["status"] = "FAILED"
        log(job_id, str(e))


# =========================
# API
# =========================

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/start", methods=["POST"])
def start():

    job_id = new_job()
    f = request.form

    threading.Thread(
        target=deploy,
        args=(job_id, f["subscription_id"], f)
    ).start()

    return jsonify({"job_id": job_id})


@app.route("/status/<jid>")
def status(jid):
    return jsonify(JOBS.get(jid))


# =========================
# RETRY
# =========================

@app.route("/retry", methods=["POST"])
def retry():

    data = request.json
    job_id = data["job_id"]
    rtype = data["type"]
    name = data["name"]
    sub = data["subscription"]

    job = JOBS[job_id]
    rg = job["rg"]

    try:
        rg_client = ResourceManagementClient(cred, sub)
        st_client = StorageManagementClient(cred, sub)
        acr_client = ContainerRegistryManagementClient(cred, sub)

        if rtype == "Storage":
            st_client.storage_accounts.begin_create(
                rg, name,
                {
                    "location": "westeurope",
                    "sku": {"name": "Standard_LRS"},
                    "kind": "StorageV2"
                }
            ).result()

        if rtype == "ACR":
            acr_client.registries.begin_create(
                rg,
                name,
                Registry(location="westeurope",
                         sku={"name": "Basic"},
                         admin_user_enabled=True)
            ).result()

        for r in job["resources"]:
            if r["name"] == name:
                r["status"] = "SUCCESS"
                r["error"] = ""

        return jsonify({"ok": True})

    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


# =========================
# RG DASHBOARD
# =========================

@app.route("/rgs")
def rgs():
    return jsonify([
        {"name": k, "time": v["time"]}
        for k, v in RG_STORE.items()
    ])


@app.route("/delete_rg", methods=["POST"])
def delete_rg():

    data = request.json
    rg = data["rg"]
    sub = data["subscription"]

    try:
        client = ResourceManagementClient(cred, sub)
        client.resource_groups.begin_delete(rg)

        RG_STORE.pop(rg, None)

        return jsonify({"ok": True})

    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


# =========================
# RUN
# =========================

if __name__ == "__main__":
    app.run(debug=True)