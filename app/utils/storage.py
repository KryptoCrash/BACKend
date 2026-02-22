from app.core.database import supabase
from fastapi import UploadFile, HTTPException

def upload_image(device_id: str, filename: str, image: bytes) -> str:
    return supabase.storage.from_("Images").upload(f"{device_id}/{filename}", image)

# Get the actual data of images from the storage
def get_image_data_from_device(device_id: str, num_images: int) -> bytes:
    images = supabase.storage.from_("Images").list(f"{device_id}")
    images_data = [supabase.storage.from_("Images").download(f"{device_id}/{image['name']}") for image in images[:num_images]]
    # Delete other images
    for image in images[num_images:]:
        supabase.storage.from_("Images").delete(f"{device_id}/{image['name']}")
    return images_data