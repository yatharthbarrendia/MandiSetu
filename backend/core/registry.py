"""Module Registry for MandiSetu Platform.

Each module registers its:
- id: unique identifier
- folder: physical folder name on disk (e.g., Module_01_User_Roles)
- router_import: python import path to the APIRouter instance
- static_mount: URL slug mounted under /modules/<static_mount>/
- tags: OpenAPI documentation tags
- enabled: whether the module is currently active
"""
import importlib
from typing import List, Dict, Any
from fastapi import APIRouter

MODULE_REGISTRY: List[Dict[str, Any]] = [
    {
        "id": "module_01",
        "name": "User & Role Management",
        "folder": "Module_01_User_Roles",
        "router_import": "Module_01_User_Roles.backend.router",
        "static_mount": "module-01",
        "tags": ["Module 01: User & Role Management"],
        "enabled": True,
    },
    {
        "id": "module_02",
        "name": "Price Discovery & Trend Engine",
        "folder": "Module_02_Price_Discovery",
        "router_import": "Module_02_Price_Discovery.backend.router",
        "static_mount": "module-02",
        "tags": ["Module 02: Price Discovery"],
        "enabled": False,
    },
    {
        "id": "module_03",
        "name": "Net-Realization Calculator",
        "folder": "Module_03_Net_Realization",
        "router_import": "Module_03_Net_Realization.backend.router",
        "static_mount": "module-03",
        "tags": ["Module 03: Net Realization"],
        "enabled": False,
    },
    {
        "id": "module_04",
        "name": "Produce Listing / Lot Creation",
        "folder": "Module_04_Produce_Listing",
        "router_import": "Module_04_Produce_Listing.backend.router",
        "static_mount": "module-04",
        "tags": ["Module 04: Produce Listing"],
        "enabled": False,
    },
    {
        "id": "module_05",
        "name": "Matching & Digital Offers",
        "folder": "Module_05_Matching_Offers",
        "router_import": "Module_05_Matching_Offers.backend.router",
        "static_mount": "module-05",
        "tags": ["Module 05: Matching & Offers"],
        "enabled": False,
    },
    {
        "id": "module_06",
        "name": "Transaction Tracking",
        "folder": "Module_06_Transactions",
        "router_import": "Module_06_Transactions.backend.router",
        "static_mount": "module-06",
        "tags": ["Module 06: Transactions"],
        "enabled": False,
    },
    {
        "id": "module_07",
        "name": "Sale-Window Recommendation",
        "folder": "Module_07_Sale_Window",
        "router_import": "Module_07_Sale_Window.backend.router",
        "static_mount": "module-07",
        "tags": ["Module 07: Sale Window"],
        "enabled": False,
    },
    {
        "id": "module_08",
        "name": "Buyer Verification & Reliability",
        "folder": "Module_08_Buyer_Trust",
        "router_import": "Module_08_Buyer_Trust.backend.router",
        "static_mount": "module-08",
        "tags": ["Module 08: Buyer Trust"],
        "enabled": False,
    },
    {
        "id": "module_09",
        "name": "Logistics Coordination",
        "folder": "Module_09_Logistics",
        "router_import": "Module_09_Logistics.backend.router",
        "static_mount": "module-09",
        "tags": ["Module 09: Logistics"],
        "enabled": False,
    },
    {
        "id": "module_10",
        "name": "Dispute Resolution",
        "folder": "Module_10_Disputes",
        "router_import": "Module_10_Disputes.backend.router",
        "static_mount": "module-10",
        "tags": ["Module 10: Dispute Resolution"],
        "enabled": False,
    },
    {
        "id": "module_11",
        "name": "Quality Grading (MobileNet)",
        "folder": "Module_11_Quality_Grading",
        "router_import": "Module_11_Quality_Grading.backend.router",
        "static_mount": "module-11",
        "tags": ["Module 11: Quality Grading"],
        "enabled": False,
    },
    {
        "id": "module_12",
        "name": "Weather Risk Advisory",
        "folder": "Module_12_Weather_Risk",
        "router_import": "Module_12_Weather_Risk.backend.router",
        "static_mount": "module-12",
        "tags": ["Module 12: Weather Risk"],
        "enabled": False,
    },
    {
        "id": "module_13",
        "name": "Admin Analytics Dashboard",
        "folder": "Module_13_Admin_Analytics",
        "router_import": "Module_13_Admin_Analytics.backend.router",
        "static_mount": "module-13",
        "tags": ["Module 13: Admin Analytics"],
        "enabled": False,
    },
]

def get_active_routers() -> List[tuple[APIRouter, Dict[str, Any]]]:
    """Dynamically load and return active routers according to registry configuration."""
    active = []
    for item in MODULE_REGISTRY:
        if not item.get("enabled", False):
            continue
        try:
            mod = importlib.import_module(item["router_import"])
            router = getattr(mod, "router", None)
            if router:
                active.append((router, item))
        except (ImportError, AttributeError) as exc:
            print(f"[Registry] Skipping {item['id']} ({item['name']}): {exc}")
    return active
