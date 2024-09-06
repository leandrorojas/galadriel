enabled = False

def set_log(log:bool):
    global enabled
    enabled = log

def log(message:str, module:str = "", disable_after:bool = False):
    global enabled
    if enabled:
        if (module == ""):
            module = "DEBUG"
        
        print(f"[{module}] " + message)

        enabled = disable_after