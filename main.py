import config
import requests
import json
import subprocess
import boto3

# Acceso a las credenciales
prisma_access_key = config.prisma_access_key
prisma_secret_key = config.prisma_secret_key
aws_access_key = config.aws_access_key
aws_secret_key = config.aws_secret_key
aws_region = config.aws_region

CONSOLE = config.CONSOLE
VERSION = config.VERSION
OUTPUT_FILE = config.OUTPUT_FILE
LAYER_NAME = config.LAYER_NAME

RUNTIME = config.RUNTIME
PROVIDER = config.PROVIDER


# FUNCIÓN PARA OBTENER EL TOKEN DE AUTENTICACIÓN
def get_authentication_token():

    url = f"{CONSOLE}/api/{VERSION}/authenticate"

    payload = json.dumps({
        "username": prisma_access_key, 
        "password": prisma_secret_key,
    })

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    response = requests.post(url, data=payload, headers=headers)

    if response.status_code == 200:
        response_data = response.json()
        token = response_data.get("token")
        return token
    else:
        print("Error en la solicitud del token")
        return None

# FUNCIÓN PARA DESCARGAR EL LAYER DEL DEFENDER
def download_twistlock_bundle(token):

    url = f"{CONSOLE}/api/{VERSION}/defenders/serverless/bundle"
    token = "Bearer " + token
    headers = {
        "Authorization": token,
    }

    payload = json.dumps({
        "runtime": RUNTIME,
        "provider": PROVIDER,
    })

    try:
        # Realizar la solicitud
        response = requests.post(url, headers=headers, data=payload)

        # Verificar si la descarga fue exitosa
        if response.status_code == 200:
            with open(OUTPUT_FILE, "wb") as f:
                f.write(response.content)
            print(f"Serverless Defender Bundle descargado exitosamente en {OUTPUT_FILE}")
        else:
            print("Error al descargar el Serverless Defender Bundle.")
            print(response.text)
    except Exception as e:
        print(f"Error: {str(e)}")

# FUNCIÓN PARA CARGAR EL LAYER A AWS
def load_lambda_layer():

    session = boto3.Session(
        aws_access_key,
        aws_secret_key,
        aws_region
    )

    # Crea un cliente de AWS Lambda utilizando la sesión
    session = session.client('lambda')

    cmd = [
        f"aws lambda publish-layer-version --layer-name {LAYER_NAME} --zip-file fileb://{OUTPUT_FILE}"
    ]

    try:
        subprocess.run(cmd, check=True, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("La capa de Lambda se ha publicado con éxito.")
    except subprocess.CalledProcessError as e:
        print(f"Error al publicar la capa de Lambda: {e}")







bundle = download_twistlock_bundle(get_authentication_token())
load_layer = load_lambda_layer()
