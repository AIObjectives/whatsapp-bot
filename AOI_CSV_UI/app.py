



from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests
import uvicorn

app = FastAPI()

# Jinja2 templates directory
templates = Jinja2Templates(directory="templates")

# Hardcoded password for validation
HARD_CODED_PASSWORD = "xxx"

# AWS API Gateway template
AWS_API_URL_TEMPLATE = "xxx/default/AOI_AdvacedCSVExtraxtion3_10?email={email}&collections={collection}"

# Route to serve the HTML form
@app.get("/", response_class=HTMLResponse)
async def show_form(request: Request):
    return templates.TemplateResponse("style_final.html", {"request": request})

# Route to handle form submission
@app.post("/submit")
async def handle_form_submission(
    request: Request,
    email: str = Form(...),
    username: str = Form(...),
    password: str = Form(...)
):
    # Validate the password
    if password != HARD_CODED_PASSWORD:
        return templates.TemplateResponse(
            "style_final.html", 
            {"request": request, "error_message": "Invalid password, please try again."}
        )

    # Create collection name based on username
    collection_name = username

    # Format the API URL with the provided email and collection name
    api_url = AWS_API_URL_TEMPLATE.format(email=email, collection=collection_name)

    # Make the GET request to the AWS API
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an error for failed requests

        # If successful, inform the user
        if response.status_code == 200:
            success_message = "API triggered successfully. Check your email for the CSV file."
            return templates.TemplateResponse(
                "style_final.html", 
                {"request": request, "success_message": success_message}
            )
        else:
            error_message = f"Failed to trigger API: {response.status_code} - {response.text}"
            return templates.TemplateResponse(
                "style_final.html", 
                {"request": request, "error_message": error_message}
            )

    except requests.exceptions.RequestException as e:
        error_message = f"Error contacting API: {str(e)}"
        return templates.TemplateResponse(
            "style_final.html", 
            {"request": request, "error_message": error_message}
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
