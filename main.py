import sys
import os
import csv
import pandas as pd
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTabWidget, QTableWidget, QTableWidgetItem,
    QLabel, QLineEdit, QDateEdit, QFileDialog, QMessageBox
)
from PySide6.QtCore import QDate
import matplotlib.pyplot as plt

DATA_FILE = os.path.join(os.path.dirname(__file__), "data.csv")

class FinanceTracker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Finance Tracker")
        self.setGeometry(100, 100, 1100, 650)
        self.tabs = {}  # section_name: {"table": table}
        self.init_ui()
        self.load_data()  # Load from data.csv on startup

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout()
        central_widget.setLayout(self.main_layout)

        self.name_input = QLineEdit()
        self.amount_input = QLineEdit()
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())

        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Name:"))
        input_layout.addWidget(self.name_input)
        input_layout.addWidget(QLabel("Amount (LKR):"))
        input_layout.addWidget(self.amount_input)
        input_layout.addWidget(QLabel("Date:"))
        input_layout.addWidget(self.date_input)
        self.main_layout.addLayout(input_layout)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add")
        self.edit_btn = QPushButton("Edit")
        self.delete_btn = QPushButton("Delete")
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        self.main_layout.addLayout(btn_layout)

        self.add_btn.clicked.connect(self.handle_add)
        self.edit_btn.clicked.connect(self.handle_edit)
        self.delete_btn.clicked.connect(self.handle_delete)

        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)

        for section in ["Savings", "Income Pending", "Loans", "Payments Pending"]:
            self.add_tab(section)

        file_layout = QHBoxLayout()
        export_csv_btn = QPushButton("Export CSV")
        export_excel_btn = QPushButton("Export Excel")
        import_csv_btn = QPushButton("Import CSV")
        import_excel_btn = QPushButton("Import Excel")
        chart_btn = QPushButton("Show Chart")

        export_csv_btn.clicked.connect(self.export_csv)
        export_excel_btn.clicked.connect(self.export_excel)
        import_csv_btn.clicked.connect(self.import_csv)
        import_excel_btn.clicked.connect(self.import_excel)
        chart_btn.clicked.connect(self.show_chart)

        file_layout.addWidget(export_csv_btn)
        file_layout.addWidget(export_excel_btn)
        file_layout.addWidget(import_csv_btn)
        file_layout.addWidget(import_excel_btn)
        file_layout.addWidget(chart_btn)
        self.main_layout.addLayout(file_layout)

    def add_tab(self, name):
        tab = QWidget()
        layout = QVBoxLayout()
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Name", "Amount (LKR)", "Date"])
        layout.addWidget(table)
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, name)
        self.tabs[name] = {"table": table}

    def get_current_table(self):
        section = self.tab_widget.tabText(self.tab_widget.currentIndex())
        return section, self.tabs[section]["table"]

    def handle_add(self):
        name = self.name_input.text().strip()
        amount = self.amount_input.text().strip()
        date = self.date_input.date().toString("yyyy-MM-dd")

        if not name or not amount:
            QMessageBox.warning(self, "Input Error", "Please fill all fields.")
            return
        try:
            float(amount)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Amount must be a number.")
            return

        section, table = self.get_current_table()
        row = table.rowCount()
        table.insertRow(row)
        table.setItem(row, 0, QTableWidgetItem(name))
        table.setItem(row, 1, QTableWidgetItem(amount))
        table.setItem(row, 2, QTableWidgetItem(date))
        self.clear_inputs()
        self.save_data()

    def handle_edit(self):
        section, table = self.get_current_table()
        row = table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Edit Error", "Select a row to edit.")
            return

        name = self.name_input.text().strip()
        amount = self.amount_input.text().strip()
        date = self.date_input.date().toString("yyyy-MM-dd")

        if not name or not amount:
            QMessageBox.warning(self, "Input Error", "Please fill all fields.")
            return
        try:
            float(amount)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Amount must be a number.")
            return

        table.setItem(row, 0, QTableWidgetItem(name))
        table.setItem(row, 1, QTableWidgetItem(amount))
        table.setItem(row, 2, QTableWidgetItem(date))
        self.clear_inputs()
        self.save_data()

    def handle_delete(self):
        _, table = self.get_current_table()
        row = table.currentRow()
        if row >= 0:
            table.removeRow(row)
            self.save_data()

    def clear_inputs(self):
        self.name_input.clear()
        self.amount_input.clear()
        self.date_input.setDate(QDate.currentDate())

    def save_data(self):
        try:
            with open(DATA_FILE, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Section", "Name", "Amount", "Date"])
                for section, data in self.tabs.items():
                    table = data["table"]
                    for row in range(table.rowCount()):
                        writer.writerow([
                            section,
                            table.item(row, 0).text(),
                            table.item(row, 1).text(),
                            table.item(row, 2).text()
                        ])
        except Exception as e:
            QMessageBox.critical(self, "Save Error", str(e))

    def load_data(self):
        if not os.path.exists(DATA_FILE):
            return
        try:
            with open(DATA_FILE, newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    section = row["Section"]
                    if section in self.tabs:
                        table = self.tabs[section]["table"]
                        r = table.rowCount()
                        table.insertRow(r)
                        table.setItem(r, 0, QTableWidgetItem(row["Name"]))
                        table.setItem(r, 1, QTableWidgetItem(row["Amount"]))
                        table.setItem(r, 2, QTableWidgetItem(row["Date"]))
        except Exception as e:
            QMessageBox.critical(self, "Load Error", str(e))

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export CSV", "", "CSV Files (*.csv)")
        if not path:
            return
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Section", "Name", "Amount", "Date"])
            for section, data in self.tabs.items():
                table = data["table"]
                for row in range(table.rowCount()):
                    writer.writerow([
                        section,
                        table.item(row, 0).text(),
                        table.item(row, 1).text(),
                        table.item(row, 2).text()
                    ])

    def export_excel(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Excel", "", "Excel Files (*.xlsx)")
        if not path:
            return
        rows = []
        for section, data in self.tabs.items():
            table = data["table"]
            for r in range(table.rowCount()):
                rows.append({
                    "Section": section,
                    "Name": table.item(r, 0).text(),
                    "Amount": float(table.item(r, 1).text()),
                    "Date": table.item(r, 2).text()
                })
        df = pd.DataFrame(rows)
        df.to_excel(path, index=False)

    def import_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import CSV", "", "CSV Files (*.csv)")
        if not path:
            return
        with open(path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                section = row["Section"]
                if section in self.tabs:
                    table = self.tabs[section]["table"]
                    r = table.rowCount()
                    table.insertRow(r)
                    table.setItem(r, 0, QTableWidgetItem(row["Name"]))
                    table.setItem(r, 1, QTableWidgetItem(row["Amount"]))
                    table.setItem(r, 2, QTableWidgetItem(row["Date"]))
        self.save_data()

    def import_excel(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import Excel", "", "Excel Files (*.xlsx)")
        if not path:
            return
        df = pd.read_excel(path)
        for _, row in df.iterrows():
            section = row["Section"]
            if section in self.tabs:
                table = self.tabs[section]["table"]
                r = table.rowCount()
                table.insertRow(r)
                table.setItem(r, 0, QTableWidgetItem(str(row["Name"])))
                table.setItem(r, 1, QTableWidgetItem(str(row["Amount"])))
                table.setItem(r, 2, QTableWidgetItem(str(row["Date"])))
        self.save_data()

    def show_chart(self):
        totals = {}
        for section, data in self.tabs.items():
            table = data["table"]
            total = 0
            for r in range(table.rowCount()):
                try:
                    total += float(table.item(r, 1).text())
                except:
                    continue
            totals[section] = total

        plt.figure(figsize=(7, 7))
        plt.pie(totals.values(), labels=totals.keys(), autopct="%1.1f%%")
        plt.title("Finance Distribution")
        plt.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FinanceTracker()
    window.show()
    sys.exit(app.exec())
