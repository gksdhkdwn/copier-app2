import sys
import os
import io
import win32print
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QFileDialog, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QMessageBox, QComboBox, QCheckBox, QLabel, 
                             QAbstractItemView, QMenu)
from PyQt5.QtCore import Qt
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from pdf2image import convert_from_bytes
import fitz  # PyMuPDF

# PyInstaller 환경 설정
def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

poppler_path = get_resource_path("poppler/bin")

# --- 라벨 출력 서식 (PDF 생성용 함수) ---
def txt_samsung(c, row, font_name, title_color):
    c.setLineWidth(1.5)
    c.rect(10, 10, 263, 188)
    
    c.setFont(font_name, 15)
    c.drawCentredString(141, 175, "[ 복합기 소모품 교체 ]")
    
    c.setLineWidth(1)
    c.line(20, 168, 263, 168)
    
    y = 145
    labels = ["제품 모델명 :", "카트리지 모델 :", "장 착 위 치 :", "배 송 지 :", "고 객 명 :", "연 락 처 :"]
    keys = ['기종', '카트리지', '설치위치', '배송지', '고객명', '연락처']
    
    for label, key in zip(labels, keys):
        c.setFont(font_name, 12)
        c.drawString(20, y, label)
        
        val = str(row.get(key, ''))
        if key == '설치위치':
            style = ParagraphStyle('BoldStyle', fontName=font_name, fontSize=14, leading=16, textColor=colors.red)
            p = Paragraph(f"<b>{val}</b>", style)
            p.wrapOn(c, 160, 30)
            p.drawOn(c, 105, y - 2)
        elif key in ['고객명', '연락처']:
            style = ParagraphStyle('DarkStyle', fontName=font_name, fontSize=12, leading=14, textColor=colors.HexColor('#000080'))
            p = Paragraph(f"<b>{val}</b>", style)
            p.wrapOn(c, 160, 30)
            p.drawOn(c, 105, y)
        else:
            style = ParagraphStyle('NormalStyle', fontName=font_name, fontSize=11, leading=13)
            p = Paragraph(val, style)
            p.wrapOn(c, 160, 30)
            p.drawOn(c, 105, y)
            
        y -= 21

def txt_sinoh(c, row, font_name, title_color):
    c.setLineWidth(1.5)
    c.rect(10, 10, 263, 188)
    
    c.setFont(font_name, 15)
    c.drawCentredString(141, 175, "[ 복합기 토너 교체 ]")
    
    c.setLineWidth(1)
    c.line(20, 168, 263, 168)
    
    y = 145
    labels = ["제품 모델명 :", "토 너 색 상 :", "장 착 위 치 :", "배 송 지 :", "고 객 명 :", "연 락 처 :"]
    keys = ['기종', '카트리지', '설치위치', '배송지', '고객명', '연락처']
    
    for label, key in zip(labels, keys):
        c.setFont(font_name, 12)
        c.drawString(20, y, label)
        
        val = str(row.get(key, ''))
        if key == '설치위치':
            style = ParagraphStyle('BoldStyle', fontName=font_name, fontSize=14, leading=16, textColor=colors.red)
            p = Paragraph(f"<b>{val}</b>", style)
            p.wrapOn(c, 160, 30)
            p.drawOn(c, 105, y - 2)
        elif key in ['고객명', '연락처']:
            style = ParagraphStyle('DarkStyle', fontName=font_name, fontSize=12, leading=14, textColor=colors.HexColor('#000080'))
            p = Paragraph(f"<b>{val}</b>", style)
            p.wrapOn(c, 160, 30)
            p.drawOn(c, 105, y)
        else:
            style = ParagraphStyle('NormalStyle', fontName=font_name, fontSize=11, leading=13)
            p = Paragraph(val, style)
            p.wrapOn(c, 160, 30)
            p.drawOn(c, 105, y)
            
        y -= 21

def txt_ecosys(c, row, font_name, title_color):
    txt_sinoh(c, row, font_name, title_color)

def txt_kyocera_m2101(c, row, font_name, title_color):
    c.setLineWidth(1.5)
    c.rect(10, 10, 263, 188)
    
    c.setFont(font_name, 15)
    c.setFillColor(title_color)
    c.drawCentredString(141, 175, "[ 토너 교체 안내 ]")
    
    c.setLineWidth(1)
    c.setStrokeColor(colors.black)
    c.line(20, 168, 263, 168)
    
    y = 145
    labels = ["제품 모델명 :", "토 너 색 상 :", "장 착 위 치 :", "배 송 지 :", "고 객 명 :", "연 락 처 :"]
    keys = ['기종', '카트리지', '설치위치', '배송지', '고객명', '연락처']
    
    for label, key in zip(labels, keys):
        c.setFillColor(colors.black)
        c.setFont(font_name, 12)
        c.drawString(20, y, label)
        
        val = str(row.get(key, ''))
        if key == '설치위치':
            style = ParagraphStyle('BoldStyle', fontName=font_name, fontSize=14, leading=16, textColor=colors.red)
            p = Paragraph(f"<b>{val}</b>", style)
            p.wrapOn(c, 160, 30)
            p.drawOn(c, 105, y - 2)
        elif key in ['고객명', '연락처']:
            style = ParagraphStyle('DarkStyle', fontName=font_name, fontSize=12, leading=14, textColor=colors.HexColor('#000080'))
            p = Paragraph(f"<b>{val}</b>", style)
            p.wrapOn(c, 160, 30)
            p.drawOn(c, 105, y)
        else:
            style = ParagraphStyle('NormalStyle', fontName=font_name, fontSize=11, leading=13)
            p = Paragraph(val, style)
            p.wrapOn(c, 160, 30)
            p.drawOn(c, 105, y)
            
        y -= 21

def txt_305(c, row, font_name, title_color):
    txt_kyocera_m2101(c, row, font_name, title_color)

def txt_5473(c, row, font_name, title_color):
    c.setLineWidth(1.5)
    c.rect(10, 10, 263, 188)
    
    c.setFont(font_name, 15)
    c.setFillColor(title_color)
    c.drawCentredString(141, 175, "[ 토너 교체 안내 ]")
    
    c.setLineWidth(1)
    c.setStrokeColor(colors.black)
    c.line(20, 168, 263, 168)
    
    y = 145
    labels = ["제품 모델명 :", "토 너 색 상 :", "장 착 위 치 :", "배 송 지 :", "고 객 명 :", "연 락 처 :"]
    keys = ['기종', '카트리지', '설치위치', '배송지', '고객명', '연락처']
    
    for label, key in zip(labels, keys):
        c.setFillColor(colors.black)
        c.setFont(font_name, 12)
        c.drawString(20, y, label)
        
        val = str(row.get(key, ''))
        if key == '설치위치':
            style = ParagraphStyle('BoldStyle', fontName=font_name, fontSize=14, leading=16, textColor=colors.red)
            p = Paragraph(f"<b>{val}</b>", style)
            p.wrapOn(c, 160, 30)
            p.drawOn(c, 105, y - 2)
        elif key in ['고객명', '연락처']:
            style = ParagraphStyle('DarkStyle', fontName=font_name, fontSize=12, leading=14, textColor=colors.HexColor('#000080'))
            p = Paragraph(f"<b>{val}</b>", style)
            p.wrapOn(c, 160, 30)
            p.drawOn(c, 105, y)
        else:
            style = ParagraphStyle('NormalStyle', fontName=font_name, fontSize=11, leading=13)
            p = Paragraph(val, style)
            p.wrapOn(c, 160, 30)
            p.drawOn(c, 105, y)
            
        y -= 21

# 기종 매핑 및 폼 자동선택 매핑
DEFAULT_FORMATS = {
    "SL-": txt_samsung, "CLX": txt_samsung, "MultiXpress": txt_samsung, "SAMSUNG": txt_samsung,
    "N60": txt_sinoh, "D400": txt_sinoh, "D410": txt_sinoh, "D420": txt_sinoh, "D450": txt_sinoh, 
    "C224": txt_sinoh, "C284": txt_sinoh, "C364": txt_sinoh, "C225": txt_sinoh, "SINOH": txt_sinoh,
    "MA2100": txt_ecosys, "M5526": txt_ecosys, "M5521": txt_ecosys, "ECOSYS": txt_ecosys, 
    "MA2101": txt_kyocera_m2101, 
    "305": txt_305, "5473": txt_5473, 
}

class LabelPrinterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.df = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("택배 라벨 자동 출력 프로그램 (100x75mm)")
        self.resize(1000, 600)
        
        main_layout = QVBoxLayout()
        
        # 상단 컨트롤 레이아웃
        top_layout = QHBoxLayout()
        
        self.btn_excel = QPushButton("엑셀 파일 불러오기")
        self.btn_excel.clicked.connect(self.load_excel)
        top_layout.addWidget(self.btn_excel)
        
        top_layout.addWidget(QLabel("프린터 선택:"))
        self.cb_printer = QComboBox()
        self.load_printers()
        top_layout.addWidget(self.cb_printer)
        
        self.chk_auto = QCheckBox("자동 서식 매핑 사용")
        self.chk_auto.setChecked(True)
        top_layout.addWidget(self.chk_auto)
        
        self.btn_print_all = QPushButton("선택 항목 인쇄")
        self.btn_print_all.clicked.connect(self.print_selected)
        top_layout.addWidget(self.btn_print_all)
        
        main_layout.addLayout(top_layout)
        
        # 테이블 위젯
        self.table = QTableWidget()
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.open_context_menu)
        main_layout.addWidget(self.table)
        
        self.setLayout(main_layout)

    def load_printers(self):
        printers = [printer[2] for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
        default_printer = win32print.GetDefaultPrinter()
        self.cb_printer.addItems(printers)
        if default_printer in printers:
            self.cb_printer.setCurrentText(default_printer)

    def load_excel(self):
        fname, _ = QFileDialog.getOpenFileName(self, "엑셀 파일 선택", "", "Excel Files (*.xlsx *.xls)")
        if fname:
            try:
                self.df = pd.read_excel(fname)
                self.populate_table()
            except Exception as e:
                QMessageBox.critical(self, "오류", f"엑셀 파일을 읽는 중 오류가 발생했습니다:\n{str(e)}")

    def populate_table(self):
        if self.df is None:
            return
            
        self.table.setRowCount(0)
        cols = list(self.df.columns)
        
        # 선택 컬럼과 서식 선택 컬럼 추가
        headers = ["선택"] + cols + ["출력 서식"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        
        format_options = ["삼성", "신도리코", "교세라 ECOSYS", "교세라 MA2101", "교세라 305", "교세라 5473"]
        
        for row_idx, row in self.df.iterrows():
            self.table.insertRow(row_idx)
            
            # 체크박스
            chk = QCheckBox()
            chk.setChecked(True)
            self.table.setCellWidget(row_idx, 0, chk)
            
            # 데이터 채우기
            for col_idx, col_name in enumerate(cols):
                val = str(row[col_name]) if pd.notna(row[col_name]) else ""
                item = QTableWidgetItem(val)
                self.table.setItem(row_idx, col_idx + 1, item)
                
            # 서식 콤보박스
            cb_fmt = QComboBox()
            cb_fmt.addItems(format_options)
            
            # 자동 매핑
            model = str(row.get('기종', ''))
            matched = False
            for key, fmt_func in DEFAULT_FORMATS.items():
                if key.lower() in model.lower():
                    if fmt_func == txt_samsung: cb_fmt.setCurrentText("삼성")
                    elif fmt_func == txt_sinoh: cb_fmt.setCurrentText("신도리코")
                    elif fmt_func == txt_ecosys: cb_fmt.setCurrentText("교세라 ECOSYS")
                    elif fmt_func == txt_kyocera_m2101: cb_fmt.setCurrentText("교세라 MA2101")
                    elif fmt_func == txt_305: cb_fmt.setCurrentText("교세라 305")
                    elif fmt_func == txt_5473: cb_fmt.setCurrentText("교세라 5473")
                    matched = True
                    break
            if not matched:
                cb_fmt.setCurrentText("삼성")
                
            self.table.setCellWidget(row_idx, len(headers) - 1, cb_fmt)
            
        self.table.header().setSectionResizeMode(QHeaderView.ResizeToContents)

    def open_context_menu(self, position):
        menu = QMenu()
        select_all = menu.addAction("전체 선택")
        deselect_all = menu.addAction("전체 해제")
        action = menu.exec_(self.table.viewport().mapToGlobal(position))
        
        if action == select_all:
            for r in range(self.table.rowCount()):
                widget = self.table.cellWidget(r, 0)
                if isinstance(widget, QCheckBox):
                    widget.setChecked(True)
        elif action == deselect_all:
            for r in range(self.table.rowCount()):
                widget = self.table.cellWidget(r, 0)
                if isinstance(widget, QCheckBox):
                    widget.setChecked(False)

    def print_selected(self):
        printer_name = self.cb_printer.currentText()
        if not printer_name:
            QMessageBox.warning(self, "경고", "프린터를 선택해주세요.")
            return

        fmt_map = {
            "삼성": txt_samsung,
            "신도리코": txt_sinoh,
            "교세라 ECOSYS": txt_ecosys,
            "교세라 MA2101": txt_kyocera_m2101,
            "교세라 305": txt_305,
            "교세라 5473": txt_5473
        }

        cols = list(self.df.columns) if self.df is not None else []
        printed_count = 0

        for r in range(self.table.rowCount()):
            chk = self.table.cellWidget(r, 0)
            if chk and chk.isChecked():
                row_data = {}
                for c_idx, c_name in enumerate(cols):
                    item = self.table.item(r, c_idx + 1)
                    row_data[c_name] = item.text() if item else ""
                
                cb_fmt = self.table.cellWidget(r, self.table.columnCount() - 1)
                fmt_str = cb_fmt.currentText()
                fmt_func = fmt_map.get(fmt_str, txt_samsung)
                
                self.generate_and_print(row_data, fmt_func, printer_name)
                printed_count += 1

        if printed_count > 0:
            QMessageBox.information(self, "완료", f"{printed_count}개의 라벨 출력이 완료되었습니다.")
        else:
            QMessageBox.warning(self, "경고", "선택된 항목이 없습니다.")

    def generate_and_print(self, row_data, fmt_func, printer_name):
        buffer = io.BytesIO()
        # 100mm x 75mm 크기 (포인트 단위: 1mm = 2.83465 pt)
        w_pt = 100 * 2.83465
        h_pt = 75 * 2.83465
        
        c = canvas.Canvas(buffer, pagesize=(w_pt, h_pt))
        
        # 폰트 등록 (한글 지원)
        try:
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            pdfmetrics.registerFont(TTFont('Malgun', 'malgun.ttf'))
            font_name = 'Malgun'
        except:
            font_name = 'Helvetica'

        fmt_func(c, row_data, font_name, colors.black)
        c.showPage()
        c.save()
        
        buffer.seek(0)
        pdf_bytes = buffer.getvalue()

        # PDF -> 이미지 변환 후 프린터 전송
        try:
            images = convert_from_bytes(pdf_bytes, poppler_path=poppler_path if os.path.exists(poppler_path) else None)
            for img in images:
                bmp_buffer = io.BytesIO()
                img.save(bmp_buffer, format='BMP')
                bmp_bytes = bmp_buffer.getvalue()
                
                hprinter = win32print.OpenPrinter(printer_name)
                try:
                    hdc = win32print.StartDocPrinter(hprinter, 1, ("Label Print", None, "RAW"))
                    win32print.StartPagePrinter(hprinter)
                    win32print.WritePrinter(hprinter, bmp_bytes)
                    win32print.EndPagePrinter(hprinter)
                    win32print.EndDocPrinter(hprinter)
                finally:
                    win32print.ClosePrinter(hprinter)
        except Exception as e:
            print(f"출력 실패: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = LabelPrinterApp()
    ex.show()
    sys.exit(app.exec_())
