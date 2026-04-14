"""Basic usage examples for the asun C++ pybind11 extension.

API (inference-driven, no manual schema for encoding):
    encode(obj)              → untyped schema text  (shorter; decode gives strings)
    encodeTyped(obj)         → typed schema text    (full round-trip fidelity)
    encodePretty(obj)        → pretty + untyped
    encodePrettyTyped(obj)   → pretty + typed
    encodeBinary(obj)        → bytes (schema inferred internally)
    decode(text)             → dict | list[dict]
    decodeBinary(data, schema) → dict | list[dict]  (schema required for binary)

Current Python support focuses on flat structs / slices with scalar and optional
scalar fields. Legacy map syntax is not supported.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import asun

# ── 1. encodeTyped / decode (typed round-trip) ───────────────────────────────
user = {"id": 1, "name": "Alice", "active": True}

text_typed = asun.encodeTyped(user)
print("encodeTyped:", repr(text_typed))

decoded = asun.decode(text_typed)
print("decode:", decoded)
assert decoded == user, f"round-trip failed: {decoded}"

# ── 2. encode (untyped, shorter output) ──────────────────────────────────────
text_untyped = asun.encode(user)
print("\nencode (untyped):", repr(text_untyped))
# NOTE: untyped decode gives strings for numeric/bool fields
# Use encodeTyped for full value-type fidelity

# ── 3. Slice — encodeTyped / decode ──────────────────────────────────────────
users = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
    {"id": 3, "name": "Carol"},
]
slice_text = asun.encodeTyped(users)
print("\nencodeTyped slice:\n" + slice_text)

decoded_users = asun.decode(slice_text)
print("decode slice:", decoded_users)
assert decoded_users == users

# ── 4. encodePrettyTyped (pretty + typed, full round-trip) ───────────────────
pretty = asun.encodePrettyTyped(users)
print("\nencodePrettyTyped:\n" + pretty)
assert asun.decode(pretty) == users

# ── 5. encodeBinary / decodeBinary ───────────────────────────────────────────
# Schema is inferred internally for encode; schema required for decode
data = asun.encodeBinary(users)
print(f"encodeBinary: {len(data)} bytes")

# binary wire format has no embedded types — schema must be explicit for decode
SCHEMA = "[{id@int, name@str}]"
restored = asun.decodeBinary(data, SCHEMA)
print("decodeBinary:", restored)
assert restored == users

# ── 6. Optional fields (null ⇒ inferred str?) ────────────────────────────────
rows = [{"id": 1, "note": "present"}, {"id": 2, "note": None}]
opt_text = asun.encodeTyped(rows)
print("\noptional encodeTyped:", repr(opt_text))
out = asun.decode(opt_text)
print("optional decode:", out)
assert out == rows

print("\nAll basic examples passed.")
