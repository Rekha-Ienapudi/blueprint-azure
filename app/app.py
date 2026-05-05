from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "Hello from Azure Container Apps deployed via Terraform 3.99.0 + GitHub Actions!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
