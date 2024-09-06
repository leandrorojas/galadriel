enabled = False
global_module = ""

def set_log(log:bool):
    global enabled
    enabled = log

def set_module(module:str):
    global global_module
    global_module = module

def log(message:str, final_log:bool = False):
    global enabled
    global global_module
    
    if enabled:
        if (global_module == ""):
            module = "DEBUG"
        
        print(f"[{module}] " + message)

        enabled = final_log
        if final_log: global_module = ""