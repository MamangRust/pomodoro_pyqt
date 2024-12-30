import sys
import time
import csv
import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QPushButton,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QGraphicsDropShadowEffect,
    QSpinBox,
    QDialog,
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QColor
from qt_material import apply_stylesheet
import plyer


class TimerThread(QThread):
    update_signal = pyqtSignal(int)
    finished_signal = pyqtSignal()

    def __init__(self, duration):
        super().__init__()
        self.duration = duration * 60  # convert to seconds
        self.is_running = True

    def run(self):
        remaining = self.duration
        while remaining > 0 and self.is_running:
            self.update_signal.emit(remaining)
            time.sleep(1)
            remaining -= 1

        if self.is_running:
            self.finished_signal.emit()

    def stop(self):
        self.is_running = False


class PomodoroApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tasks = []
        self.current_timer = None
        self.current_date = datetime.now().date()
        self.initUI()

    def initUI(self):
        # Atur jendela utama
        self.setWindowTitle("Pomodoro Task Manager")
        self.setGeometry(100, 100, 800, 600)

        # Widget utama
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Shadow effect untuk komponen
        def add_shadow(widget):
            effect = QGraphicsDropShadowEffect()
            effect.setBlurRadius(15)
            effect.setColor(QColor(0, 0, 0, 30))
            effect.setOffset(0, 5)
            widget.setGraphicsEffect(effect)

        # Timer Display
        self.timer_label = QLabel("25:00")
        self.timer_label.setStyleSheet(
            """
            font-size: 48px; 
            font-weight: bold; 
            color: #2196F3;
            padding: 20px;
            border-radius: 10px;
            background-color: rgba(33, 150, 243, 0.1);
        """
        )
        self.timer_label.setAlignment(Qt.AlignCenter)
        add_shadow(self.timer_label)
        layout.addWidget(self.timer_label)

        # Input Layout
        input_layout = QHBoxLayout()

        # Title Input
        title_layout = QVBoxLayout()
        title_label = QLabel("Judul Task")
        self.title_input = QLineEdit()
        self.title_input.setStyleSheet(
            """
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #BDBDBD;
        """
        )
        title_layout.addWidget(title_label)
        title_layout.addWidget(self.title_input)
        input_layout.addLayout(title_layout)

        # Description Input
        desc_layout = QVBoxLayout()
        desc_label = QLabel("Deskripsi Task")
        self.desc_input = QLineEdit()
        self.desc_input.setStyleSheet(
            """
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #BDBDBD;
        """
        )
        desc_layout.addWidget(desc_label)
        desc_layout.addWidget(self.desc_input)
        input_layout.addLayout(desc_layout)

        # Pomodoro Durasi
        pomodoro_layout = QVBoxLayout()
        pomodoro_label = QLabel("Durasi Pomodoro")
        self.pomodoro_select = QComboBox()
        self.pomodoro_select.addItems(["25", "30", "45", "60"])
        self.pomodoro_select.setStyleSheet(
            """
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #BDBDBD;
        """
        )
        pomodoro_layout.addWidget(pomodoro_label)
        pomodoro_layout.addWidget(self.pomodoro_select)
        input_layout.addLayout(pomodoro_layout)

        # Language Selection
        language_layout = QVBoxLayout()
        language_label = QLabel("Bahasa Pemrograman")
        self.language_select = QComboBox()
        self.language_select.addItems(["Python", "Golang", "Java", "Rust"])
        self.language_select.setStyleSheet(
            """
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #BDBDBD;
        """
        )
        language_layout.addWidget(language_label)
        language_layout.addWidget(self.language_select)
        input_layout.addLayout(language_layout)

        layout.addLayout(input_layout)

        # Tombol Action
        button_layout = QHBoxLayout()

        buttons = [
            ("Tambah Task", self.tambah_task, "primary"),
            ("Mulai Timer", self.start_timer, "secondary"),
            ("Jeda", self.pause_timer, "warning"),
            ("Berhenti", self.stop_timer, "danger"),
            (
                "Pilih Visualisasi",
                self.pilih_visualisasi,
                "primary",
            ),  # Tambahkan tombol baru di sini
        ]

        for text, method, style in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(method)
            btn.setStyleSheet(
                f"""
                background-color: {style};
                color: white;
                padding: 10px;
                border-radius: 5px;
            """
            )
            button_layout.addWidget(btn)

        layout.addLayout(button_layout)

        # Tabel Task
        self.task_table = QTableWidget()
        self.task_table.setColumnCount(5)
        self.task_table.setHorizontalHeaderLabels(
            ["Judul", "Deskripsi", "Durasi (menit)", "Bahasa", "Status"]
        )
        self.task_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.task_table)

    def tambah_task(self):
        title = self.title_input.text()
        desc = self.desc_input.text()
        pomodoro = self.pomodoro_select.currentText()
        language = self.language_select.currentText()

        if not title or not desc:
            QMessageBox.warning(self, "Peringatan", "Harap isi semua kolom!")
            return

        # Tambah task ke list
        task = {
            "title": title,
            "description": desc,
            "duration": pomodoro,
            "language": language,
            "status": "Belum Dimulai",
        }
        self.tasks.append(task)

        # Update tabel
        row_position = self.task_table.rowCount()
        self.task_table.insertRow(row_position)
        self.task_table.setItem(row_position, 0, QTableWidgetItem(title))
        self.task_table.setItem(row_position, 1, QTableWidgetItem(desc))
        self.task_table.setItem(row_position, 2, QTableWidgetItem(pomodoro))
        self.task_table.setItem(row_position, 3, QTableWidgetItem(language))
        self.task_table.setItem(row_position, 4, QTableWidgetItem("Belum Dimulai"))

        # Simpan ke CSV
        self.simpan_ke_csv()

        try:
            plyer.notification.notify(
                title="Task Ditambahkan",
                message=f"{title} - {desc}",
                app_icon=None,
                timeout=10,
            )
        except Exception as e:
            print(f"Gagal menampilkan notifikasi: {e}")

        # Reset input
        self.title_input.clear()
        self.desc_input.clear()

    def start_timer(self):
        duration = int(self.pomodoro_select.currentText())

        self.current_timer = TimerThread(duration)
        self.current_timer.update_signal.connect(self.update_timer_display)
        self.current_timer.finished_signal.connect(self.timer_finished)

        self.current_timer.start()

    def update_timer_display(self, remaining):
        minutes = remaining // 60
        seconds = remaining % 60
        self.timer_label.setText(f"{minutes:02d}:{seconds:02d}")

    def timer_finished(self):
        plyer.notification.notify(
            title="Pomodoro Selesai!",
            message="Waktu istirahat atau lanjutkan task berikutnya",
            app_icon=None,
            timeout=10,
        )

        self.timer_label.setText("00:00")

    def pause_timer(self):
        if self.current_timer:
            self.current_timer.stop()

    def stop_timer(self):
        if self.current_timer:
            self.current_timer.stop()
        self.timer_label.setText("00:00")

    def simpan_ke_csv(self):
        today = datetime.now().date()

        # Create hierarchical folder structure
        year_folder = os.path.join(os.getcwd(), str(today.year))
        month_folder = os.path.join(year_folder, today.strftime("%B"))
        day_folder = os.path.join(month_folder, str(today.day))

        # Create folders if they don't exist
        os.makedirs(day_folder, exist_ok=True)

        # Generate filename with daily datestamp
        csv_filename = os.path.join(
            day_folder, f"{today.strftime('%Y-%m-%d')}_tasks.csv"
        )

        # Prepare data for CSV
        csv_data = []
        for task in self.tasks:
            csv_data.append(
                {
                    "Tanggal": today,
                    "Judul": task["title"],
                    "Deskripsi": task["description"],
                    "Durasi": task["duration"],
                    "Bahasa": task["language"],
                    "Status": task["status"],
                }
            )

        # Save to CSV
        df = pd.DataFrame(csv_data)
        df.to_csv(csv_filename, index=False, encoding="utf-8")

    def visualisasi_data(self, tahun=None, bulan=None):
        try:
            # Jika tidak ada tahun yang ditentukan, gunakan tahun saat ini
            if tahun is None:
                tahun = datetime.now().year

            # Konversi tahun ke string
            tahun_str = str(tahun)
            year_folder = os.path.join(os.getcwd(), tahun_str)

            # Check if year folder exists
            if not os.path.exists(year_folder):
                QMessageBox.warning(
                    self, "Peringatan", f"Folder tahun {tahun} tidak ditemukan!"
                )
                return

            # Collect all task data from CSV files
            all_tasks_data = []

            # Filter folder bulan
            for month_dir in os.listdir(year_folder):
                # Jika bulan ditentukan, filter hanya bulan tersebut
                if bulan and bulan.lower() != month_dir.lower():
                    continue

                month_path = os.path.join(year_folder, month_dir)
                if os.path.isdir(month_path):
                    # Tambahkan iterasi untuk folder tanggal
                    for day_dir in os.listdir(month_path):
                        day_path = os.path.join(month_path, day_dir)
                        if os.path.isdir(day_path):
                            for file in os.listdir(day_path):
                                if file.endswith("_tasks.csv"):
                                    file_path = os.path.join(day_path, file)
                                    try:
                                        # Parse dates with custom parsing to handle different formats
                                        df = pd.read_csv(file_path)

                                        # Custom date parsing
                                        df["Tanggal"] = pd.to_datetime(
                                            df["Tanggal"],
                                            format="%Y-%m-%d",
                                            errors="coerce",
                                        )

                                        # Tambahkan kolom bulan dan tahun
                                        df["Bulan"] = df["Tanggal"].dt.month_name()
                                        df["Tahun"] = df["Tanggal"].dt.year

                                        all_tasks_data.append(df)
                                    except Exception as e:
                                        print(f"Error reading file {file_path}: {e}")

            if not all_tasks_data:
                QMessageBox.warning(
                    self, "Peringatan", f"Tidak ada data tasks untuk tahun {tahun}!"
                )
                return

            # Combine all tasks data
            combined_df = pd.concat(all_tasks_data, ignore_index=True)

            # Remove any rows with invalid dates
            combined_df = combined_df.dropna(subset=["Tanggal"])

            # Visualisasi 1: Distribusi Bahasa Pemrograman
            plt.figure(figsize=(15, 6))

            plt.subplot(1, 2, 1)
            language_counts = combined_df["Bahasa"].value_counts()
            language_counts.plot(kind="pie", autopct="%1.1f%%")
            plt.title(f"Distribusi Bahasa Pemrograman\n{tahun}")
            plt.ylabel("")

            # Visualisasi 2: Jumlah Task per Bulan/Minggu
            plt.subplot(1, 2, 2)
            # Jika spesifik bulan, tampilkan detail per minggu
            if bulan:
                combined_df["Minggu"] = combined_df["Tanggal"].dt.isocalendar().week
                monthly_tasks = combined_df.groupby("Minggu").size()
                monthly_tasks.plot(kind="bar")
                plt.title(f"Jumlah Task per Minggu\n{bulan} {tahun}")
                plt.xlabel("Minggu ke-")
            else:
                monthly_tasks = combined_df.groupby("Bulan").size()
                monthly_tasks.plot(kind="bar")
                plt.title(f"Jumlah Task per Bulan\n{tahun}")
                plt.xlabel("Bulan")

            plt.ylabel("Jumlah Task")
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()

            # Simpan visualisasi
            output_folder = os.path.join(year_folder, "Visualisasi")
            os.makedirs(output_folder, exist_ok=True)

            # Buat nama file berdasarkan tahun dan bulan (jika ada)
            if bulan:
                output_filename = f"Visualisasi_Tasks_{tahun}_{bulan}.png"
            else:
                output_filename = f"Visualisasi_Tasks_{tahun}.png"

            output_path = os.path.join(output_folder, output_filename)

            plt.savefig(output_path, bbox_inches="tight")
            plt.close()

            # Tampilkan pesan berhasil
            QMessageBox.information(
                self, "Visualisasi Berhasil", f"Visualisasi disimpan di:\n{output_path}"
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Kesalahan",
                f"Terjadi kesalahan dalam membuat visualisasi:\n{str(e)}",
            )

    # Tambahkan method untuk memilih visualisasi
    def pilih_visualisasi(self):
        # Dialog untuk memilih tahun dan bulan (opsional)
        dialog = QDialog(self)
        dialog.setWindowTitle("Pilih Visualisasi")
        layout = QVBoxLayout()

        # Input tahun
        tahun_layout = QHBoxLayout()
        tahun_label = QLabel("Tahun:")
        tahun_input = QSpinBox()
        tahun_input.setRange(2000, 2050)
        tahun_input.setValue(datetime.now().year)
        tahun_layout.addWidget(tahun_label)
        tahun_layout.addWidget(tahun_input)

        # Input bulan (opsional)
        bulan_layout = QHBoxLayout()
        bulan_label = QLabel("Bulan (Opsional):")
        bulan_input = QComboBox()
        bulan_input.addItem("Semua Bulan")
        bulan_input.addItems(
            [
                "January",
                "February",
                "March",
                "April",
                "May",
                "June",
                "July",
                "August",
                "September",
                "October",
                "November",
                "December",
            ]
        )
        bulan_layout.addWidget(bulan_label)
        bulan_layout.addWidget(bulan_input)

        # Tombol visualisasi
        visualisasi_btn = QPushButton("Buat Visualisasi")
        visualisasi_btn.clicked.connect(
            lambda: self.visualisasi_data(
                tahun=tahun_input.value(),
                bulan=(
                    bulan_input.currentText()
                    if bulan_input.currentIndex() > 0
                    else None
                ),
            )
        )

        layout.addLayout(tahun_layout)
        layout.addLayout(bulan_layout)
        layout.addWidget(visualisasi_btn)

        dialog.setLayout(layout)
        dialog.exec_()


def main():
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme="light_blue.xml")

    pomodoro_app = PomodoroApp()
    pomodoro_app.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
