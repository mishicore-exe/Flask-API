import cloudinary 
import cloudinary.uploader
from send_email import email

Cloud_Name="ajklkyxy"
Api_Key="496387888836798"
Secret_Key="8hXaQlqJSz3HqXqrlIWu0WfnTDk"

# connecting to cloudinary
cloudinary.config(
    cloud_name=Cloud_Name,
    api_key=Api_Key,
    api_secret=Secret_Key
)
print("cloudinary configuration successful")

def upload_pdf(pdf_file):
    try:
        file_path = f"receipts/{pdf_file}.pdf"
        # upload pdf
        upload = cloudinary.uploader.upload(file_path, resource_type="raw")
        receipt_url = upload["secure_url"]

        print("successful cloudinary upload") 
        print(receipt_url)
        # send email
        email("mitchellewanjohi69@gmail.com","Successful Payment",f"Thankyou,we have rceived your payment.\n\n"f"Receipt:{receipt_url}")
        return "success"

    except Exception as e:
        print(f"upload failed: {e}")
        return "failed"