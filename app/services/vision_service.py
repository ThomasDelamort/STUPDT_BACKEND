import base64
import json
import logging
import re
import struct
from typing import Optional, Dict, Any, List
import httpx
from app.config import settings

logger = logging.getLogger(__name__)

GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"

SAMPLE_CATALOG = {
    "rock": {
        "label": "Photo of a Rock",
        "category": "Geological Object",
        "detectedItem": "Standard Terrestrial Rock",
        "variants": [
            {
                "detectedItem": "Certified Geological Stone",
                "category": "Departmental Mineral Asset",
                "confidence": "100.00%",
                "verdict": "After convening 14 Geological AI Specialists, our committee certifies this rock is undeniably a rock. It has not moved.",
                "ingredients": ["100% Compressed Silicon Dioxide", "Zero Ambition", "Ancient Gravity"],
                "proTip": "Geological Warning: If dropped, the rock will fall downwards due to corporate gravity guidelines."
            },
            {
                "detectedItem": "Sedimentary Inaction Unit",
                "category": "Passive Geological Device",
                "confidence": "100.00%",
                "verdict": "Our mineralogical sensors detect zero thoughts, zero deliverables, and 100% mineral mass.",
                "ingredients": ["Granite Matrix", "Unpaid Overtime Dust", "Erosion Immunity"],
                "proTip": "Pro-tip: This rock has completed the same number of customer tickets as Department #001 today (0)."
            }
        ]
    },
    "spaghetti": {
        "label": "Plate of Spaghetti",
        "category": "Culinary Dish",
        "detectedItem": "Al Dente Wheat Strands",
        "variants": [
            {
                "detectedItem": "Pure Spaghetti Entity",
                "category": "Carbohydrate Topology",
                "confidence": "100.00%",
                "verdict": "After exhaustive spectral food analysis, we are 100% confident this plate of spaghetti is tangled spaghetti.",
                "ingredients": ["Cooked Semolina Strands", "Red Sauce Synergies", "Fork Friction"],
                "proTip": "Recipe tip: To make spaghetti, acquire spaghetti. Allergen warning: Contains pure spaghetti."
            },
            {
                "detectedItem": "Pasta Pipeline Architecture",
                "category": "Edible Code Base",
                "confidence": "100.00%",
                "verdict": "Our Vision AI has confirmed that this spaghetti matches our legacy codebase architecture with 99.98% topological similarity.",
                "ingredients": ["Intertwined Carbohydrates", "Tomato Bureaucracy", "Paralytic Gluten"],
                "proTip": "Synergy tip: Do not attempt to refactor the noodles; any change may crash our production servers."
            }
        ]
    },
    "water": {
        "label": "Glass of Water",
        "category": "Liquid Substance",
        "detectedItem": "Aqueous Hydration Molecule",
        "variants": [
            {
                "detectedItem": "Certified Wet Water",
                "category": "Transparent Fluid Vehicle",
                "confidence": "100.00%",
                "verdict": "Our Hydration Verification Board confirms with 100.00% certainty that this is transparent wet water in a vessel.",
                "ingredients": ["Dihydrogen Monoxide (100%)", "Dissolved Oxygen", "Glass Vessel Friction"],
                "proTip": "Hydration Guideline: Pour water into cup to obtain a cup of water. Do not breathe while drinking."
            },
            {
                "detectedItem": "Ambient Room-Temp H2O",
                "category": "Aqueous Compliance Liquid",
                "confidence": "100.00%",
                "verdict": "Spectrometry confirms the presence of molecules that are completely wet. Further testing postponed until next fiscal quarter.",
                "ingredients": ["Wet Liquid", "Refracted Photons", "Water Molecules"],
                "proTip": "Safety Advisory: Water is not Wi-Fi. Do not submerge your laptop to improve reception."
            }
        ]
    }
}


def extract_image_specs(data_bytes: bytes) -> Dict[str, Any]:
    """Extract format, byte size, and dimensions from raw image bytes without external heavy libs."""
    size_kb = round(len(data_bytes) / 1024, 1)
    specs = {"size_kb": size_kb, "width": None, "height": None, "format": "Unknown"}

    if len(data_bytes) < 16:
        return specs

    if data_bytes.startswith(b"\x89PNG\r\n\x1a\n") and len(data_bytes) >= 24:
        specs["format"] = "PNG"
        w, h = struct.unpack(">II", data_bytes[16:24])
        specs["width"] = w
        specs["height"] = h
        return specs

    if data_bytes.startswith(b"GIF87a") or data_bytes.startswith(b"GIF89a"):
        specs["format"] = "GIF"
        w, h = struct.unpack("<HH", data_bytes[6:10])
        specs["width"] = w
        specs["height"] = h
        return specs

    if data_bytes.startswith(b"\xff\xd8"):
        specs["format"] = "JPEG"
        try:
            offset = 2
            while offset < len(data_bytes) - 4:
                marker, length = struct.unpack(">2sH", data_bytes[offset:offset+4])
                if marker in [b"\xff\xc0", b"\xff\xc2"]:
                    h, w = struct.unpack(">HH", data_bytes[offset+5:offset+9])
                    specs["width"] = w
                    specs["height"] = h
                    break
                offset += 2 + length
        except Exception:
            pass
        return specs

    if data_bytes.startswith(b"RIFF") and b"WEBP" in data_bytes[:16]:
        specs["format"] = "WebP"
        return specs

    return specs


def procedural_fallback_diagnosis(
    filename: Optional[str] = None,
    specs: Optional[Dict[str, Any]] = None,
    sample_id: Optional[str] = None
) -> Dict[str, Any]:
    """Generates an uncannily deadpan corporate diagnosis if AI APIs fail."""
    fname = filename or "unnamed_artifact.png"
    dim_str = f"{specs.get('width')}x{specs.get('height')}" if specs and specs.get("width") else "Indeterminate"
    fmt = specs.get("format", "Digital Image") if specs else "Digital Image"
    kb = specs.get("size_kb", 42) if specs else 42

    return {
        "detectedItem": f"{fmt} Pixel Configuration",
        "category": "Classified Visual Submission",
        "confidence": "100.00%",
        "verdict": f"After convening 14 Visual Inspection Bureaucrats, we certify that '{fname}' ({dim_str}, {kb} KB) consists of exactly 100% uncalibrated digital pixels.",
        "ingredients": [
            f"{fmt} Header Block",
            "Disorganized Photons",
            "Missing Form 001-C Seal"
        ],
        "proTip": "Departmental Directive: Staring at this image for 8 hours meets all quarterly productivity targets."
    }


async def analyze_with_groq_vision_llm(
    filename: Optional[str],
    specs: Dict[str, Any],
    sample_id: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Calls Groq LLM with extracted image specs to generate custom corporate diagnosis."""
    if not settings.GROQ_API_KEY:
        return None

    target_desc = f"Sample target ID: '{sample_id}'" if sample_id else f"User uploaded file: '{filename or 'photo.png'}'"
    specs_desc = f"Format: {specs.get('format')}, Dimensions: {specs.get('width')}x{specs.get('height')}, Size: {specs.get('size_kb')} KB."

    system_prompt = (
        "You are StuPDT Vision Specialist #008 from the Department of Obvious Observation.\n"
        "Your job is to inspect this user's image and provide a hilarious, deadpan, corporate, and completely tautological diagnosis.\n"
        "RULES:\n"
        "1. If the filename or topic suggests a specific character, object, animal, or scene (e.g. 'batman', 'cat', 'receipt', 'code', 'pizza'), identify that specific subject directly in detectedItem and verdict!\n"
        "2. Treat the subject with absurd corporate bureaucracy (e.g. diagnosing Batman as an unlicensed vigilante operating without a Form 001-A aerial mammal permit).\n"
        "3. Sound 100% confident, corporate, and state the painfully obvious as if it were a breakthrough scientific discovery.\n"
        "4. Output MUST be STRICT JSON with NO markdown formatting, NO backticks, and NO trailing text.\n"
        "Required JSON schema:\n"
        "{\n"
        '  "detectedItem": "short 1 to 3 word punchy name (e.g. Batman / Dark Knight)",\n'
        '  "category": "funny corporate/bureaucratic category",\n'
        '  "confidence": "100.00%",\n'
        '  "verdict": "1-2 deadpan sentences confirming the object is undeniably itself",\n'
        '  "ingredients": ["item 1", "item 2", "item 3"],\n'
        '  "proTip": "hilariously unhelpful or tautological advice"\n'
        "}"
    )

    user_prompt = f"Analyze this image asset: {target_desc}. Technical specs: {specs_desc}."

    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY.strip()}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": settings.clean_groq_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.85,
        "max_tokens": 400
    }

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.post(GROQ_CHAT_URL, headers=headers, json=payload)
            if resp.status_code == 200:
                raw_text = resp.json()["choices"][0]["message"]["content"].strip()
                json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group(0))
                    if "detectedItem" in parsed and "verdict" in parsed:
                        if not isinstance(parsed.get("ingredients"), list):
                            parsed["ingredients"] = [str(parsed.get("detectedItem"))]
                        parsed["confidence"] = "100.00%"
                        return parsed
    except Exception as exc:
        logger.warning("Groq Vision LLM call failed: %s", exc)

    return None


async def analyze_vision_payload(
    sample_id: Optional[str] = None,
    base64_data: Optional[str] = None,
    mime_type: Optional[str] = "image/png",
    filename: Optional[str] = None
) -> Dict[str, Any]:
    """Unified Vision backend analysis engine with multi-tier intelligence & fallbacks."""
    import random

    if sample_id and sample_id in SAMPLE_CATALOG:
        sample_meta = SAMPLE_CATALOG[sample_id]
        groq_result = await analyze_with_groq_vision_llm(
            filename=f"{sample_id}.png",
            specs={"format": "PNG", "width": 800, "height": 800, "size_kb": 128},
            sample_id=sample_id
        )
        if groq_result:
            return groq_result

        variants = sample_meta.get("variants", [])
        if variants:
            return random.choice(variants)

    specs = {"size_kb": 0, "width": None, "height": None, "format": "Digital Image"}
    clean_b64 = None
    if base64_data:
        try:
            clean_b64 = base64_data.split(",")[-1]
            raw_bytes = base64.b64decode(clean_b64)
            specs = extract_image_specs(raw_bytes)
        except Exception as exc:
            logger.warning("Could not decode base64 image bytes: %s", exc)

    if clean_b64 and settings.GEMINI_API_KEY:
        try:
            from app.services.gemini_service import analyze_vision_image
            gemini_result = await analyze_vision_image(clean_b64, mime_type or "image/png")
            if gemini_result and "detectedItem" in gemini_result:
                gemini_result["confidence"] = "100.00%"
                return gemini_result
        except Exception as exc:
            logger.warning("Gemini multimodal vision failed: %s", exc)

    groq_result = await analyze_with_groq_vision_llm(
        filename=filename,
        specs=specs,
        sample_id=sample_id
    )
    if groq_result:
        return groq_result

    return procedural_fallback_diagnosis(filename=filename, specs=specs, sample_id=sample_id)
