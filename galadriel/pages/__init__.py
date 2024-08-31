from .rx_about import rx_tutorial_about_page
from .rx_pricing import rx_tutorial_pricing_page
#from .contact import contact_page
from .rx_protected import rx_tutorial_protected_page
from .auth import login, signup, logout

__all__ = [
    'login',
    'signup',
    'logout',
    'rx_tutorial_about_page',
    #'contact_page',
    'rx_tutorial_pricing_page',
    'rx_tutorial_protected_page'
]