"""
Module de journalisation des activités utilisateur.
Enregistre chaque action réalisée avec horodatage et détails,
puis génère un rapport détaillé et professionnel de la session.
"""
import datetime
import os


class ActivityLogger:
    """Enregistre les actions de l'utilisateur pendant la session."""

    CATEGORY_LABELS = {
        "file":       "Fichier",
        "edit":       "Édition",
        "filter":     "Filtre",
        "tool":       "Outil",
        "navigation": "Navigation",
        "ia":         "Intelligence Artificielle",
        "view":       "Affichage",
        "annotation": "Annotation",
    }

    CATEGORY_ICONS = {
        "file":       "\U0001F4C1",
        "edit":       "\u270F\uFE0F",
        "filter":     "\U0001F3A8",
        "tool":       "\U0001F527",
        "navigation": "\u2194\uFE0F",
        "ia":         "\U0001F916",
        "view":       "\U0001F441\uFE0F",
        "annotation": "\U0001F3F7",
    }

    def __init__(self):
        self.session_start = datetime.datetime.now()
        self.entries: list[dict] = []

    # ── Enregistrement ──────────────────────────────────────────
    def log(self, category: str, action: str, details: str = ""):
        self.entries.append({
            "timestamp": datetime.datetime.now(),
            "category": category,
            "action": action,
            "details": details,
        })

    # ── Statistiques ────────────────────────────────────────────
    def get_stats(self) -> dict:
        now = datetime.datetime.now()
        duration = now - self.session_start
        counts: dict[str, int] = {}
        for e in self.entries:
            counts[e["category"]] = counts.get(e["category"], 0) + 1
        return {
            "total": len(self.entries),
            "duration": duration,
            "duration_str": self._format_duration(duration),
            "session_start": self.session_start,
            "session_end": now,
            "counts": counts,
        }

    @staticmethod
    def _format_duration(delta) -> str:
        total = int(delta.total_seconds())
        h, rem = divmod(total, 3600)
        m, s = divmod(rem, 60)
        if h > 0:
            return f"{h}h {m:02d}m {s:02d}s"
        elif m > 0:
            return f"{m}m {s:02d}s"
        return f"{s}s"

    # ── Génération du rapport (texte brut) ──────────────────────
    def generate_report(self) -> str:
        stats = self.get_stats()
        lines: list[str] = []
        sep = "\u2500" * 56

        lines.append("")
        lines.append("  \u25C6  RAPPORT DE SESSION \u2014 TkImage Studio")
        lines.append(f"     {sep}")
        lines.append("")
        lines.append(f"     Date de session    {stats['session_start']:%d/%m/%Y}")
        lines.append(f"     Heure de d\u00e9but    {stats['session_start']:%H:%M:%S}")
        lines.append(f"     Heure de fin       {stats['session_end']:%H:%M:%S}")
        lines.append(f"     Dur\u00e9e totale       {stats['duration_str']}")
        lines.append(f"     Nombre d'actions   {stats['total']}")
        lines.append("")
        lines.append(f"  \u25C6  R\u00c9SUM\u00c9 PAR CAT\u00c9GORIE")
        lines.append(f"     {sep}")
        lines.append("")

        if stats["counts"]:
            for cat, count in sorted(stats["counts"].items(), key=lambda x: -x[1]):
                icon = self.CATEGORY_ICONS.get(cat, "\u2022")
                label = self.CATEGORY_LABELS.get(cat, cat)
                bar_len = min(count, 30)
                bar = "\u2588" * bar_len
                lines.append(f"     {icon} {label:<22} {count:>3}  {bar}")
        else:
            lines.append("     Aucune action enregistr\u00e9e.")

        lines.append("")
        lines.append(f"  \u25C6  JOURNAL D\u00c9TAILL\u00c9 DES ACTIONS")
        lines.append(f"     {sep}")
        lines.append("")

        if self.entries:
            for i, e in enumerate(self.entries, 1):
                ts = e["timestamp"].strftime("%H:%M:%S")
                icon = self.CATEGORY_ICONS.get(e["category"], "\u2022")
                action = e["action"]
                detail = e.get("details", "")
                lines.append(f"     {i:>3}.  [{ts}]  {icon} {action}")
                if detail:
                    lines.append(f"           \u2514\u2500 {detail}")
        else:
            lines.append("     Aucune action enregistr\u00e9e.")

        lines.append("")
        lines.append(f"     {sep}")
        lines.append(f"     G\u00e9n\u00e9r\u00e9 le {stats['session_end']:%d/%m/%Y \u00e0 %H:%M:%S}")
        lines.append("     TkImage Studio v1.0.0")
        lines.append("")

        return "\n".join(lines)

    # ── Export vers fichier ─────────────────────────────────────
    def export_report(self, file_path: str) -> str:
        report = self.generate_report()
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(report)
        return file_path
