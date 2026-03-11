APP_TITLE = "TkImage Studio"
APP_VERSION = "1.0.0"

WINDOW_MIN_WIDTH = 1280
WINDOW_MIN_HEIGHT = 820

# ═══════════════════════════════════════════════════════════════
#  LIGHT PROFESSIONAL THEME  –  Clean, airy, high-contrast
# ═══════════════════════════════════════════════════════════════
COLORS = {
    # Layered backgrounds (warm whites & soft grays)
    "bg_base":        "#F5F6FA",     # main workspace background
    "bg_surface":     "#ECEEF5",     # image viewer / center area
    "bg_panel":       "#FFFFFF",     # side panels (clean white)
    "bg_panel_light": "#F0F1F7",     # cards inside panels
    "bg_elevated":    "#E6E8F0",     # inputs, sub-cards
    "bg_hover":       "#D8DBE8",     # hover state

    # Accent (Refined Blue)
    "accent":         "#4A6CF7",
    "accent_hover":   "#3B5ADB",
    "accent_soft":    "#EEF1FF",     # light accent tint
    "accent_glow":    "#4A6CF710",

    # Semantic
    "success":        "#22C55E",
    "warning":        "#F59E0B",
    "danger":         "#EF4444",

    # Text hierarchy (dark on light — maximum readability)
    "text_primary":   "#1A1D2E",     # near-black for body
    "text_secondary": "#5B6078",     # mid-gray for labels
    "text_muted":     "#9095A8",     # light gray for hints

    # Borders (subtle definition)
    "border":         "#E0E3EB",
    "border_light":   "#ECEEF4",
}

COLLAPSED_RAIL_WIDTH = 42

# ── Generic annotation system (dataset-agnostic) ──
ANNOTATION_STATUS = [
    "Non annoté", "En cours", "Annoté",
    "À vérifier", "Validé", "Rejeté",
]

ANNOTATION_QUALITY = [
    "—", "Excellente", "Bonne", "Acceptable", "Médiocre", "Inutilisable",
]

# Typography
FONTS = {
    "main":       ("Segoe UI", 10),
    "header":     ("Segoe UI", 10, "bold"),
    "section":    ("Segoe UI", 9, "bold"),
    "title":      ("Segoe UI", 18, "bold"),
    "subtitle":   ("Segoe UI", 11),
    "small":      ("Segoe UI", 9),
    "tiny":       ("Segoe UI", 8),
    "mono":       ("Consolas", 10),
    "mono_small": ("Consolas", 9),
    "icon":       ("Segoe UI", 16),
    "icon_small": ("Segoe UI", 12),
}

