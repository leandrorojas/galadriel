"""
to use this module, you first need to import it, of course
then use the folowing sequence:
debug.set_log(False)
debug.set_module("<module_name>")
debug.log("<message>")

end a log with True to finish the logging
debug.log("<message>", True)
"""

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