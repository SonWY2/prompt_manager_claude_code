"""
[overview]
결과 뷰어 위젯

[description]
오른쪽 패널 결과 UI와 실행 이력/비교/메트릭 기능을 제공합니다.
"""

from __future__ import annotations

from datetime import datetime
from difflib import ndiff
from html import escape
from typing import Any, Dict, List, Optional

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTabWidget,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from src.core.provider_manager import ProviderManager
from src.gui.theme import (
    COLOR_ACCENT,
    COLOR_BORDER,
    COLOR_SIDEBAR,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_INPUT_BG,
    COLOR_INPUT_BORDER,
    COLOR_BUTTON_BG,
    COLOR_BUTTON_HOVER,
    COLOR_BACKGROUND,
)


class ResultViewer(QWidget):
    run_clicked = Signal(str)

    DEFAULT_MODELS = ["OpenAI: GPT-4o", "Ollama: llama2"]
    METRIC_KEYS = ["latency", "input_tokens", "output_tokens", "cost"]

    def __init__(self, provider_manager: Optional[ProviderManager] = None) -> None:
        super().__init__()
        self._provider_manager = provider_manager
        self._history: List[str] = []
        self._history_entries: List[Dict[str, Any]] = []
        self._is_streaming = False
        self._last_metrics: Dict[str, float] = {
            "latency": 0.0,
            "input_tokens": 0.0,
            "output_tokens": 0.0,
            "cost": 0.0,
        }

        self._setup_ui()
        self._connect_signals()
        self._load_models()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._create_control_bar())

        self._tab_widget = QTabWidget()
        self._tab_widget.setStyleSheet(
            f"""
            QTabWidget::pane {{ border: none; background-color: {COLOR_BACKGROUND}; }}
            QTabBar::tab {{
                background-color: transparent;
                color: {COLOR_TEXT_SECONDARY};
                padding: 10px 16px;
                margin-right: 4px;
                font-size: 10pt;
                font-weight: 500;
                border-bottom: 2px solid transparent;
            }}
            QTabBar::tab:selected {{
                color: {COLOR_ACCENT};
                border-bottom: 2px solid {COLOR_ACCENT};
            }}
            QTabBar::tab:hover {{ color: {COLOR_TEXT_PRIMARY}; }}
            """
        )

        self._tab_widget.addTab(self._create_result_tab(), "Result")
        self._tab_widget.addTab(self._create_history_tab(), "History")
        self._tab_widget.addTab(self._create_compare_tab(), "Compare")
        self._tab_widget.addTab(self._create_metrics_tab(), "Metrics")
        layout.addWidget(self._tab_widget)

        self._metrics_bar = self._create_metrics_bar()
        layout.addWidget(self._metrics_bar)

        self.setLayout(layout)

    def _create_control_bar(self) -> QWidget:
        widget = QWidget()
        widget.setStyleSheet(f"background-color: {COLOR_SIDEBAR}; border-bottom: 1px solid {COLOR_BORDER};")

        layout = QHBoxLayout()
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        model_label = QLabel("Model")
        model_label.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 10pt;")
        layout.addWidget(model_label)

        self._model_selector = QComboBox()
        self._model_selector.setStyleSheet(
            f"""
            QComboBox {{
                background-color: {COLOR_INPUT_BG};
                color: {COLOR_TEXT_PRIMARY};
                border: 1px solid {COLOR_INPUT_BORDER};
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 10pt;
                min-width: 200px;
            }}
            QComboBox::drop-down {{ border: none; }}
            QComboBox QAbstractItemView {{
                background-color: {COLOR_SIDEBAR};
                selection-background-color: {COLOR_ACCENT};
                color: {COLOR_TEXT_PRIMARY};
            }}
            """
        )
        layout.addWidget(self._model_selector)

        layout.addStretch()

        self._run_button = QPushButton("RUN")
        self._run_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._run_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {COLOR_ACCENT};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 32px;
                font-size: 11pt;
                font-weight: 600;
            }}
            QPushButton:hover {{ background-color: #0062A3; }}
            QPushButton:pressed {{ background-color: #0055A0; }}
            QPushButton:disabled {{ background-color: {COLOR_BUTTON_BG}; color: {COLOR_TEXT_SECONDARY}; }}
            """
        )
        layout.addWidget(self._run_button)

        widget.setLayout(layout)
        return widget

    def _create_result_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._result_browser = QTextBrowser()
        self._result_browser.setStyleSheet(
            f"""
            QTextBrowser {{
                background-color: transparent;
                color: {COLOR_TEXT_PRIMARY};
                border: none;
                padding: 20px;
                font-size: 11pt;
                line-height: 1.6;
            }}
            """
        )
        layout.addWidget(self._result_browser)

        widget.setLayout(layout)
        return widget

    def _create_history_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        self._history_list = QListWidget()
        self._history_list.currentRowChanged.connect(self._on_history_row_changed)
        self._history_list.setStyleSheet(
            f"""
            QListWidget {{ background-color: {COLOR_SIDEBAR}; color: {COLOR_TEXT_PRIMARY}; border: 1px solid {COLOR_BORDER}; }}
            QListWidget::item:selected {{ background-color: {COLOR_BORDER}; color: {COLOR_TEXT_PRIMARY}; }}
            """
        )
        layout.addWidget(self._history_list)

        self._history_preview = QTextBrowser()
        self._history_preview.setStyleSheet(
            f"background-color: {COLOR_SIDEBAR}; color: {COLOR_TEXT_PRIMARY};"
        )
        layout.addWidget(self._history_preview)

        widget.setLayout(layout)
        return widget

    def _create_compare_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        selectors = QHBoxLayout()
        self._compare_left_selector = QComboBox()
        self._compare_right_selector = QComboBox()
        self._compare_left_selector.currentIndexChanged.connect(
            self._update_compare_view
        )
        self._compare_right_selector.currentIndexChanged.connect(
            self._update_compare_view
        )
        selectors.addWidget(self._compare_left_selector)
        selectors.addWidget(self._compare_right_selector)
        layout.addLayout(selectors)

        self._compare_browser = QTextBrowser()
        self._compare_browser.setStyleSheet(
            f"background-color: {COLOR_SIDEBAR}; color: {COLOR_TEXT_PRIMARY};"
        )
        layout.addWidget(self._compare_browser)

        widget.setLayout(layout)
        return widget

    def _create_metrics_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)

        self._metrics_summary_label = QLabel("Runs: 0")
        self._metrics_summary_label.setWordWrap(True)
        self._metrics_summary_label.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-size: 10pt;"
        )
        layout.addWidget(self._metrics_summary_label)
        layout.addStretch()

        widget.setLayout(layout)
        return widget

    def _create_metrics_bar(self) -> QWidget:
        widget = QWidget()
        widget.setStyleSheet(
            f"QWidget {{ background-color: {COLOR_BORDER}; border-top: 1px solid {COLOR_BORDER}; }}"
        )

        layout = QHBoxLayout()
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(24)

        self._latency_label = QLabel("Latency: -")
        self._input_tokens_label = QLabel("Input: -")
        self._output_tokens_label = QLabel("Output: -")
        self._cost_label = QLabel("Cost: -")

        base_style = f"color: {COLOR_TEXT_PRIMARY}; font-size: 9pt;"
        self._latency_label.setStyleSheet(base_style)
        self._input_tokens_label.setStyleSheet(base_style)
        self._output_tokens_label.setStyleSheet(base_style)
        self._cost_label.setStyleSheet(
            f"color: {COLOR_ACCENT}; font-size: 9pt; font-weight: bold;"
        )

        layout.addWidget(self._latency_label)
        layout.addWidget(self._input_tokens_label)
        layout.addWidget(self._output_tokens_label)
        layout.addWidget(self._cost_label)
        layout.addStretch()

        widget.setLayout(layout)
        return widget

    def _connect_signals(self) -> None:
        self._run_button.clicked.connect(self._on_run_clicked)

    def _on_run_clicked(self) -> None:
        self.run_clicked.emit(self._model_selector.currentText())

    def _on_history_row_changed(self, row: int) -> None:
        if row < 0 or row >= len(self._history_entries):
            self._history_preview.clear()
            return
        self._history_preview.setMarkdown(str(self._history_entries[row]["result"]))

    def _refresh_history_view(self) -> None:
        self._history_list.clear()
        for index, entry in enumerate(self._history_entries, start=1):
            self._history_list.addItem(
                QListWidgetItem(f"#{index} {entry['model']} ({entry['timestamp']})")
            )
        if self._history_entries:
            self._history_list.setCurrentRow(len(self._history_entries) - 1)

    def _refresh_compare_selectors(self) -> None:
        left = self._compare_left_selector.currentIndex()
        right = self._compare_right_selector.currentIndex()

        self._compare_left_selector.blockSignals(True)
        self._compare_right_selector.blockSignals(True)
        self._compare_left_selector.clear()
        self._compare_right_selector.clear()

        for index, entry in enumerate(self._history_entries, start=1):
            label = f"#{index} {entry['model']}"
            self._compare_left_selector.addItem(label, index - 1)
            self._compare_right_selector.addItem(label, index - 1)

        if self._history_entries:
            left = left if 0 <= left < len(self._history_entries) else 0
            right = (
                right
                if 0 <= right < len(self._history_entries)
                else len(self._history_entries) - 1
            )
            self._compare_left_selector.setCurrentIndex(left)
            self._compare_right_selector.setCurrentIndex(right)

        self._compare_left_selector.blockSignals(False)
        self._compare_right_selector.blockSignals(False)
        self._update_compare_view()

    def _format_diff_html(self, left_text: str, right_text: str) -> str:
        left_lines = left_text.splitlines()
        right_lines = right_text.splitlines()
        rows: List[str] = []
        for line in ndiff(left_lines, right_lines):
            if line.startswith("- "):
                rows.append(
                    f'<div style="background:#4a1f1f;">- {escape(line[2:])}</div>'
                )
            elif line.startswith("+ "):
                rows.append(
                    f'<div style="background:#1f4a2a;">+ {escape(line[2:])}</div>'
                )
            elif line.startswith("  "):
                rows.append(f"<div>{escape(line[2:])}</div>")
        return "".join(rows)

    def _update_compare_view(self) -> None:
        if not self._history_entries:
            self._compare_browser.setMarkdown("No history to compare.")
            return

        left_data = self._compare_left_selector.currentData()
        right_data = self._compare_right_selector.currentData()
        if left_data is None or right_data is None:
            self._compare_browser.setMarkdown("Select two runs to compare.")
            return

        left_entry = self._history_entries[int(left_data)]
        right_entry = self._history_entries[int(right_data)]

        header = (
            f"<h3>Left: {escape(str(left_entry['model']))}</h3>"
            f"<p>Latency: {left_entry['latency']:.3f}s / Tokens: in {left_entry['input_tokens']}, out {left_entry['output_tokens']}</p>"
            f"<h3>Right: {escape(str(right_entry['model']))}</h3>"
            f"<p>Latency: {right_entry['latency']:.3f}s / Tokens: in {right_entry['input_tokens']}, out {right_entry['output_tokens']}</p>"
            "<hr/>"
        )
        body = self._format_diff_html(
            str(left_entry["result"]), str(right_entry["result"])
        )
        self._compare_browser.setHtml(header + body)

    def _refresh_metrics_summary(self) -> None:
        run_count = len(self._history_entries)
        if run_count == 0:
            self._metrics_summary_label.setText("Runs: 0")
            return

        total_latency = sum(float(e["latency"]) for e in self._history_entries)
        total_input = sum(int(e["input_tokens"]) for e in self._history_entries)
        total_output = sum(int(e["output_tokens"]) for e in self._history_entries)
        total_cost = sum(float(e["cost"]) for e in self._history_entries)

        by_model: Dict[str, Dict[str, float]] = {}
        for entry in self._history_entries:
            model = str(entry["model"])
            if model not in by_model:
                by_model[model] = {"count": 0.0, "latency": 0.0, "cost": 0.0}
            by_model[model]["count"] += 1
            by_model[model]["latency"] += float(entry["latency"])
            by_model[model]["cost"] += float(entry["cost"])

        max_count = max(int(m["count"]) for m in by_model.values())
        model_lines: List[str] = ["Model Breakdown:"]
        for model_name, values in sorted(by_model.items()):
            count = int(values["count"])
            avg_latency = values["latency"] / count if count else 0.0
            bar_width = int((count / max_count) * 12) if max_count else 0
            bar = "#" * bar_width
            model_lines.append(
                f"- {model_name}: {count} runs [{bar}] avg {avg_latency:.3f}s cost ${values['cost']:.4f}"
            )

        summary_lines = [
            f"Runs: {run_count}",
            f"Average Latency: {total_latency / run_count:.3f}s",
            f"Total Input Tokens: {total_input}",
            f"Total Output Tokens: {total_output}",
            f"Total Cost: ${total_cost:.4f}",
            "",
            *model_lines,
        ]
        self._metrics_summary_label.setText("\n".join(summary_lines))

    def display_result(self, result: str) -> None:
        self._result_browser.setMarkdown(result)

    def clear_result(self) -> None:
        self._result_browser.clear()

    def set_metrics(
        self, latency: float, input_tokens: int, output_tokens: int, cost: float
    ) -> None:
        self._latency_label.setText(f"Latency: {latency}s")
        self._input_tokens_label.setText(f"Input: {input_tokens}")
        self._output_tokens_label.setText(f"Output: {output_tokens}")
        self._cost_label.setText(f"Cost: ${cost:.4f}")
        self._last_metrics = {
            "latency": float(latency),
            "input_tokens": float(input_tokens),
            "output_tokens": float(output_tokens),
            "cost": float(cost),
        }

    def set_loading(self, loading: bool) -> None:
        if loading:
            self._run_button.setText("Running...")
            self._run_button.setEnabled(False)
            return
        self._run_button.setText("RUN")
        self._run_button.setEnabled(True)

    def add_to_history(
        self,
        result: str,
        model: Optional[str] = None,
        latency: Optional[float] = None,
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None,
        cost: Optional[float] = None,
    ) -> None:
        self._history.append(result)
        entry = {
            "result": result,
            "model": model or self._model_selector.currentText(),
            "latency": latency
            if latency is not None
            else self._last_metrics["latency"],
            "input_tokens": int(
                input_tokens
                if input_tokens is not None
                else self._last_metrics["input_tokens"]
            ),
            "output_tokens": int(
                output_tokens
                if output_tokens is not None
                else self._last_metrics["output_tokens"]
            ),
            "cost": cost if cost is not None else self._last_metrics["cost"],
            "timestamp": datetime.now().strftime("%H:%M:%S"),
        }
        self._history_entries.append(entry)
        self._refresh_history_view()
        self._refresh_compare_selectors()
        self._refresh_metrics_summary()

    def get_history(self) -> List[str]:
        return self._history.copy()

    def clear_history(self) -> None:
        self._history.clear()
        self._history_entries.clear()
        self._refresh_history_view()
        self._refresh_compare_selectors()
        self._refresh_metrics_summary()

    def display_error(self, error: str) -> None:
        self._result_browser.setHtml(
            """
            <div style="color: #FF6B6B; padding: 16px; border-left: 4px solid #FF6B6B; background-color: rgba(255, 107, 107, 0.1);">
                <strong>Error:</strong> {error}
            </div>
            """.format(error=escape(error))
        )

    def _load_models(self) -> None:
        self._model_selector.clear()
        if self._provider_manager is None:
            for model in self.DEFAULT_MODELS:
                self._model_selector.addItem(model, None)
            return

        providers = self._provider_manager.get_all_providers()
        if not providers:
            for model in self.DEFAULT_MODELS:
                self._model_selector.addItem(model, None)
            return

        for provider in providers:
            self._model_selector.addItem(
                f"{provider.name}: {provider.model}", provider.id
            )

    def refresh_models(self) -> None:
        self._load_models()

    def get_selected_provider_id(self) -> Optional[str]:
        return self._model_selector.currentData()

    def start_streaming(self) -> None:
        self._is_streaming = True
        self._result_browser.clear()

    def append_streaming_chunk(self, chunk: str) -> None:
        if self._is_streaming:
            self._result_browser.setPlainText(
                self._result_browser.toPlainText() + chunk
            )

    def end_streaming(self) -> None:
        self._is_streaming = False
