import sys
import csv
import pandas as pd
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QLabel,
    QLineEdit,
    QDateEdit,
    QFileDialog,
    QMessageBox,
)
from PySide6.QtCore import QDate
import matplotlib.pyplot as plt


class FinanceTracker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Finance Tracker")
        self.setGeometry(100, 100, 1000, 600)

        self.tabs = {}  # Dictionary to hold tab widgets
        self.init_ui()

    def init_ui(self):
        # Central widget and layout
        self.tabs_widget = QTabWidget()
        central_widget = QWidget()
        self.central_layout = QVBoxLayout()  # Store layout as instance variable

        # Add tab widget to central layout
        self.central_layout.addWidget(self.tabs_widget)
        central_widget.setLayout(self.central_layout)
        self.setCentralWidget(central_widget)

        # Tab section names
        sections = ["Savings", "Income Pending", "Loans", "Payments Pending"]
        for section in sections:
            self.add_section(section)

        # Inputs for name, amount, and date
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter name")

        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Enter amount")

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())

        # Layout for input fields
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Name:"))
        input_layout.addWidget(self.name_input)
        input_layout.addWidget(QLabel("Amount (LKR):"))
        input_layout.addWidget(self.amount_input)
        input_layout.addWidget(QLabel("Date:"))
        input_layout.addWidget(self.date_input)

        # Add buttons to each section tab
        for section in sections:
            tab = self.tabs[section]
            button_layout = QHBoxLayout()

            add_button = QPushButton("Add")
            add_button.clicked.connect(lambda _, s=section: self.add_entry(s))
            button_layout.addWidget(add_button)

            edit_button = QPushButton("Edit")
            edit_button.clicked.connect(lambda _, s=section: self.edit_entry(s))
            button_layout.addWidget(edit_button)

            delete_button = QPushButton("Delete")
            delete_button.clicked.connect(lambda _, s=section: self.delete_entry(s))
            button_layout.addWidget(delete_button)

            # Add input and buttons to the tab's layout
            tab["layout"].addLayout(input_layout)
            tab["layout"].addLayout(button_layout)

        # Add export/import/chart buttons below the tabs
        self.add_export_import_buttons()

    def add_section(self, section_name):
        tab = QWidget()
        layout = QVBoxLayout()
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Name", "Amount (LKR)", "Date"])

        layout.addWidget(table)
        tab.setLayout(layout)

        self.tabs_widget.addTab(tab, section_name)
        self.tabs[section_name] = {"tab": tab, "layout": layout, "table": table}

    def add_entry(self, section):
        name = self.name_input.text()
        amount = self.amount_input.text()
        date = self.date_input.date().toString("yyyy-MM-dd")

        if not name or not amount:
            QMessageBox.warning(self, "Input Error", "Please enter all fields.")
            return

        try:
            float(amount)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Amount must be a number.")
            return

        table = self.tabs[section]["table"]
        row = table.rowCount()
        table.insertRow(row)
        table.setItem(row, 0, QTableWidgetItem(name))
        table.setItem(row, 1, QTableWidgetItem(amount))
        table.setItem(row, 2, QTableWidgetItem(date))

        self.clear_inputs()

    def edit_entry(self, section):
        table = self.tabs[section]["table"]
        selected = table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Edit Error", "Select a row to edit.")
            return

        name = self.name_input.text()
        amount = self.amount_input.text()
        date = self.date_input.date().toString("yyyy-MM-dd")

        if not name or not amount:
            QMessageBox.warning(self, "Input Error", "Please enter all fields.")
            return

        try:
            float(amount)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Amount must be a number.")
            return

        table.setItem(selected, 0, QTableWidgetItem(name))
        table.setItem(selected, 1, QTableWidgetItem(amount))
        table.setItem(selected, 2, QTableWidgetItem(date))

        self.clear_inputs()

    def delete_entry(self, section):
        table = self.tabs[section]["table"]
        selected = table.currentRow()
        if selected >= 0:
            table.removeRow(selected)

    def clear_inputs(self):
        self.name_input.clear()
        self.amount_input.clear()
        self.date_input.setDate(QDate.currentDate())

    def add_export_import_buttons(self):
        button_layout = QHBoxLayout()

        export_csv_btn = QPushButton("Export CSV")
        export_csv_btn.clicked.connect(self.export_csv)
        button_layout.addWidget(export_csv_btn)

        export_excel_btn = QPushButton("Export Excel")
        export_excel_btn.clicked.connect(self.export_excel)
        button_layout.addWidget(export_excel_btn)

        import_csv_btn = QPushButton("Import CSV")
        import_csv_btn.clicked.connect(self.import_csv)
        button_layout.addWidget(import_csv_btn)

        import_excel_btn = QPushButton("Import Excel")
        import_excel_btn.clicked.connect(self.import_excel)
        button_layout.addWidget(import_excel_btn)

        chart_btn = QPushButton("Show Chart")
        chart_btn.clicked.connect(self.show_chart)
        button_layout.addWidget(chart_btn)

        # ✅ Add this layout to the main layout, not the tab widget!
        self.central_layout.addLayout(button_layout)

    def export_csv(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export CSV", "", "CSV Files (*.csv)"
        )
        if not file_path:
            return

        all_data = []
        for section, info in self.tabs.items():
            table = info["table"]
            for row in range(table.rowCount()):
                row_data = [
                    section,
                    table.item(row, 0).text(),
                    table.item(row, 1).text(),
                    table.item(row, 2).text(),
                ]
                all_data.append(row_data)

        with open(file_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Section", "Name", "Amount", "Date"])
            writer.writerows(all_data)

    def export_excel(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Excel", "", "Excel Files (*.xlsx)"
        )
        if not file_path:
            return

        all_data = []
        for section, info in self.tabs.items():
            table = info["table"]
            for row in range(table.rowCount()):
                row_data = {
                    "Section": section,
                    "Name": table.item(row, 0).text(),
                    "Amount": float(table.item(row, 1).text()),
                    "Date": table.item(row, 2).text(),
                }
                all_data.append(row_data)

        df = pd.DataFrame(all_data)
        df.to_excel(file_path, index=False)

    def import_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import CSV", "", "CSV Files (*.csv)"
        )
        if not file_path:
            return

        with open(file_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                section = row["Section"]
                if section in self.tabs:
                    table = self.tabs[section]["table"]
                    row_pos = table.rowCount()
                    table.insertRow(row_pos)
                    table.setItem(row_pos, 0, QTableWidgetItem(row["Name"]))
                    table.setItem(row_pos, 1, QTableWidgetItem(row["Amount"]))
                    table.setItem(row_pos, 2, QTableWidgetItem(row["Date"]))

    def import_excel(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Excel", "", "Excel Files (*.xlsx)"
        )
        if not file_path:
            return

        df = pd.read_excel(file_path)
        for _, row in df.iterrows():
            section = row["Section"]
            if section in self.tabs:
                table = self.tabs[section]["table"]
                row_pos = table.rowCount()
                table.insertRow(row_pos)
                table.setItem(row_pos, 0, QTableWidgetItem(str(row["Name"])))
                table.setItem(row_pos, 1, QTableWidgetItem(str(row["Amount"])))
                table.setItem(row_pos, 2, QTableWidgetItem(str(row["Date"])))

    def show_chart(self):
        data = {}
        for section, info in self.tabs.items():
            total = 0.0
            table = info["table"]
            for row in range(table.rowCount()):
                try:
                    amount = float(table.item(row, 1).text())
                    total += amount
                except:
                    continue
            data[section] = total

        # Create pie chart
        plt.figure(figsize=(7, 7))
        plt.pie(data.values(), labels=data.keys(), autopct="%1.1f%%")
        plt.title("Finance Distribution")
        plt.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FinanceTracker()
    window.show()
    sys.exit(app.exec())
