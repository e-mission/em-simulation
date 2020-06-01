class Error(Exception):
    pass 

class AddressNotFoundError(Error):
    """ Exception raised for Addresses that are not found in the trip planner client.
    """
    def __init__(self, message, address):
        self.message = message
        self.address = address 

class EmailNotFoundInFileName(Error):
    """ Exception raised when the file to load has an invalid file name
    """

    def __init__(self, invalid_file_name):
        self.invalid_file_name = invalid_file_name
