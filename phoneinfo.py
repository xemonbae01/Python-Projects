from flask import Flask, request, jsonify
import phonenumbers
from phonenumbers import geocoder, carrier, number_type, timezone, is_valid_number, region_code_for_number
import ipaddress

app = Flask(__name__)

# Country short name to country code map
COUNTRY_CODES = {
    'bd': '+880',
    'us': '+1',
    'in': '+91',
    'uk': '+44',
    'ca': '+1',
    'pk': '+92',
    'au': '+61',
    'fr': '+33',
    'de': '+49',
    'np': '+977'
    # Add more if needed I'm just lazy to add but there's lot so i know you'll add with your needs
}

# Country short name to region (ISO Alpha-2)
REGION_CODES = {
    'bd': 'BD',
    'us': 'US',
    'in': 'IN',
    'uk': 'GB',
    'ca': 'CA',
    'pk': 'PK',
    'au': 'AU',
    'fr': 'FR',
    'de': 'DE',
    'np': 'NP'
}

@app.route('/analyze', methods=['GET'])
def analyze_number():
    number = request.args.get('number')
    country_type = request.args.get('type')  # like 'bd', 'us', etc.

    if not number:
        return jsonify({"error": "Missing 'number' query parameter"}), 400

    # Normalize number with country code if type= is provided
    if not number.startswith('+') and country_type and country_type.lower() in COUNTRY_CODES:
        number = COUNTRY_CODES[country_type.lower()] + number

    try:
        # Determine default region
        if number.startswith('+'):
            parsed = phonenumbers.parse(number, None)
        elif country_type and country_type.lower() in REGION_CODES:
            parsed = phonenumbers.parse(number, REGION_CODES[country_type.lower()])
        else:
            parsed = phonenumbers.parse(number, 'US')  # fallback

        if not is_valid_number(parsed):
            return jsonify({"error": "Invalid phone number"}), 400

        country = geocoder.description_for_number(parsed, "en")
        sim_carrier = carrier.name_for_number(parsed, "en")
        sim_type = number_type(parsed)
        time_zone = timezone.time_zones_for_number(parsed)
        country_code = parsed.country_code
        number_length = len(str(parsed.national_number))
        region = region_code_for_number(parsed)
        area_code = str(parsed.national_number)[:3]
        prefix = str(parsed.national_number)[:4]

        sim_type_info = "Prepaid" if sim_carrier.lower() in ["vodafone", "airtel", "jio", "robi", "grameenphone", "banglalink"] else "Postpaid"
        call_type = "ISD" if parsed.country_code != 91 else "STD"

        types = {
            0: "FIXED_LINE",
            1: "MOBILE",
            2: "FIXED_LINE_OR_MOBILE",
            3: "TOLL_FREE",
            4: "PREMIUM_RATE",
            5: "SHARED_COST",
            6: "VOIP",
            7: "PERSONAL_NUMBER",
            8: "PAGER",
            9: "UAN",
            10: "VOICEMAIL",
            27: "UNKNOWN"
        }

        response = {
            "location": country,
            "carrier": sim_carrier,
            "type": types.get(sim_type, "UNKNOWN"),
            "time_zone": time_zone,
            "international_format": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
            "national_format": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL),
            "country_code": country_code,
            "number_length": number_length,
            "valid_number": True,
            "region_code": region,
            "area_code": area_code,
            "prefix": prefix,
            "sim_type": sim_type_info,
            "call_type": call_type,
            "carrier_validity": f"Carrier {sim_carrier} seems valid.",
            "international_roaming": "Check with carrier for roaming status.",
            "risk_score": "Not available",
            "spam_report": "Not available",
            "data_breach_info": "Not available"
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
from flask import Flask, request, jsonify
import phonenumbers
from phonenumbers import geocoder, carrier, number_type, timezone, is_valid_number, region_code_for_number
import ipaddress

app = Flask(__name__)

# Country short name to country code map
COUNTRY_CODES = {
    'bd': '+880',
    'us': '+1',
    'in': '+91',
    'uk': '+44',
    'ca': '+1',
    'pk': '+92',
    'au': '+61',
    'fr': '+33',
    'de': '+49',
    'np': '+977'
    # Add more if needed
}

# Country short name to region (ISO Alpha-2)
REGION_CODES = {
    'bd': 'BD',
    'us': 'US',
    'in': 'IN',
    'uk': 'GB',
    'ca': 'CA',
    'pk': 'PK',
    'au': 'AU',
    'fr': 'FR',
    'de': 'DE',
    'np': 'NP'
}

@app.route('/analyze', methods=['GET'])
def analyze_number():
    number = request.args.get('number')
    country_type = request.args.get('type')  # like 'bd', 'us', etc.

    if not number:
        return jsonify({"error": "Missing 'number' query parameter"}), 400

    # Normalize number with country code if type= is provided
    if not number.startswith('+') and country_type and country_type.lower() in COUNTRY_CODES:
        number = COUNTRY_CODES[country_type.lower()] + number

    try:
        # Determine default region
        if number.startswith('+'):
            parsed = phonenumbers.parse(number, None)
        elif country_type and country_type.lower() in REGION_CODES:
            parsed = phonenumbers.parse(number, REGION_CODES[country_type.lower()])
        else:
            parsed = phonenumbers.parse(number, 'US')  # fallback

        if not is_valid_number(parsed):
            return jsonify({"error": "Invalid phone number"}), 400

        country = geocoder.description_for_number(parsed, "en")
        sim_carrier = carrier.name_for_number(parsed, "en")
        sim_type = number_type(parsed)
        time_zone = timezone.time_zones_for_number(parsed)
        country_code = parsed.country_code
        number_length = len(str(parsed.national_number))
        region = region_code_for_number(parsed)
        area_code = str(parsed.national_number)[:3]
        prefix = str(parsed.national_number)[:4]

        sim_type_info = "Prepaid" if sim_carrier.lower() in ["vodafone", "airtel", "jio", "robi", "grameenphone", "banglalink"] else "Postpaid"
        call_type = "ISD" if parsed.country_code != 91 else "STD"

        types = {
            0: "FIXED_LINE",
            1: "MOBILE",
            2: "FIXED_LINE_OR_MOBILE",
            3: "TOLL_FREE",
            4: "PREMIUM_RATE",
            5: "SHARED_COST",
            6: "VOIP",
            7: "PERSONAL_NUMBER",
            8: "PAGER",
            9: "UAN",
            10: "VOICEMAIL",
            27: "UNKNOWN"
        }

        response = {
            "location": country,
            "carrier": sim_carrier,
            "type": types.get(sim_type, "UNKNOWN"),
            "time_zone": time_zone,
            "international_format": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
            "national_format": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL),
            "country_code": country_code,
            "number_length": number_length,
            "valid_number": True,
            "region_code": region,
            "area_code": area_code,
            "prefix": prefix,
            "sim_type": sim_type_info,
            "call_type": call_type,
            "carrier_validity": f"Carrier {sim_carrier} seems valid.",
            "international_roaming": "Check with carrier for roaming status.",
            "risk_score": "Not available",
            "spam_report": "Not available",
            "data_breach_info": "Not available"
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
