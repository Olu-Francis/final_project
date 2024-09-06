import phonenumbers
from phonenumbers import *


def process_phone_number(raw_phone_number, default_region='NG'):
    try:
        # Parse the phone number
        phone_number = phonenumbers.parse(raw_phone_number, default_region)

        # Validate and format the phone number
        if not phonenumbers.is_valid_number(phone_number):
            raise ValueError("Invalid phone number")

        return phonenumbers.format_number(phone_number, PhoneNumberFormat.E164)
    except NumberParseException as e:
        raise ValueError(f"Error parsing phone number: {e}")
