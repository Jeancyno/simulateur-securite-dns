from ..models import TrustAnchor


class TrustAnchorManager:
    @staticmethod
    def get_root_anchor():
        return TrustAnchor.objects.filter(name=".", is_active=True).first()

    @staticmethod
    def get_anchor(name):
        return TrustAnchor.objects.filter(name=name, is_active=True).first()

    @staticmethod
    def get_all_anchors():
        return TrustAnchor.objects.filter(is_active=True)

    @staticmethod
    def initialize_root_anchor():
        root_key = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAu9sMpP6w0Zy8rV2nXpXn
qgP1rVZYbYw5jZRsQdQ2YRZQZ2vM0iQxOMyR5ZxXqZ5QJkR7QxOMyR5ZxXqZ5QJkR
7QxOMyR5ZxXqZ5QJkR7QxOMyR5ZxXqZ5QJkR7QxOMyR5ZxXqZ5QJkR7QxOMyR5ZxX
qZ5QJkR7QxOMyR5ZxXqZ5QJkR7QxOMyR5ZxXqZ5QJkR7QxOMyR5ZxXqZ5QJkR7Qx
OMyR5ZxXqZ5QJkR7QxOMyR5ZxXqZ5QJkR7QxOMyR5ZxXqZ5QJkR7QxOMyR5ZxXq
Z5QIDAQAB
-----END PUBLIC KEY-----"""

        return TrustAnchor.objects.get_or_create(
            name=".",
            key_tag=19036,
            algorithm=8,
            defaults={"public_key": root_key, "is_active": True}
        )