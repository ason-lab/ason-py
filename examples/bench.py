from __future__ import annotations

"""ASON Python benchmark.

Output style follows the repository's JSON / ASON / BIN comparison format.
The Python extension currently benchmarks flat structs and flat record slices.
"""

import json
import os
import platform
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import ason


_NAMES = ["Alice", "Bob", "Carol", "David", "Eve", "Frank", "Grace", "Hank"]
_ROLES = ["engineer", "designer", "manager", "analyst"]
_CITIES = ["NYC", "LA", "Chicago", "Houston", "Phoenix"]

FLAT_SCHEMA_BIN = "[{id@int,name@str,email@str,age@int,score@float,active@bool,role@str,city@str}]"
ALL_TYPES_SCHEMA_BIN = "[{b@bool,iv@int,pv@int,fv@float,sv@str,oi@int?,os@str?}]"
SINGLE_SCHEMA_BIN = "{id@int,name@str,email@str,age@int,score@float,active@bool,role@str,city@str}"


def compact_json(value) -> bytes:
    return json.dumps(value, separators=(",", ":"), ensure_ascii=False).encode()


def bench(fn, iterations: int) -> float:
    start = time.perf_counter_ns()
    for _ in range(iterations):
        fn()
    return (time.perf_counter_ns() - start) / 1e6


def format_ratio(base_ms: float, target_ms: float) -> str:
    if target_ms <= 0:
        return "infx"
    ratio = base_ms / target_ms
    text = f"{ratio:.1f}".rstrip("0").rstrip(".")
    return f"{text}x"


def format_percent(part: int, whole: int) -> str:
    if whole <= 0:
        return "0%"
    text = f"{part * 100.0 / whole:.1f}".rstrip("0").rstrip(".")
    return f"{text}%"


def print_section(title: str, width: int = 68) -> None:
    line = "─" * (width - 2)
    print(f"┌{line}┐")
    print(f"│ {title:<{width - 4}} │")
    print(f"└{line}┘")


def print_result(
    name: str,
    json_ser_ms: float,
    ason_ser_ms: float,
    bin_ser_ms: float,
    json_de_ms: float,
    ason_de_ms: float,
    bin_de_ms: float,
    json_bytes: int,
    ason_bytes: int,
    bin_bytes: int,
) -> None:
    print(f"  {name}")
    print(
        f"    Serialize:   JSON {json_ser_ms:8.2f}ms/{json_bytes}B | "
        f"ASON {ason_ser_ms:8.2f}ms({format_ratio(json_ser_ms, ason_ser_ms)})/{ason_bytes}B({format_percent(ason_bytes, json_bytes)}) | "
        f"BIN {bin_ser_ms:8.2f}ms({format_ratio(json_ser_ms, bin_ser_ms)})/{bin_bytes}B({format_percent(bin_bytes, json_bytes)})"
    )
    print(
        f"    Deserialize: JSON {json_de_ms:8.2f}ms | "
        f"ASON {ason_de_ms:8.2f}ms({format_ratio(json_de_ms, ason_de_ms)}) | "
        f"BIN {bin_de_ms:8.2f}ms({format_ratio(json_de_ms, bin_de_ms)})"
    )


def make_users(n: int) -> list[dict]:
    return [
        {
            "id": i,
            "name": _NAMES[i % len(_NAMES)],
            "email": f"{_NAMES[i % len(_NAMES)].lower()}@example.com",
            "age": 25 + i % 40,
            "score": 50.0 + (i % 50) + 0.5,
            "active": i % 3 != 0,
            "role": _ROLES[i % len(_ROLES)],
            "city": _CITIES[i % len(_CITIES)],
        }
        for i in range(n)
    ]


def make_all_types(n: int) -> list[dict]:
    return [
        {
            "b": i % 2 == 0,
            "iv": -(i * 100_000),
            "pv": i * 1_000_000 + 7,
            "fv": float(i) * 0.25 + 0.5,
            "sv": f"item_{i}",
            "oi": i if i % 2 == 0 else None,
            "os": None,
        }
        for i in range(n)
    ]


def run_case(name: str, value, binary_schema: str, iterations: int) -> None:
    json_data = compact_json(value)
    ason_text = ason.encodeTyped(value)
    bin_data = ason.encodeBinary(value)

    json_ser_ms = bench(lambda: compact_json(value), iterations)
    ason_ser_ms = bench(lambda: ason.encodeTyped(value), iterations)
    bin_ser_ms = bench(lambda: ason.encodeBinary(value), iterations)

    json_de_ms = bench(lambda: json.loads(json_data), iterations)
    ason_de_ms = bench(lambda: ason.decode(ason_text), iterations)
    bin_de_ms = bench(lambda: ason.decodeBinary(bin_data, binary_schema), iterations)

    print_result(
        name,
        json_ser_ms,
        ason_ser_ms,
        bin_ser_ms,
        json_de_ms,
        ason_de_ms,
        bin_de_ms,
        len(json_data),
        len(ason_text.encode()),
        len(bin_data),
    )


def run_flat_section() -> None:
    print_section("Section 1: Flat Struct (8 fields)")
    for count, iterations in [(100, 100), (500, 100), (1000, 100), (5000, 20)]:
        run_case(f"Flat struct × {count} (8 fields, vec)", make_users(count), FLAT_SCHEMA_BIN, iterations)
        print()


def run_all_types_section() -> None:
    print_section("Section 2: All-Types Struct (7 fields)")
    for count, iterations in [(100, 100), (500, 100)]:
        run_case(
            f"All-types struct × {count} (7 fields, optional)",
            make_all_types(count),
            ALL_TYPES_SCHEMA_BIN,
            iterations,
        )
        print()


def run_single_section() -> None:
    print_section("Section 3: Single Struct Roundtrip")
    run_case("Single struct × 10000 (8 fields)", make_users(1)[0], SINGLE_SCHEMA_BIN, 10_000)
    print()


def run_large_payload_section() -> None:
    print_section("Section 4: Large Payload (10k records)")
    run_case("Large payload × 10000 (8 fields, vec)", make_users(10_000), FLAT_SCHEMA_BIN, 10)
    print()


def run_throughput_section() -> None:
    print_section("Section 5: Throughput Summary")
    rows = make_users(1000)
    json_data = compact_json(rows)
    ason_text = ason.encodeTyped(rows)
    bin_data = ason.encodeBinary(rows)
    iterations = 100
    total_records = len(rows) * iterations

    json_ser_ms = bench(lambda: compact_json(rows), iterations)
    ason_ser_ms = bench(lambda: ason.encodeTyped(rows), iterations)
    bin_ser_ms = bench(lambda: ason.encodeBinary(rows), iterations)
    json_de_ms = bench(lambda: json.loads(json_data), iterations)
    ason_de_ms = bench(lambda: ason.decode(ason_text), iterations)
    bin_de_ms = bench(lambda: ason.decodeBinary(bin_data, FLAT_SCHEMA_BIN), iterations)

    json_ser_rps = total_records / (json_ser_ms / 1000.0)
    ason_ser_rps = total_records / (ason_ser_ms / 1000.0)
    bin_ser_rps = total_records / (bin_ser_ms / 1000.0)
    json_de_rps = total_records / (json_de_ms / 1000.0)
    ason_de_rps = total_records / (ason_de_ms / 1000.0)
    bin_de_rps = total_records / (bin_de_ms / 1000.0)

    print(f"  Serialize throughput:   JSON {json_ser_rps:12,.0f} rec/s | ASON {ason_ser_rps:12,.0f} rec/s | BIN {bin_ser_rps:12,.0f} rec/s")
    print(f"  Deserialize throughput: JSON {json_de_rps:12,.0f} rec/s | ASON {ason_de_rps:12,.0f} rec/s | BIN {bin_de_rps:12,.0f} rec/s")
    ason_bytes = len(ason_text.encode())
    print(f"  Size baseline (1k rows): JSON {len(json_data)}B | ASON {ason_bytes}B({format_percent(ason_bytes, len(json_data))}) | BIN {len(bin_data)}B({format_percent(len(bin_data), len(json_data))})")
    print()


def main() -> None:
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║               ASON Python vs JSON Benchmark                  ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print(f"\nSystem: {platform.system()} {platform.machine()} | Python {platform.python_version()}")
    print("Mode: compact JSON vs typed ASON text vs ASON binary")
    print("Scope: flat structs / flat record slices supported by ason-py")
    print()

    run_flat_section()
    run_all_types_section()
    run_single_section()
    run_large_payload_section()
    run_throughput_section()

    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                    Benchmark Complete                        ║")
    print("╚══════════════════════════════════════════════════════════════╝")


if __name__ == "__main__":
    main()
