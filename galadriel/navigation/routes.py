#galadriel
import reflex_local_auth

#auth
LOGIN = reflex_local_auth.routes.LOGIN_ROUTE
SIGNUP = reflex_local_auth.routes.REGISTER_ROUTE
LOGOUT = "/logout"

HOME = "/"
ABOUT = "/about"

#suites
SUITES = "/suites"
SUITE_ADD = "/suites/add"
SUITE_DETAIL = "/suites/[id]"
SUITE_EDIT = "/suites/[id]/edit"

#scenarios
SCENARIOS = "/scenarios"
SCENARIO_ADD = "/scenarios/add"
SCENARIO_DETAIL = "/scenarios/[id]"
SCENARIO_EDIT = "/scenarios/[id]/edit"

#cases
CASES = "/cases"
CASE_ADD = "/cases/add"
CASE_DETAIL = "/cases/[id]"
CASE_EDIT = "/cases/[id]/edit"

#cycles
CYCLES = "/cycles"
CYCLE_ADD = "/cycles/add"
# CYCLE_DETAIL = "/cycles/[id]"
# CYCLE_EDIT = "/cycles/[id]/edit"