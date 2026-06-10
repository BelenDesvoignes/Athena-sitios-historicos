from flask import current_app
from src.web.storage import get_s3_client


def get_site_images(sitio, only_cover=False):
    """
    Obtiene imágenes del sitio y genera URLs presignadas.
    Si only_cover=True, solo devuelve la portada.
    Retorna (cover_url, cover_title, lista_de_imagenes)
    """
    s3_client = get_s3_client()
    bucket_name = current_app.config["MINIO_BUCKET"]
    default_url = None

    if only_cover:
        portada = next((img for img in sitio.imagenes if img.es_portada), None)
        if portada:
            try:
                cover_url = s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': bucket_name, 'Key': portada.ruta},
                    ExpiresIn=7200,
                )
                print(f"[MINIO] Generated cover URL for {portada.ruta}: {cover_url[:80]}...", flush=True)
            except Exception as e:
                print(f"[MINIO] ERROR generating cover URL for {portada.ruta}: {e}", flush=True)
                cover_url = default_url
            cover_title = portada.titulo
        else:
            print(f"[MINIO] No portada found for sitio id={sitio.id} (imagenes count={len(sitio.imagenes)})", flush=True)
            cover_url = default_url
            cover_title = ""
        return cover_url, cover_title, []

    imagenes_data = []
    for img in sitio.imagenes:
        try:
            image_url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket_name, 'Key': img.ruta},
                ExpiresIn=7200,
            )
        except Exception as e:
            print(f"[MINIO] ERROR generating URL for {img.ruta}: {e}", flush=True)
            image_url = default_url

        imagenes_data.append({
            "id": img.id,
            "url": image_url,
            "title": img.titulo,
            "is_cover": img.es_portada
        })

    imagenes_data.sort(key=lambda x: not x["is_cover"])
    cover_url = imagenes_data[0]["url"] if imagenes_data else default_url
    cover_title = imagenes_data[0]["title"] if imagenes_data else ""

    return cover_url, cover_title, imagenes_data
