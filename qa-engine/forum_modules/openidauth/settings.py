OPENID_SREG = {
    "required": "nickname, email",
    "optional": "postcode, country",
    "policy_url": ""
}
OPENID_AX = [
            {"type_uri": "http://axschema.org/contact/email", "count": 1, "required": True, "alias": "email"},
            {"type_uri": "fullname", "count":1 , "required": False, "alias": "fullname"}
        ]