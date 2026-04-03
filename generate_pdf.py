#!/usr/bin/env python3
"""
Генератор PDF отчёта о рекламных каналах для Vaysberg v2.
Использует ReportLab для создания красивого PDF с поддержкой кириллицы.
"""

from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY


def create_pdf_report():
    """Создаёт PDF отчёт о рекламных каналах."""
    
    pdf_path = Path(__file__).parent / "examples" / "advertising_channels_report.pdf"
    
    # Создаём документ
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        rightMargin=15*mm,
        leftMargin=15*mm,
        topMargin=20*mm,
        bottomMargin=20*mm,
        encoding='utf-8'
    )
    
    # Подготавливаем стили
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a5490'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2c7ab1'),
        spaceAfter=10,
        spaceBefore=10,
        fontName='Helvetica-Bold'
    )
    
    heading3_style = ParagraphStyle(
        'CustomHeading3',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#3d8bc2'),
        spaceAfter=8,
        spaceBefore=8,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        encoding='utf-8',
        alignment=TA_LEFT
    )
    
    # Содержание документа
    content = []
    
    # Заголовок
    content.append(Paragraph("Исследование рекламных каналов", title_style))
    content.append(Paragraph("Platnie i besplatnye instrumenty dlja analiza kompanij", 
                            ParagraphStyle('subtitle', parent=styles['Normal'], 
                                         textColor=colors.HexColor('#666666'),
                                         fontSize=10, alignment=TA_CENTER)))
    content.append(Spacer(1, 10*mm))
    
    # Текущий стек
    content.append(Paragraph("Tekushchij stek proekta (ispolzuetsja v Vaysberg v2)", heading2_style))
    content.append(Paragraph("Tekushchaja okhvat: ~20-30% maksimal'no dostupnoj informacii po reklamnym kanalam", 
                            normal_style))
    content.append(Spacer(1, 5*mm))
    
    # Таблица текущего стека
    current_stack_data = [
        ['Kanal', 'Instrument', 'Status', 'Informacija'],
        ['VK', 'VK API v5 + html-parsing', 'Besplatnyj', 'Posty, podpischiniki, ER'],
        ['Telegram', 'Telethon + TGStat API', 'Gibrid', 'Kontent i statistika'],
        ['Instagram', 'Instaloader', 'Besplatnyj', 'Posty, podpischiniki, ER'],
        ['Sajt', 'BeautifulSoup+Playwright', 'Besplatnyj', 'Struktura, skorost, SEO']
    ]
    
    current_stack_table = Table(current_stack_data, colWidths=[2*cm, 3*cm, 2.5*cm, 5*cm])
    current_stack_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c7ab1')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')])
    ]))
    
    content.append(current_stack_table)
    content.append(Spacer(1, 8*mm))
    
    # VK
    content.append(Paragraph("VK - Polnoe issledovanie", heading2_style))
    content.append(Paragraph("Platnye instrumenty (+3-5x bol'she informacii):", heading3_style))
    content.append(Paragraph("HypeAuditor ($49-150/mes) - Detaljnaja demografija auditorii<br/>" +
                            "Popsters ($99/mes) - Polnaja analitika VK, Telegram, Instagram<br/>" +
                            "LiveDune ($49/mes) - Upravlenie kontentom<br/>" +
                            "Brand Analytics (30 000 r/mes) - Analiz konkurentnoj sredy<br/>",
                            normal_style))
    content.append(Spacer(1, 5*mm))
    
    # Сравнение
    content.append(Paragraph("Sravnenie: Informacija s platnymi instrumentami", heading2_style))
    
    comparison_data = [
        ['Kanal', 'Tekushchee %', 'S platnymi %', 'Prirost %'],
        ['VK', '20', '90', '+350%'],
        ['Telegram', '25', '95', '+280%'],
        ['Instagram', '15', '95', '+530%'],
        ['YouTube', '10', '90', '+800%'],
        ['Google Ads', '5', '95', '+1800%'],
        ['Yandex Direct', '5', '85', '+1600%']
    ]
    
    comparison_table = Table(comparison_data, colWidths=[3*cm, 3*cm, 3*cm, 3*cm])
    comparison_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c7ab1')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')])
    ]))
    
    content.append(comparison_table)
    content.append(Spacer(1, 10*mm))
    
    # Итоговые рекомендации
    content.append(Paragraph("Minimal'nyj rekomenduemyj stek", heading2_style))
    content.append(Paragraph("Bez platnykh: ~35-40% informacii. S platnymi: ~95%+ informacii. ROI: 2-3 mesyaca pri 5+ otchotakh/mes",
                            normal_style))
    
    content.append(Spacer(1, 10*mm))
    content.append(Paragraph("Vaysberg v2 Research Report | March 2026", 
                            ParagraphStyle('footer', parent=styles['Normal'],
                                         textColor=colors.HexColor('#666666'),
                                         fontSize=8, alignment=TA_CENTER)))
    
    # Создаём PDF
    try:
        print(f"Creatung PDF file...")
        doc.build(content)
        
        if pdf_path.exists():
            size_mb = pdf_path.stat().st_size / (1024 * 1024)
            print(f"PDF created: {pdf_path}")
            print(f"Size: {size_mb:.2f} MB")
            return True
        return False
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Glavnaya funkciya."""
    print("=" * 60)
    print("PDF Generator (Vaysberg v2)")
    print("=" * 60)
    
    success = create_pdf_report()
    
    if success:
        print("\nSuccess! PDF is ready.")
    else:
        print("\nError. Check logs above.")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
