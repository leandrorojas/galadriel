enabled = True

def log(message:str, module:str = ""):
    global enabled
    if enabled:
        if (module == ""):
            module = "DEBUG"
        
        print(f"[{module}] " + message)