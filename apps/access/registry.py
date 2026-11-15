"""The permission vocabulary and the default roles (Module 21 §21.2 and §21.3).

Permissions live in code because code has to check them. Roles are data: each
facility gets a copy of the defaults below and can change them freely."""

ACTIONS = {
    "view": "View",
    "create": "Create",
    "edit": "Edit",
    "approve": "Approve",
    "void": "Void",
    "export": "Export or print",
    "assign": "Assign",
    "configure": "Configure",
    "sign": "Sign",
    "dispense": "Dispense",
}

# module code: (label, allowed actions)
MODULES = {
    "patients": ("Patients", ["view", "create", "edit", "export"]),
    "visits": ("Visits and queues", ["view", "create", "edit", "assign"]),
    "nursing": ("Nursing care", ["view", "create", "edit"]),
    "clinical": ("Clinical records", ["view", "create", "edit", "sign"]),
    "prescriptions": ("Prescriptions", ["view", "create", "dispense"]),
    # laboratory: create = request tests, edit = record results, approve = validate results
    "laboratory": ("Laboratory", ["view", "create", "edit", "approve"]),
    "imaging": ("Imaging", ["view", "create", "edit"]),
    "pharmacy": ("Pharmacy stock", ["view", "edit"]),
    "inventory": ("Inventory", ["view", "create", "edit", "approve"]),
    "billing": ("Billing and payments", ["view", "create", "approve", "void", "export"]),
    "insurance": ("Insurance", ["view", "create", "edit", "approve"]),
    "finance": ("Finance", ["view", "create", "approve", "export"]),
    "reports": ("Reports and dashboards", ["view", "export"]),
    "users": ("Staff accounts", ["view", "create", "edit", "assign"]),
    "facilities": ("Facility settings", ["configure"]),
    "access": ("Roles and permissions", ["configure"]),
    "audit": ("Audit trail", ["view"]),
}

PERMISSIONS = [
    (f"{module}.{action}", f"{ACTIONS[action]}: {label}", module, action)
    for module, (label, actions) in MODULES.items()
    for action in actions
]
ALL_CODES = frozenset(code for code, *_ in PERMISSIONS)

# code, name, description, permission codes
DEFAULT_ROLES = [
    ("system_admin", "System Administrator",
     "Manages accounts, roles and settings. Clinical access must be granted separately.",
     ["users.view", "users.create", "users.edit", "users.assign", "facilities.configure", "access.configure"]),
    ("director", "Managing Director",
     "Facility-wide dashboards and approval of designated transactions.",
     ["reports.view", "reports.export", "finance.view", "finance.approve", "billing.view",
      "billing.approve", "inventory.view", "inventory.approve", "visits.view"]),
    ("head_of_department", "Head of Department",
     "Supervises a department, reviews its reports and approves designated requests.",
     ["reports.view", "visits.view", "visits.assign", "inventory.view", "inventory.approve"]),
    ("doctor", "Medical Doctor",
     "Consultations, diagnoses, investigations and prescriptions.",
     ["patients.view", "visits.view", "nursing.view", "clinical.view", "clinical.create",
      "clinical.edit", "clinical.sign", "prescriptions.view", "prescriptions.create",
      "laboratory.view", "laboratory.create", "imaging.view", "imaging.create"]),
    ("nurse", "Nurse",
     "Triage, vital signs, nursing notes and care activities.",
     ["patients.view", "visits.view", "visits.edit", "visits.assign", "nursing.view", "nursing.create",
      "nursing.edit", "clinical.view", "prescriptions.view", "laboratory.view", "pharmacy.view"]),
    ("receptionist", "Receptionist",
     "Registers patients, opens visits, manages queues and records payments.",
     ["patients.view", "patients.create", "patients.edit", "visits.view", "visits.create",
      "visits.edit", "visits.assign", "billing.view", "billing.create", "billing.export"]),
    ("pharmacist", "Pharmacist",
     "Verifies and dispenses prescriptions and manages pharmacy stock.",
     ["patients.view", "prescriptions.view", "prescriptions.dispense", "pharmacy.view",
      "pharmacy.edit", "inventory.view"]),
    ("lab_technician", "Laboratory Technician",
     "Receives test requests, records and validates results.",
     ["patients.view", "laboratory.view", "laboratory.edit", "laboratory.approve"]),
    ("imaging_staff", "Imaging Staff",
     "Manages imaging requests and records findings.",
     ["patients.view", "imaging.view", "imaging.edit"]),
    ("accountant", "Accountant",
     "Invoices, receipts, payments, adjustments and financial reports.",
     ["billing.view", "billing.create", "billing.void", "billing.export", "finance.view",
      "finance.create", "finance.export", "insurance.view", "reports.view", "reports.export"]),
    ("storekeeper", "Storekeeper",
     "Receives, issues and transfers stock.",
     ["inventory.view", "inventory.create", "inventory.edit", "pharmacy.view"]),
    ("insurance_officer", "Insurance Officer",
     "Insurance details, claims and reconciliations.",
     ["patients.view", "billing.view", "insurance.view", "insurance.create", "insurance.edit",
      "insurance.approve"]),
    ("auditor", "Auditor",
     "Reviews transactions and logs without changing anything.",
     ["audit.view", "billing.view", "finance.view", "reports.view", "users.view",
      "insurance.view", "inventory.view"]),
]