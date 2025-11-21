#!/usr/bin/env python3
"""
PDF Export module for financial performance comparison report
Creates compact, professional PDF reports with charts and statistics
"""

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import io
import pandas as pd
import plotly.graph_objects as go
from plotly.io import to_image


def create_statistics_table(stats):
    """Create a formatted statistics table from stats data"""
    # Table data with header
    data = [['Index', 'Kursanstieg (%)', 'CAGR (%)']]

    for stat in stats:
        data.append([
            stat['name'],
            f"{stat['total_return']:.2f}%",
            f"{stat['cagr']:.2f}%"
        ])

    # Create table
    table = Table(data, colWidths=[3.5*cm, 2.5*cm, 2.5*cm])

    # Apply styling
    table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4da6ff')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),

        # Data rows
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#2a2a2a')),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#e0e0e0')),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#2a2a2a'), colors.HexColor('#353535')]),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#444444')),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))

    return table


def create_performance_chart_image(df, fig_config):
    """Create a Plotly chart and convert to image"""
    fig = go.Figure()

    for index_config in fig_config:
        name = index_config['name']
        if name in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df[name],
                mode='lines',
                name=name,
                line=dict(color=index_config['color'], width=2),
                hovertemplate='%{y:.2f}<extra></extra>'
            ))

    fig.update_layout(
        title='Performance Vergleich (Basis 100 in CHF)',
        xaxis_title='Datum',
        yaxis_title='Indexwert (Basis 100)',
        hovermode='x unified',
        template='plotly_dark',
        plot_bgcolor='#1a1a1a',
        paper_bgcolor='#2a2a2a',
        font=dict(color='#e0e0e0'),
        height=400,
        margin=dict(l=50, r=50, t=50, b=50),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=9)
        )
    )

    # Convert to image
    try:
        img_bytes = to_image(fig, format='png', width=900, height=400)
        return img_bytes
    except Exception as e:
        print(f"Error creating chart image: {e}")
        return None


def generate_pdf_report(filename, df, stats, date_range, fig_config):
    """
    Generate a compact PDF report with performance data

    Args:
        filename: Output PDF filename
        df: DataFrame with performance data
        stats: List of statistics dictionaries
        date_range: Tuple of (start_date, end_date)
        fig_config: List of index configurations with colors
    """

    # Create PDF
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=landscape(A4),
        rightMargin=10*mm,
        leftMargin=10*mm,
        topMargin=10*mm,
        bottomMargin=10*mm
    )

    # Container for PDF elements
    elements = []

    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#4da6ff'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=11,
        textColor=colors.HexColor('#4da6ff'),
        spaceAfter=6,
        spaceBefore=8,
        fontName='Helvetica-Bold'
    )

    text_style = ParagraphStyle(
        'CustomText',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#e0e0e0'),
        spaceAfter=3
    )

    # Title
    title = Paragraph('📊 Index-Performance-Vergleich (CHF, Basis 100)', title_style)
    elements.append(title)

    # Date range info
    start_date, end_date = date_range
    date_text = f"<b>Zeitraum:</b> {start_date} bis {end_date} | <b>Generiert:</b> {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
    elements.append(Paragraph(date_text, text_style))
    elements.append(Spacer(1, 0.3*cm))

    # Create chart image
    chart_img_bytes = create_performance_chart_image(df, fig_config)
    if chart_img_bytes:
        chart_img = Image(io.BytesIO(chart_img_bytes), width=17*cm, height=7.5*cm)
        elements.append(chart_img)
        elements.append(Spacer(1, 0.2*cm))

    # Statistics heading
    elements.append(Paragraph('Performance Statistiken', heading_style))

    # Statistics table
    stats_table = create_statistics_table(stats)
    elements.append(stats_table)
    elements.append(Spacer(1, 0.3*cm))

    # Summary statistics
    elements.append(Paragraph('Zusammenfassung', heading_style))

    # Calculate summary stats
    best_performer = max(stats, key=lambda x: x['cagr'])
    worst_performer = min(stats, key=lambda x: x['cagr'])
    avg_cagr = sum(s['cagr'] for s in stats) / len(stats)

    summary_text = f"""
    <b>Beste Performance (CAGR):</b> {best_performer['name']} mit {best_performer['cagr']:.2f}%<br/>
    <b>Schwächste Performance (CAGR):</b> {worst_performer['name']} mit {worst_performer['cagr']:.2f}%<br/>
    <b>Durchschnittliche CAGR:</b> {avg_cagr:.2f}%<br/>
    <b>Anzahl der Indizes:</b> {len(stats)}
    """
    elements.append(Paragraph(summary_text, text_style))

    # Footer
    elements.append(Spacer(1, 0.4*cm))
    footer_text = "<i>Diese Daten werden von Yahoo Finance bereitgestellt und dienen nur zu Informationszwecken.</i>"
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#888888'),
        alignment=TA_CENTER
    )
    elements.append(Paragraph(footer_text, footer_style))

    # Build PDF
    doc.build(elements)

    # Save to file
    pdf_buffer.seek(0)
    with open(filename, 'wb') as f:
        f.write(pdf_buffer.getvalue())

    return filename


if __name__ == '__main__':
    print("PDF Export module loaded successfully")
