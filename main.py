import sys
import os
from datetime import datetime
import pandas as pd
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QTabWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QDateEdit,
    QInputDialog,
)
from PySide6.QtCore import QDate, Qt

# Constants
DATA_FILE = "finance_data.csv"
COLUMNS = ["Section", "Name", "Amount", "Date"]


class FinanceTracker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Finance Tracker")
        self.setGeometry(100, 100, 800, 600)
        self.data = self.load_data()

        self.tabs = {}
        self.init_ui()

        # Styling: Blue + Black Theme
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #121212;
                color: #FFFFFF;
                font-family: Segoe UI, sans-serif;
            }
            QLabel {
                font-size: 14px;
                color: #FFFFFF;
            }
            QLineEdit, QDateEdit {
                background-color: #1e1e1e;
                color: #FFFFFF;
                border: 1px solid #2196F3;
                padding: 5px;
                font-size: 13px;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                padding: 6px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QTableWidget {
                background-color: #1e1e1e;
                color: #FFFFFF;
                gridline-color: #2196F3;
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #0d47a1;
                color: white;
                font-weight: bold;
                padding: 6px;
            }
        """
        )

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                df = pd.read_csv(DATA_FILE)
                if df.empty or list(df.columns) != COLUMNS:
                    raise pd.errors.EmptyDataError
                return df
            except pd.errors.EmptyDataError:
                print("CSV file was empty or corrupted. Initializing new data.")
                return pd.DataFrame(columns=COLUMNS)
        return pd.DataFrame(columns=COLUMNS)

    def save_data(self):
        self.data.to_csv(DATA_FILE, index=False)

    def init_ui(self):
        self.tabs_widget = QTabWidget()
        self.setCentralWidget(self.tabs_widget)

        sections = ["Savings", "Income Pending", "Loans", "Payments Pending"]
        for section in sections:
            self.add_section(section)

        # Input Fields
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter name")
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Enter amount")
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())

        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Name:"))
        input_layout.addWidget(self.name_input)
        input_layout.addWidget(QLabel("Amount:"))
        input_layout.addWidget(self.amount_input)
        input_layout.addWidget(QLabel("Date:"))
        input_layout.addWidget(self.date_input)

        # Buttons
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

            tab["layout"].addLayout(input_layout)
            tab["layout"].addLayout(button_layout)

    def add_section(self, section):
        tab = QWidget()
        layout = QVBoxLayout()
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Name", "Amount", "Date"])
        table.setSortingEnabled(True)

        layout.addWidget(table)

        # Optional total label
        total_label = QLabel()
        layout.addWidget(total_label)

        tab.setLayout(layout)
        self.tabs_widget.addTab(tab, section)
        self.tabs[section] = {
            "widget": tab,
            "layout": layout,
            "table": table,
            "total_label": total_label,
        }
        self.refresh_table(section)

    def add_entry(self, section):
        name = self.name_input.text().strip()
        amount_text = self.amount_input.text().strip()

        if not name:
            QMessageBox.warning(self, "Missing Input", "Please enter a name.")
            return

        if not amount_text:
            QMessageBox.warning(self, "Missing Input", "Please enter an amount.")
            return

        try:
            amount = float(amount_text)
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Amount must be a number.")
            return

        date = self.date_input.date().toString("yyyy-MM-dd")

        new_row = pd.DataFrame([[section, name, amount, date]], columns=COLUMNS)
        self.data = pd.concat([self.data, new_row], ignore_index=True)
        self.save_data()
        self.refresh_table(section)
        self.name_input.clear()
        self.amount_input.clear()
        self.date_input.setDate(QDate.currentDate())

    def edit_entry(self, section):
        table = self.tabs[section]["table"]
        row = table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "No Selection", "Please select a row to edit.")
            return

        name = table.item(row, 0).text()
        amount = table.item(row, 1).text()
        date = table.item(row, 2).text()

        new_name, ok1 = QInputDialog.getText(self, "Edit Name", "Name:", text=name)
        if not ok1 or not new_name.strip():
            return

        new_amount_text, ok2 = QInputDialog.getText(
            self, "Edit Amount", "Amount:", text=amount
        )
        if not ok2 or not new_amount_text.strip():
            return

        new_date_text, ok3 = QInputDialog.getText(
            self, "Edit Date", "Date (YYYY-MM-DD):", text=date
        )
        if not ok3 or not new_date_text.strip():
            return

        try:
            new_amount = float(new_amount_text)
            datetime.strptime(new_date_text, "%Y-%m-%d")
        except Exception:
            QMessageBox.warning(
                self,
                "Invalid Data",
                "Please enter a valid amount and date in YYYY-MM-DD format.",
            )
            return

        idx = self.data[
            (self.data["Section"] == section)
            & (self.data["Name"] == name)
            & (self.data["Amount"] == float(amount))
            & (self.data["Date"] == date)
        ].index

        if not idx.empty:
            self.data.at[idx[0], "Name"] = new_name.strip()
            self.data.at[idx[0], "Amount"] = new_amount
            self.data.at[idx[0], "Date"] = new_date_text
            self.save_data()
            self.refresh_table(section)

    def delete_entry(self, section):
        table = self.tabs[section]["table"]
        row = table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "No Selection", "Please select a row to delete.")
            return

        reply = QMessageBox.question(
            self,
            "Delete Entry",
            "Are you sure you want to delete this entry?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            name = table.item(row, 0).text()
            amount = table.item(row, 1).text()
            date = table.item(row, 2).text()

            self.data = self.data.drop(
                self.data[
                    (self.data["Section"] == section)
                    & (self.data["Name"] == name)
                    & (self.data["Amount"] == float(amount))
                    & (self.data["Date"] == date)
                ].index
            )

            self.save_data()
            self.refresh_table(section)

    def refresh_table(self, section):
        table = self.tabs[section]["table"]
        df = self.data[self.data["Section"] == section].copy()

        table.setRowCount(len(df))
        for i, (_, row) in enumerate(df.iterrows()):
            table.setItem(i, 0, QTableWidgetItem(str(row["Name"])))
            table.setItem(i, 1, QTableWidgetItem(str(row["Amount"])))
            table.setItem(i, 2, QTableWidgetItem(str(row["Date"])))

        # Update total
        total = df["Amount"].sum()
        self.tabs[section]["total_label"].setText(f"Total: {total:.2f}")


# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FinanceTracker()
    window.show()
    sys.exit(app.exec())
