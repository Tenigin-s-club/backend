

def status_200(details: str | dict | list | None = None):
    if details:
        return {"status": "success", "details": details}
    
    return {"status": "success"}