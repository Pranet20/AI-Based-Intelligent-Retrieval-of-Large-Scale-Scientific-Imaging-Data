"""HTML and JSON dataset audit report generator with summary distribution plots."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.datasets.registry import DatasetRegistryEntry


class DatasetReportGenerator:
    """Generates comprehensive scientific dataset audit reports (HTML, JSON, Plots)."""

    def __init__(self, output_dir: str | Path = "reports/dataset_audit") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.figures_dir = self.output_dir.parent / "figures"
        self.figures_dir.mkdir(parents=True, exist_ok=True)

    def generate_distribution_plots(
        self,
        df: pd.DataFrame,
        dataset_id: str,
    ) -> Dict[str, str]:
        """Generate distribution plots (file size, dimensions, quality metrics, labels)."""
        plots: Dict[str, str] = {}
        if df.empty:
            return plots

        # 1. Image dimensions & aspect ratio plot
        if "width" in df.columns and "height" in df.columns and df["width"].dropna().count() > 0:
            plt.figure(figsize=(7, 4))
            valid = df.dropna(subset=["width", "height"])
            plt.scatter(valid["width"], valid["height"], alpha=0.6, edgecolors="none", color="#2563eb")
            plt.title(f"Image Dimensions: {dataset_id}")
            plt.xlabel("Width (px)")
            plt.ylabel("Height (px)")
            plt.grid(True, linestyle="--", alpha=0.5)
            plot_path = self.figures_dir / f"{dataset_id}_dimensions.png"
            plt.tight_layout()
            plt.savefig(plot_path, dpi=150)
            plt.close()
            plots["dimensions"] = str(plot_path.name)

        # 2. File size distribution
        if "file_size_bytes" in df.columns and df["file_size_bytes"].dropna().count() > 0:
            plt.figure(figsize=(7, 4))
            sizes_kb = df["file_size_bytes"].dropna() / 1024.0
            plt.hist(sizes_kb, bins=30, color="#059669", edgecolor="black", alpha=0.7)
            plt.title(f"File Size Distribution (KB): {dataset_id}")
            plt.xlabel("File Size (KB)")
            plt.ylabel("Count")
            plt.grid(True, linestyle="--", alpha=0.5)
            plot_path = self.figures_dir / f"{dataset_id}_filesize.png"
            plt.tight_layout()
            plt.savefig(plot_path, dpi=150)
            plt.close()
            plots["filesize"] = str(plot_path.name)

        # 3. Quality score distribution if available
        if "quality_score" in df.columns and df["quality_score"].dropna().count() > 0:
            plt.figure(figsize=(7, 4))
            scores = df["quality_score"].dropna()
            plt.hist(scores, bins=25, range=(0, 1), color="#d97706", edgecolor="black", alpha=0.7)
            plt.title(f"Computational Quality Score: {dataset_id}")
            plt.xlabel("Quality Score (0.0 to 1.0)")
            plt.ylabel("Count")
            plt.grid(True, linestyle="--", alpha=0.5)
            plot_path = self.figures_dir / f"{dataset_id}_quality.png"
            plt.tight_layout()
            plt.savefig(plot_path, dpi=150)
            plt.close()
            plots["quality"] = str(plot_path.name)

        # 4. Class distribution if labels exist
        if "label" in df.columns and df["label"].dropna().count() > 0:
            plt.figure(figsize=(8, 4))
            counts = df["label"].dropna().value_counts().head(15)
            counts.plot(kind="bar", color="#7c3aed", edgecolor="black")
            plt.title(f"Label / Defect Distribution: {dataset_id}")
            plt.xlabel("Class / Label")
            plt.ylabel("Count")
            plt.xticks(rotation=45, ha="right")
            plt.grid(axis="y", linestyle="--", alpha=0.5)
            plot_path = self.figures_dir / f"{dataset_id}_classes.png"
            plt.tight_layout()
            plt.savefig(plot_path, dpi=150)
            plt.close()
            plots["classes"] = str(plot_path.name)

        return plots

    def build_summary_stats(
        self,
        entry: DatasetRegistryEntry,
        df: pd.DataFrame,
        error_collector_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Aggregate statistical metrics for the dataset."""
        total_images = len(df)
        total_storage_bytes = int(df["file_size_bytes"].sum()) if not df.empty and "file_size_bytes" in df.columns else 0

        formats = df["format"].value_counts().to_dict() if not df.empty and "format" in df.columns else {}
        bit_depths = df["bit_depth"].value_counts().to_dict() if not df.empty and "bit_depth" in df.columns else {}
        channels = df["channels"].value_counts().to_dict() if not df.empty and "channels" in df.columns else {}

        exact_dups = int(df["duplicate_group_id"].notna().sum()) if "duplicate_group_id" in df.columns else 0
        near_dups = int(df["near_duplicate_group_id"].notna().sum()) if "near_duplicate_group_id" in df.columns else 0

        quality_status_counts = (
            df["quality_status"].value_counts().to_dict() if "quality_status" in df.columns else {}
        )

        labels_count = int(df["label"].notna().sum()) if "label" in df.columns else 0

        errors_list = (error_collector_data or {}).get("errors", [])

        return {
            "dataset_id": entry.dataset_id,
            "name": entry.name,
            "source_url": entry.source_url,
            "doi": entry.doi,
            "version": entry.version,
            "license": entry.license,
            "role": entry.role,
            "total_images": total_images,
            "total_storage_bytes": total_storage_bytes,
            "total_storage_mb": round(total_storage_bytes / (1024 * 1024), 2),
            "formats": formats,
            "bit_depths": {str(k): int(v) for k, v in bit_depths.items()},
            "channels": {str(k): int(v) for k, v in channels.items()},
            "labels_available": entry.labels_available,
            "annotated_images_count": labels_count,
            "metadata_available": entry.metadata_available,
            "exact_duplicate_records": exact_dups,
            "near_duplicate_records": near_dups,
            "quality_status_breakdown": quality_status_counts,
            "error_count": len(errors_list),
            "errors": errors_list,
        }

    def generate_html_report(
        self,
        summary: Dict[str, Any],
        plot_files: Dict[str, str],
        output_path: str | Path,
    ) -> Path:
        """Render standalone HTML audit report."""
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        plots_html = ""
        for name, fname in plot_files.items():
            plots_html += f"""
            <div class="plot-box">
                <h4>{name.capitalize()} Plot</h4>
                <img src="../figures/{fname}" alt="{name}" style="max-width:100%; border:1px solid #cbd5e1; border-radius:6px;"/>
            </div>
            """

        errors_html = ""
        if summary.get("errors"):
            rows = "".join(
                f"<tr><td>{e.get('file','')}</td><td>{e.get('operation','')}</td><td>{e.get('exception','')}</td></tr>"
                for e in summary["errors"][:50]
            )
            errors_html = f"""
            <h3>Audit Exceptions ({summary['error_count']} total)</h3>
            <table>
                <thead><tr><th>File</th><th>Operation</th><th>Exception</th></tr></thead>
                <tbody>{rows}</tbody>
            </table>
            """
        else:
            errors_html = "<p style='color:#059669; font-weight:600;'>Zero corruption or read errors encountered during audit.</p>"

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Dataset Audit Report - {summary['name']}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 30px; background: #f8fafc; color: #1e293b; }}
        .header {{ background: #0f172a; color: #ffffff; padding: 25px; border-radius: 8px; margin-bottom: 25px; }}
        .header h1 {{ margin: 0 0 10px 0; font-size: 24px; }}
        .badge {{ background: #2563eb; color: #fff; padding: 4px 10px; border-radius: 4px; font-size: 13px; font-weight: 500; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 15px; margin-bottom: 25px; }}
        .card {{ background: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border: 1px solid #e2e8f0; }}
        .card h3 {{ margin-top: 0; font-size: 16px; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; }}
        .stat-val {{ font-size: 28px; font-weight: 700; color: #0f172a; margin-top: 5px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; background: #fff; border-radius: 8px; overflow: hidden; }}
        th, td {{ padding: 12px 16px; text-align: left; border-bottom: 1px solid #e2e8f0; }}
        th {{ background: #f1f5f9; font-weight: 600; color: #475569; }}
        .plot-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(380px, 1fr)); gap: 20px; margin: 25px 0; }}
        .plot-box {{ background: #fff; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{summary['name']}</h1>
        <p><strong>ID:</strong> {summary['dataset_id']} | <strong>Role:</strong> <span class="badge">{summary['role']}</span> | <strong>DOI:</strong> {summary['doi']}</p>
        <p><strong>License:</strong> {summary['license']} | <strong>Version:</strong> {summary['version']} | <strong>Source:</strong> <a href="{summary['source_url']}" style="color:#60a5fa;" target="_blank">{summary['source_url']}</a></p>
    </div>

    <div class="grid">
        <div class="card">
            <h3>Total Images</h3>
            <div class="stat-val">{summary['total_images']}</div>
        </div>
        <div class="card">
            <h3>Total Storage</h3>
            <div class="stat-val">{summary['total_storage_mb']} MB</div>
        </div>
        <div class="card">
            <h3>Exact Duplicates</h3>
            <div class="stat-val">{summary['exact_duplicate_records']}</div>
        </div>
        <div class="card">
            <h3>Near Duplicates</h3>
            <div class="stat-val">{summary['near_duplicate_records']}</div>
        </div>
    </div>

    <div class="card">
        <h3>Structural Properties</h3>
        <p><strong>Formats:</strong> {json.dumps(summary['formats'])}</p>
        <p><strong>Bit Depths:</strong> {json.dumps(summary['bit_depths'])}</p>
        <p><strong>Channels:</strong> {json.dumps(summary['channels'])}</p>
        <p><strong>Quality Breakdown:</strong> {json.dumps(summary['quality_status_breakdown'])}</p>
    </div>

    <h3>Distribution Plots</h3>
    <div class="plot-grid">
        {plots_html}
    </div>

    {errors_html}
</body>
</html>
"""
        with open(out, "w", encoding="utf-8") as f:
            f.write(html_content)
        return out

    def generate_full_report(
        self,
        entry: DatasetRegistryEntry,
        df: pd.DataFrame,
        error_collector_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, str]:
        """Generate JSON, HTML reports and plots for a dataset."""
        summary = self.build_summary_stats(entry, df, error_collector_data)
        plot_files = self.generate_distribution_plots(df, entry.dataset_id)

        json_path = self.output_dir / f"{entry.dataset_id}_audit.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        html_path = self.output_dir / f"{entry.dataset_id}_audit.html"
        self.generate_html_report(summary, plot_files, html_path)

        return {
            "json": str(json_path.resolve()),
            "html": str(html_path.resolve()),
        }
