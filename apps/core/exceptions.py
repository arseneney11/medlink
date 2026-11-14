class HardDeleteNotAllowed(Exception):
    """Raised when code tries to permanently delete a clinical or financial record."""