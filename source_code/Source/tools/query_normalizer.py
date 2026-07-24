"""
tools/query_normalizer.py
─────────────────────────────────────────────────────────────────────────────
Vietnamese Query Normalizer — supports VNI input method + LLM typo fallback.

Pipeline:
  1. VNI Decoder (deterministic, zero-latency):
     Decodes VNI digits into Vietnamese diacritics.
     "chi tiet611" → "chi tiết"
     VNI rules: 1=acute 2=grave 3=hook 4=tilde 5=dot
                6=circumflex(â/ê/ô) 7=horn(ơ/ư) 8=breve(ă) 9=đ
     Extra/invalid digits are discarded.

  2. LLM Spellcheck (fallback, only when needed):
     Corrects spelling and missing diacritics remaining after VNI decoding.
     Strict prompt: ONLY add diacritics, DO NOT add new words.
     Guard: word count +1 max, numbers preserved.
"""

import re
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

# ─── VNI mappings ─────────────────────────────────────────────────────────────

# Diacritics: key=digit, value={base_char: result_char}
_VNI_CIRCUMFLEX = {'a': 'â', 'e': 'ê', 'o': 'ô', 'A': 'Â', 'E': 'Ê', 'O': 'Ô'}
_VNI_HORN       = {'o': 'ơ', 'u': 'ư', 'O': 'Ơ', 'U': 'Ư'}
_VNI_BREVE      = {'a': 'ă', 'A': 'Ă'}

# Tone marks: (base_vowel, digit) → accented_vowel
_VNI_TONES: dict[tuple[str, str], str] = {}
_TONE_DATA = [
    # (base, acute, grave, hook, tilde, dot)
    ('a',  'á','à','ả','ã','ạ'),
    ('ă',  'ắ','ằ','ẳ','ẵ','ặ'),
    ('â',  'ấ','ầ','ẩ','ẫ','ậ'),
    ('e',  'é','è','ẻ','ẽ','ẹ'),
    ('ê',  'ế','ề','ể','ễ','ệ'),
    ('i',  'í','ì','ỉ','ĩ','ị'),
    ('o',  'ó','ò','ỏ','õ','ọ'),
    ('ô',  'ố','ồ','ổ','ỗ','ộ'),
    ('ơ',  'ớ','ờ','ở','ỡ','ợ'),
    ('u',  'ú','ù','ủ','ũ','ụ'),
    ('ư',  'ứ','ừ','ử','ữ','ự'),
    ('y',  'ý','ỳ','ỷ','ỹ','ỵ'),
]
for _base, *_accents in _TONE_DATA:
    for _digit, _accented in zip('12345', _accents):
        _VNI_TONES[(_base, _digit)] = _accented
        _VNI_TONES[(_base.upper(), _digit)] = _accented.upper()

# ─── VNI token decoder ────────────────────────────────────────────────────────

def _is_vni_token(token: str) -> bool:
    """
    Returns True if token looks like VNI-encoded Vietnamese.
    Condition: contains Latin letters and digits 1-9 (not pure numbers).
    """
    has_letter = bool(re.search(r'[a-zA-Z]', token))
    has_vni_digit = bool(re.search(r'[1-9]', token))
    return has_letter and has_vni_digit


def _decode_vni_token(token: str) -> str:
    """
    Decodes a VNI token into accented Vietnamese.
    Invalid or redundant digits are discarded.

    Examples:
      "tiet611"  → "tiết"   (6→ê, 1→acute, second 1 is discarded)
      "kho7a7n5" → "khoản"  (7→ơ, second 7→ư is invalid and discarded, 5→dot is invalid on 'n')
      "vie65t"   → "việt"   (6→ê, 5→dot)
      "d9"       → "đ"
    """
    if not _is_vni_token(token):
        return token

    output: list[str] = []
    tone_applied = False  # Each syllable can receive at most 1 tone mark

    for ch in token:
        if not ch.isdigit():
            output.append(ch)
            continue

        digit = ch

        if digit == '6':
            # Circumflex: find the nearest vowel from right-to-left
            for j in range(len(output) - 1, -1, -1):
                if output[j] in _VNI_CIRCUMFLEX:
                    output[j] = _VNI_CIRCUMFLEX[output[j]]
                    break

        elif digit == '7':
            # Horn
            for j in range(len(output) - 1, -1, -1):
                if output[j] in _VNI_HORN:
                    output[j] = _VNI_HORN[output[j]]
                    break

        elif digit == '8':
            # Breve
            for j in range(len(output) - 1, -1, -1):
                if output[j] in _VNI_BREVE:
                    output[j] = _VNI_BREVE[output[j]]
                    break

        elif digit == '9':
            # Stroke
            for j in range(len(output) - 1, -1, -1):
                if output[j].lower() == 'd':
                    output[j] = 'Đ' if output[j].isupper() else 'đ'
                    break

        elif digit in '12345':
            # Tone mark
            if not tone_applied:
                # Apply tone mark to the nearest vowel from right-to-left
                for j in range(len(output) - 1, -1, -1):
                    key = (output[j], digit)
                    if key in _VNI_TONES:
                        output[j] = _VNI_TONES[key]
                        tone_applied = True
                        break

        # Digit '0' (clear mark) — rarely used in chats, skipped

    return ''.join(output)


def decode_vni(text: str) -> Tuple[str, bool]:
    """
    Decodes the entire sentence: splits tokens, decodes each token if it is VNI.

    Returns:
        (decoded_text, was_changed)
    """
    tokens = text.split(' ')
    decoded_tokens = [_decode_vni_token(t) for t in tokens]
    decoded = ' '.join(decoded_tokens)
    changed = decoded != text
    if changed:
        logger.info(f"[VNI] '{text}' → '{decoded}'")
    return decoded, changed


# ─── Diacritic heuristic (for LLM fallback) ──────────────────────────────────

_VIET_DIACRITICS_RE = re.compile(
    r'[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ'
    r'ÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ]'
)
_VIET_SYLLABLE_PATTERNS = [
    r'\b(ph|nh|ch|th|gi|qu|tr|ng|ngh|kh|gh)\w+\b',
    r'\b\w*(ong|ung|ang|eng|inh|anh|oan|uon|ien|uoc|uot|iet|uong)\b',
    r'\b(la|gi|hay|khi|roi|voi|cua|cho|nhu|ma|va|de|bi|se|da|thi|nhe)\b',
]


def _diacritics_ratio(text: str) -> float:
    chars = re.sub(r'\s+', '', text)
    if not chars:
        return 1.0
    return len(_VIET_DIACRITICS_RE.findall(text)) / len(chars)


def _needs_llm_spellcheck(text: str) -> bool:
    """Detects text missing diacritics (not VNI) that needs LLM correction."""
    words = text.strip().split()
    if len(words) < 2:
        return False
    if _diacritics_ratio(text) >= 0.08:
        return False
    text_lower = text.lower()
    return any(re.search(p, text_lower) for p in _VIET_SYLLABLE_PATTERNS)


# ─── LLM spellcheck (conservative) ───────────────────────────────────────────

def _tokenize(text: str) -> list[str]:
    return re.findall(r'\S+', text)


def _validate_correction(original: str, corrected: str) -> bool:
    """Validates that LLM does not over-correct (adding words, losing numbers)."""
    orig_tokens  = _tokenize(original)
    corr_tokens  = _tokenize(corrected)
    # Word count check: max +1 (in case attached words were split)
    if len(corr_tokens) > len(orig_tokens) + 1:
        logger.warning(f"[Normalizer] Over-correction: {len(orig_tokens)}→{len(corr_tokens)} tokens. Rollback.")
        return False
    # Numbers must be preserved
    digits_in_orig = re.findall(r'\d+', original)
    digits_in_corr = re.findall(r'\d+', corrected)
    for d in digits_in_orig:
        if d not in digits_in_corr:
            logger.warning(f"[Normalizer] Number '{d}' lost in correction. Rollback.")
            return False
    # Length check
    if len(corrected) > len(original) * 2:
        logger.warning("[Normalizer] Corrected text too long. Rollback.")
        return False
    return True


def _llm_spellcheck(query: str, llm) -> Tuple[str, bool]:
    """LLM is only allowed to add diacritics, NOT add/remove words."""
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser

    prompt = ChatPromptTemplate.from_template(
        "Bạn là công cụ sửa lỗi chính tả tiếng Việt.\n"
        "Nhiệm vụ DUY NHẤT: thêm dấu thanh còn thiếu vào các từ đã có.\n\n"
        "QUY TẮC TUYỆT ĐỐI:\n"
        "1. KHÔNG thêm từ mới. KHÔNG xóa từ. Chỉ sửa dấu.\n"
        "2. Số, mã code, ký hiệu → GIỮ NGUYÊN hoàn toàn.\n"
        "3. Kết quả phải có đúng {word_count} từ (±1 nếu tách từ dính).\n"
        "4. CHỈ trả về câu đã sửa, KHÔNG giải thích.\n\n"
        "Ví dụ:\n"
        "  may tinh hoc sau  →  máy tính học sâu\n"
        "  ky thuat dien tu  →  kỹ thuật điện tử\n\n"
        "Câu cần sửa: {query}\n"
        "Câu đã sửa:"
    )
    chain = prompt | llm | StrOutputParser()
    try:
        corrected = chain.invoke({
            "query": query,
            "word_count": len(_tokenize(query)),
        }).strip().strip('"').strip("'")
        # Extract first line (preventing LLM from appending explanations)
        corrected = corrected.split('\n')[0].strip()
        if not corrected or not _validate_correction(query, corrected):
            return query, False
        changed = corrected.lower() != query.lower()
        return corrected, changed
    except Exception as e:
        logger.error(f"[Normalizer] LLM spellcheck failed: {e}")
        return query, False


# ─── Public API ───────────────────────────────────────────────────────────────

def normalize_query(query: str, llm, force: bool = False) -> Tuple[str, bool]:
    """
    Normalizes a query using a 2-step pipeline:
      1. VNI decode (deterministic, does not call LLM)
      2. LLM spellcheck (only if text is still missing diacritics after step 1)

    Args:
        query:  Original query from user.
        llm:    ChatOllama instance.
        force:  Skip heuristics (used for testing).

    Returns:
        (final_query, was_corrected)
    """
    original = query
    was_corrected = False

    # ── Step 1: VNI decode ──
    decoded, vni_changed = decode_vni(query)
    if vni_changed:
        query = decoded
        was_corrected = True
        logger.info(f"[Normalizer] VNI decoded: '{original}' → '{query}'")

    # ── Step 2: LLM spellcheck (if text still lacks diacritics) ──
    if force or _needs_llm_spellcheck(query):
        logger.info(f"[Normalizer] LLM spellcheck triggered for: '{query}'")
        corrected, llm_changed = _llm_spellcheck(query, llm)
        if llm_changed:
            query = corrected
            was_corrected = True
            logger.info(f"[Normalizer] LLM corrected: '{decoded}' → '{query}'")

    if was_corrected:
        logger.info(f"[Normalizer] Final: '{original}' → '{query}'")

    return query, was_corrected
