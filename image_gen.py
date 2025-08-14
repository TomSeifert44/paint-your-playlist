from openai import OpenAI
import base64
import os

secret_key = os.environ.get("SECRET_KEY")


client = OpenAI(api_key=secret_key)

from datetime import datetime
import requests

timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

def generate_image(prompt):
	result = client.images.generate(
	    model="dall-e-3",
	    prompt=prompt,
	    size="1024x1024",
	    quality="standard",
	    n=1
	)

	# Step 2: Get image URL
	image_url = result.data[0].url

	# Step 3: Download the image using requests
	image_data = requests.get(image_url).content

	# Save the image to a file
	with open("/tmp/output.png", "wb") as f:
	    f.write(image_data)

	#with open(f"image_archive/output_{timestamp}.png", "wb") as f:
		#f.write(image_data)

	print(prompt)

	return True

