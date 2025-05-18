import sys
import csv
import os
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QMessageBox,
    QDateEdit,
    QInputDialog,
)
from PySide6.QtCore import Qt, QDate
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pandas as pd

DATA_FILE = "finance_data.csv"
COLUMNS = ["Section", "Name", "Amount", "Date"]
SECTIONS = ["Savings", "Income Pending", "Loans", "Payments Pending"]


class FinanceTracker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Finance Tracker")
        self.resize(900, 600)

        self.data = pd.DataFrame(columns=COLUMNS)
        self.load_data()

        self.tabs = {}
        self.tabs_widget = QTabWidget()
        self.setCentralWidget(self.tabs_widget)

        for section in SECTIONS:
            self.create_tab(section)

        self.create_summary_tab()
        self.create_chart_tab()

    def load_data(self):
        if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
            self.data = pd.read_csv(DATA_FILE)
        else:
            self.data = pd.DataFrame(columns=COLUMNS)

    def save_data(self):
        self.data.to_csv(DATA_FILE, index=False)
        self.update_summary()

    def create_tab(self, section):
        tab = QWidget()
        layout = QVBoxLayout()

        # Inputs
        input_layout = QHBoxLayout()
        self.name_input = QLineEdit()
        self.amount_input = QLineEdit()
        self.date_input = QDateEdit(calendarPopup=True)
        self.date_input.setDate(QDate.currentDate())

        input_layout.addWidget(QLabel("Name"))
        input_layout.addWidget(self.name_input)
        input_layout.addWidget(QLabel("Amount"))
        input_layout.addWidget(self.amount_input)
        input_layout.addWidget(QLabel("Date"))
        input_layout.addWidget(self.date_input)

        add_button = QPushButton("Add")
        add_button.clicked.connect(lambda _, s=section: self.add_entry(s))
        input_layout.addWidget(add_button)
        layout.addLayout(input_layout)

        # Table
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Name", "Amount", "Date"])
        layout.addWidget(table)

        # Edit/Delete
        btn_layout = QHBoxLayout()
        edit_button = QPushButton("Edit Selected")
        delete_button = QPushButton("Delete Selected")
        edit_button.clicked.connect(lambda _, s=section: self.edit_entry(s))
        delete_button.clicked.connect(lambda _, s=section: self.delete_entry(s))
        btn_layout.addWidget(edit_button)
        btn_layout.addWidget(delete_button)
        layout.addLayout(btn_layout)

        tab.setLayout(layout)
        self.tabs[section] = {"widget": tab, "table": table}
        self.tabs_widget.addTab(tab, section)
        self.refresh_table(section)

    def add_entry(self, section):
        name = self.name_input.text().strip()
        try:
            amount = float(self.amount_input.text())
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Amount must be a number.")
            return
        date = self.date_input.date().toString("yyyy-MM-dd")

        if name:
            new_row = pd.DataFrame([[section, name, amount, date]], columns=COLUMNS)
            self.data = pd.concat([self.data, new_row], ignore_index=True)
            self.save_data()
            self.refresh_table(section)
            self.name_input.clear()
            self.amount_input.clear()

    def edit_entry(self, section):
        table = self.tabs[section]["table"]
        row = table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "No Selection", "Select a row to edit.")
            return

        name = table.item(row, 0).text()
        amount = table.item(row, 1).text()
        date = table.item(row, 2).text()

        new_name, ok1 = QInputDialog.getText(self, "Edit Name", "Name:", text=name)
        if not ok1 or not new_name:
            return
        new_amount, ok2 = QInputDialog.getText(
            self, "Edit Amount", "Amount:", text=amount
        )
        if not ok2 or not new_amount:
            return
        new_date, ok3 = QInputDialog.getText(
            self, "Edit Date", "Date (YYYY-MM-DD):", text=date
        )
        if not ok3 or not new_date:
            return

        try:
            new_amount = float(new_amount)
            datetime.strptime(new_date, "%Y-%m-%d")
        except Exception:
            QMessageBox.warning(self, "Invalid Data", "Enter valid amount and date.")
            return

        idx = self.data[
            (self.data["Section"] == section)
            & (self.data["Name"] == name)
            & (self.data["Amount"] == float(amount))
            & (self.data["Date"] == date)
        ].index

        if not idx.empty:
            self.data.at[idx[0], "Name"] = new_name
            self.data.at[idx[0], "Amount"] = new_amount
            self.data.at[idx[0], "Date"] = new_date
            self.save_data()
            self.refresh_table(section)

    def delete_entry(self, section):
        table = self.tabs[section]["table"]
        row = table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "No Selection", "Select a row to delete.")
            return

        name = table.item(row, 0).text()
        amount = float(table.item(row, 1).text())
        date = table.item(row, 2).text()

        self.data = self.data[
            ~(
                (self.data["Section"] == section)
                & (self.data["Name"] == name)
                & (self.data["Amount"] == amount)
                & (self.data["Date"] == date)
            )
        ]
        self.save_data()
        self.refresh_table(section)

    def refresh_table(self, section):
        table = self.tabs[section]["table"]
        df = self.data[self.data["Section"] == section]
        table.setRowCount(len(df))
        for i, row in df.iterrows():
            table.setItem(i, 0, QTableWidgetItem(row["Name"]))
            table.setItem(i, 1, QTableWidgetItem(f"{row['Amount']:.2f}"))
            table.setItem(i, 2, QTableWidgetItem(row["Date"]))

    def create_summary_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        self.summary_label = QLabel()
        layout.addWidget(self.summary_label)
        tab.setLayout(layout)
        self.tabs_widget.addTab(tab, "Summary")
        self.update_summary()

    def update_summary(self):
        total = ""
        for section in SECTIONS:
            section_total = self.data[self.data["Section"] == section]["Amount"].sum()
            total += f"{section}: {section_total:.2f}\n"
        self.summary_label.setText(total)

    def create_chart_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        canvas = FigureCanvas(plt.figure())
        layout.addWidget(canvas)
        tab.setLayout(layout)
        self.tabs_widget.addTab(tab, "Charts")
        self.plot_charts(canvas)

    def plot_charts(self, canvas):
        if self.data.empty:
            return
        df = self.data.copy()
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"])
        monthly = df.groupby(df["Date"].dt.to_period("M"))["Amount"].sum()
        canvas.figure.clear()
        ax = canvas.figure.add_subplot(111)
        monthly.plot(kind="bar", ax=ax)
        ax.set_title("Monthly Cash Flow")
        canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FinanceTracker()
    window.show()
    sys.exit(app.exec())
