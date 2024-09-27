import azure.functions as func
import logging

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

def install_playwright_browsers():
    import subprocess
    subprocess.run(["playwright", "install", "chromium"], check=True)

def send_whatsapp_message(phone_number, message):
    from playwright.sync_api import sync_playwright
    import time

    try:
        with sync_playwright() as p:
            try:
                install_playwright_browsers()
                browser = p.chromium.launch_persistent_context(user_data_dir="whatsapp_data", headless=False)
            except Exception as e:
                logging.error(f"Error launching browser: {e}")
                logging.info("Attempting to install Playwright browsers...")
                install_playwright_browsers()
                browser = p.chromium.launch_persistent_context(user_data_dir="whatsapp_data", headless=False)

            page = browser.new_page()
            whatsapp_url = f"https://web.whatsapp.com/send?phone={phone_number}&text={message}"
            page.goto(whatsapp_url)
            page.wait_for_load_state("networkidle")
            if "Escanea el código QR" in page.content():
                logging.info("Escanea el código QR de WhatsApp Web")
                time.sleep(15)
            try:
                # page.wait_for_selector("div[data-tab='1']", timeout=60000)
                time.sleep(15)
                page.keyboard.press("Enter")
                time.sleep(10)
            except Exception as e:
                logging.error(f"Error sending message: {e}")
            finally:
                browser.close()
    except Exception as e:
        logging.error(f"Error in send_whatsapp_message: {e}")


@app.route(route="rpawb6")
def rpawb6(req: func.HttpRequest) -> func.HttpResponse:
    cel = req.params.get('cel')
    message = req.params.get('message')

    logging.info('Python HTTP trigger function processed a request.')
    
    if not cel or not message:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            cel = req_body.get('cel')
            message = req_body.get('message')

    if cel and message:
        send_whatsapp_message(cel, message)
        return func.HttpResponse(f"Message sent to {cel}")
    else:
        return func.HttpResponse(
            "Please pass a phone_number and message on the query string or in the request body",
            status_code=400
        )