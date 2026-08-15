"""
KDP Print-Quality Gate
Mission: pre-flight the finished PDF against Amazon KDP paperback requirements
before it is declared done. Ground truth remains the KDP Print Previewer;
this gate catches the mechanical failures early and cheaply.
"""

import logging
import os

from pypdf import PdfReader
from src import config

logger = logging.getLogger("KDPValidator")

POINTS_PER_INCH = 72.0
KDP_MIN_DPI = 300
KDP_MIN_PAGES = 24  # KDP paperback minimum page count
DIM_TOLERANCE_IN = 0.01


class KDPValidator:
    def validate(self, pdf_path, expected_page_count=None):
        """
        Validates page geometry, image resolution, and page count.

        Returns {"passed": bool, "errors": [...], "warnings": [...], "pages": [...]}
        errors   -> would fail KDP review or print visibly wrong
        warnings -> acceptable for smoke runs but not for shipping
        """
        errors, warnings, page_reports = [], [], []

        if not os.path.exists(pdf_path):
            return {"passed": False, "errors": [f"PDF not found: {pdf_path}"],
                    "warnings": [], "pages": []}

        reader = PdfReader(pdf_path)

        interior_w = config.TRIM_WIDTH + config.BLEED_SIZE
        interior_h = config.TRIM_HEIGHT + 2 * config.BLEED_SIZE
        cover_w, cover_h = config.get_cover_spread_size()

        interior_count = 0
        for idx, page in enumerate(reader.pages, start=1):
            box = page.mediabox
            w_in = float(box.width) / POINTS_PER_INCH
            h_in = float(box.height) / POINTS_PER_INCH

            is_cover = w_in > interior_w * 1.5  # spread is ~2x an interior page
            kind = "cover" if is_cover else "interior"
            if not is_cover:
                interior_count += 1

            exp_w, exp_h = (cover_w, cover_h) if is_cover else (interior_w, interior_h)
            if abs(w_in - exp_w) > DIM_TOLERANCE_IN or abs(h_in - exp_h) > DIM_TOLERANCE_IN:
                errors.append(
                    f"Page {idx} ({kind}): size {w_in:.3f}x{h_in:.3f}\" "
                    f"!= expected {exp_w:.3f}x{exp_h:.3f}\""
                )

            # Effective DPI of the page's BACKGROUND art = its largest embedded
            # image measured against the page width. Small overlays (the 1.2"
            # logo) are drawn far narrower than the page, so judging them
            # against full page width would produce false low-DPI failures.
            art_dpi = None
            try:
                widths = [img.image.width for img in page.images]
                if widths:
                    art_dpi = max(widths) / w_in
            except Exception as e:  # image extraction is best-effort
                warnings.append(f"Page {idx}: could not inspect images ({e})")

            if art_dpi is not None and art_dpi < KDP_MIN_DPI:
                errors.append(
                    f"Page {idx} ({kind}): effective resolution {art_dpi:.0f} DPI "
                    f"< KDP minimum {KDP_MIN_DPI} DPI"
                )

            page_reports.append({"page": idx, "kind": kind,
                                 "size_in": (round(w_in, 3), round(h_in, 3)),
                                 "art_dpi": round(art_dpi) if art_dpi else None})

        if interior_count < KDP_MIN_PAGES:
            warnings.append(
                f"Interior page count {interior_count} < KDP minimum {KDP_MIN_PAGES} "
                "(fine for a smoke run, not shippable)"
            )
        if expected_page_count and interior_count != expected_page_count:
            warnings.append(
                f"Interior page count {interior_count} != configured {expected_page_count}"
            )

        passed = not errors
        status = "PASSED" if passed else "FAILED"
        logger.info(f"KDP validation {status}: {len(errors)} error(s), "
                    f"{len(warnings)} warning(s) for {pdf_path}")
        for e in errors:
            logger.error(f"  ✗ {e}")
        for w in warnings:
            logger.warning(f"  ⚠ {w}")

        return {"passed": passed, "errors": errors, "warnings": warnings,
                "pages": page_reports}

    def summary_text(self, report):
        """Short human-readable summary for the Telegram completion message."""
        if report["passed"] and not report["warnings"]:
            return "✅ KDP pre-flight: all checks passed"
        lines = ["✅ KDP pre-flight passed with warnings:" if report["passed"]
                 else "🛑 KDP pre-flight FAILED:"]
        lines += [f"• {e}" for e in report["errors"][:5]]
        lines += [f"• {w}" for w in report["warnings"][:5]]
        return "\n".join(lines)
