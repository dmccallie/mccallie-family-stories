# image utilities for Stories app
from io import BytesIO
from PIL import Image as PilImage, ExifTags
from django.core.files.base import ContentFile

def resize_and_reorient_image(image, max_size=(1500, 1500), quality=70):
    # use Pillow to resize and re-orient the image before saving
    # NOTE that "image" is an in-memory file object 
    #  extracted from a Django request.FILES dictionary
    #  image = request.FILES['image']
    # returns a Django in-memory ContentFile object

    pil_image = PilImage.open(image)

    # grab format before rotations which mess it up?
    # MPO format seems to get handled as JPEG
    image_format = pil_image.format

    # Handle EXIF orientation data
    try:
        exif = pil_image._getexif() # type: ignore
        if exif is not None:
            exif = dict(exif.items())
            # print("found exif: ", exif)
            orientation = None
            for tag, value in exif.items():
                if ExifTags.TAGS.get(tag) == 'Orientation':
                    orientation = value
                    break
            # print("found orientation: ", orientation)   
            if orientation == 3:
                pil_image = pil_image.rotate(180, expand=True)
            elif orientation == 6:
                pil_image = pil_image.rotate(270, expand=True)
            elif orientation == 8:
                pil_image = pil_image.rotate(90, expand=True)
    
    except (AttributeError, KeyError, IndexError):
        # Cases: image doesn't have getexif or no EXIF data
        # print(f"NOTE - image {image} has no exif data")
        pass
    
    # Resize the image
    pil_image.thumbnail(max_size)

    # remap the image to a BytesIO object
    img_io = BytesIO()

    if image_format == 'JPEG':
        pil_image.save(img_io, format='JPEG', quality=quality)
    else:
        pil_image.save(img_io, format=image_format)
    
    # Create a Django ContentFile (in memory file) from the BytesIO object
    image_file = ContentFile(img_io.getvalue(), name=image.name)

    # return the ContentFile object (to be added to a Model, or ...)
    return image_file