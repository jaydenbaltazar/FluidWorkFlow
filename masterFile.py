import os
import requests
import json

# Klaviyo API Configuration
upload_url = "https://a.klaviyo.com/api/image-upload"
get_image_url = "https://a.klaviyo.com/api/images/"
template_url = "https://a.klaviyo.com/api/templates/"
headers = {
    "accept": "application/json",
    "revision": "2024-10-15",
    "Authorization": "Klaviyo-API-Key APIKEY",  # Replace with your API key
}

# Specify the folder containing the images
folder_path = "/Users/Jayden/Downloads/imagecompressor"  # Replace with your folder path

# Supported image file extensions
supported_extensions = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}

# Get a sorted list of all image files in the folder
image_files = sorted(
    [f for f in os.listdir(folder_path) if os.path.splitext(f)[1].lower() in supported_extensions]
)

# List to store uploaded image URLs
uploaded_image_urls = []

# Step 1: Upload Images
for image_file in image_files:
    file_path = os.path.join(folder_path, image_file)
    print(f"Uploading: {image_file}")
    
    # Open the image file and prepare the payload
    with open(file_path, "rb") as file:
        files = {
            "file": file,
        }
        data = {
            "hidden": "false",
            "name": image_file,  # Use the file name as the image name
        }

        # Send the POST request to upload the image
        response = requests.post(upload_url, data=data, files=files, headers=headers)

    # Check the response and fetch the image URL using the image ID
    if response.status_code == 201:
        response_data = response.json()
        image_id = response_data.get("data", {}).get("id")
        if image_id:
            # Fetch the image URL using the image ID
            image_response = requests.get(f"{get_image_url}{image_id}", headers=headers)
            if image_response.status_code == 200:
                image_url = image_response.json().get("data", {}).get("attributes", {}).get("image_url")
                if image_url:
                    uploaded_image_urls.append(image_url)
                    print(f"Successfully uploaded: {image_file} -> {image_url}")
                else:
                    print(f"Failed to get URL for: {image_file}")
            else:
                print(f"Failed to fetch image details for ID: {image_id}. Status Code: {image_response.status_code}")
        else:
            print(f"Failed to get image ID for: {image_file}")
    else:
        print(f"Failed to upload: {image_file}. Status Code: {response.status_code}")
        print(response.text)

# Step 2: Create Drag-and-Drop Template with Uploaded Images
if uploaded_image_urls:
    print("Creating drag-and-drop template with the uploaded images...")

    # Create HTML content with all the uploaded image URLs using the image block structure
    html_content = f"""
    <!DOCTYPE html>
<html>
<body style="word-spacing:normal;background-color:#f7f7f7;">
    <table align="center" width="600" style="border-spacing: 0; margin: 0 auto; padding: 0; width: 600px;">
        {"".join(f'''
        <tr style="margin: 0; padding: 0;">
            <td style="margin: 0; padding: 0;" data-klaviyo-region="true" data-klaviyo-region-width-pixels="600">
                <div class="klaviyo-block klaviyo-image-block" style="margin: 0; padding: 0;">
                    <img src="{url}" alt="Image {i+1}" style="width: 600px; height: auto; display: block; margin: 0; padding: 0;">
                </div>
            </td>
        </tr>
        ''' for i, url in enumerate(uploaded_image_urls))}
    </table>
</body>
</html>
    """

    # JSON payload for creating the template
    payload = {
        "data": {
            "type": "template",
            "attributes": {
                "name": f"Drag-and-Drop Template with {len(uploaded_image_urls)} Images",
                "editor_type": "USER_DRAGGABLE",  # Set as user-draggable
                "html": html_content,  # HTML with image blocks
                "text": "This is a fallback plain text version of the email.",
            },
        }
    }

    # Send the POST request to create the template
    response = requests.post(template_url, headers={**headers, "content-type": "application/vnd.api+json"}, data=json.dumps(payload))

    # Print the response
    if response.status_code == 201:
        print("Drag-and-drop template created successfully!")
        template_id = response.json().get("data", {}).get("id")
        print(f"Template ID: {template_id}")
    else:
        print("Failed to create the template.")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
else:
    print("No images were uploaded to create a template.")
