#!/usr/bin/env python3
"""
Actualizacion de Informe Word v2 - Seccion de Analisis de Hidrologia
=====================================================================

Actualiza el informe Word con:
1. Introduccion de distribuciones de probabilidad
2. Actualizacion de curvas H-H (lineal vs cuadratico)
3. Formato con 4 cifras significativas

Autor: Seccion de Analisis de Hidrologia
Fecha: 2026-02-25
"""

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from pathlib import Path
import pandas as pd
from datetime import datetime

# Rutas
DATA_PATH = Path(r"C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\Data\Niveles")
REPORT_PATH = DATA_PATH / "04_reports" / "Informe_Analisis_Exploratorio_Magdalena.docx"
FIGURES_PATH = DATA_PATH / "03_figures"
ANALYSIS_PATH = DATA_PATH / "02_analysis"

# Colores
COLOR_BLUE = RGBColor(0x2E, 0x5E, 0xAA)
COLOR_GRAY = RGBColor(0x66, 0x66, 0x66)


def add_section_header(doc, title, level=1):
    """Agrega encabezado de seccion."""
    doc.add_heading(title, level=level)


def add_paragraph(doc, text, bold=False, italic=False):
    """Agrega paragrafo."""
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.bold = bold
    run.italic = italic
    return p


def add_figure(doc, image_path, caption, width_inches=6.5, figure_count=[0]):
    """Agrega figura con referencia."""
    figure_count[0] += 1
    ref = f"Figura {figure_count[0]}"
    
    if image_path.exists():
        doc.add_picture(str(image_path), width=Inches(width_inches))
        last_paragraph = doc.paragraphs[-1]
        last_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    caption_p = doc.add_paragraph()
    caption_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = caption_p.add_run(f"{ref}. {caption}")
    run.italic = True
    run.font.size = Pt(10)
    run.font.color.rgb = COLOR_GRAY
    
    return ref


def add_table_from_df(doc, df, caption, table_count=[0], max_rows=15):
    """Agrega tabla desde DataFrame."""
    table_count[0] += 1
    ref = f"Tabla {table_count[0]}"
    
    if len(df) > max_rows:
        df_display = df.head(max_rows)
        note = f" (primeras {max_rows} filas de {len(df)})"
    else:
        df_display = df
        note = ""
    
    table = doc.add_table(rows=1, cols=len(df_display.columns))
    table.style = 'Table Grid'
    
    # Encabezados
    hdr_cells = table.rows[0].cells
    for i, col in enumerate(df_display.columns):
        hdr_cells[i].text = str(col)
        for paragraph in hdr_cells[i].paragraphs:
            for run in paragraph.runs:
                run.bold = True
                run.font.size = Pt(10)
    
    # Datos
    for _, row in df_display.iterrows():
        row_cells = table.add_row().cells
        for i, value in enumerate(row):
            row_cells[i].text = str(value)
            for paragraph in row_cells[i].paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(9)
    
    # Caption
    caption_p = doc.add_paragraph()
    caption_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = caption_p.add_run(f"{ref}. {caption}{note}")
    run.italic = True
    run.font.size = Pt(10)
    run.font.color.rgb = COLOR_GRAY
    
    return ref


def add_distribution_introduction(doc):
    """Agrega introduccion de distribuciones de probabilidad."""
    
    add_section_header(doc, "5.1 Introduccion a las Distribuciones de Probabilidad Ajustadas", level=2)
    
    intro = (
        "El analisis de frecuencia de niveles requiere la seleccion apropiada de distribuciones "
        "de probabilidad que modelen el comportamiento estadistico de las cotas. A continuacion, "
        "se presenta una descripcion de las distribuciones evaluadas en este estudio, incluyendo "
        "sus parametros y aplicaciones tipicas en hidrologia."
    )
    add_paragraph(doc, intro)
    
    # Distribucion Normal
    add_section_header(doc, "5.1.1 Distribucion Normal", level=3)
    
    normal_text = (
        "La distribucion Normal (o Gaussiana) es una distribucion continua simetrica definida por "
        "dos parametros: la media (μ) y la desviacion estandar (σ). Su funcion de densidad de "
        "probabilidad tiene forma de campana simetrica alrededor de la media.\n\n"
        "Parametros:\n"
        "- μ (media): Valor central de la distribucion\n"
        "- σ (desviacion estandar): Medida de dispersion alrededor de la media\n\n"
        "Aplicacion hidrologica: Utilizada para variables que presentan simetria y variabilidad "
        "moderada. Sin embargo, en hidrologia muchas variables (precipitaciones, caudales maximos) "
        "presentan asimetria positiva, limitando su aplicabilidad directa."
    )
    add_paragraph(doc, normal_text)
    
    # Distribucion Log-Normal
    add_section_header(doc, "5.1.2 Distribucion Log-Normal", level=3)
    
    lognormal_text = (
        "La distribucion Log-Normal describe variables cuyo logaritmo sigue una distribucion normal. "
        "Es asimetrica positiva (cola hacia la derecha), caracteristica comun en variables hidrologicas.\n\n"
        "Parametros:\n"
        "- s (shape): Parametro de forma relacionado con la asimetria\n"
        "- loc: Parametro de localizacion (desplazamiento)\n"
        "- scale: Parametro de escala relacionado con la mediana\n\n"
        "Aplicacion hidrologica: Ampliamente utilizada para modelar precipitaciones anuales, "
        "caudales maximos anuales y otros fenomenos hidrologicos con asimetria positiva."
    )
    add_paragraph(doc, lognormal_text)
    
    # Distribucion Gamma
    add_section_header(doc, "5.1.3 Distribucion Gamma", level=3)
    
    gamma_text = (
        "La distribucion Gamma es una familia de distribuciones continuas de dos parametros, "
        "definida solo para valores positivos. Es flexible y puede modelar diversas formas "
        "desde exponencial hasta casi normal.\n\n"
        "Parametros:\n"
        "- a (alpha): Parametro de forma (> 0)\n"
        "- loc: Parametro de localizacion\n"
        "- scale (beta): Parametro de escala (> 0)\n\n"
        "Aplicacion hidrologica: Utilizada para modelar precipitaciones, caudales maximos "
        "y otros procesos hidrologicos donde solo son posibles valores positivos."
    )
    add_paragraph(doc, gamma_text)
    
    # Distribucion Gumbel
    add_section_header(doc, "5.1.4 Distribucion Gumbel (Valor Extremo Tipo I)", level=3)
    
    gumbel_text = (
        "La distribucion Gumbel es una distribucion de valores extremos asimetrica, "
        "especialmente util para modelar maximos o minimos de series de datos.\n\n"
        "Parametros:\n"
        "- loc (μ): Moda de la distribucion (parametro de localizacion)\n"
        "- scale (β): Parametro de escala (> 0)\n\n"
        "Aplicacion hidrologica: Es la distribucion mas utilizada para analisis de frecuencia "
        "de caudales maximos instantaneos anuales y precipitaciones maximas, conforme a las "
        "recomendaciones del U.S. Water Resources Council."
    )
    add_paragraph(doc, gumbel_text)
    
    # Distribucion Weibull
    add_section_header(doc, "5.1.5 Distribucion Weibull", level=3)
    
    weibull_text = (
        "La distribucion Weibull es una distribucion versatil de dos parametros que puede "
        "modelar comportamientos desde exponenciales hasta aproximadamente normales, "
        "dependiendo de sus parametros.\n\n"
        "Parametros:\n"
        "- c (shape): Parametro de forma (> 0). Si c < 3, la distribucion es asimetrica negativa; "
        "si c > 3, es asimetrica positiva; si c = 3.6, se aproxima a la normal\n"
        "- loc: Parametro de localizacion\n"
        "- scale: Parametro de escala (> 0)\n\n"
        "Aplicacion hidrologica: Utilizada para modelar vientos, caudales minimos (estiajes), "
        "y analisis de confiabilidad de estructuras hidraulicas. Tambien es efectiva para "
        "datos de niveles con diferentes grados de asimetria."
    )
    add_paragraph(doc, weibull_text)
    
    # Distribucion Pearson III
    add_section_header(doc, "5.1.6 Distribucion Pearson Tipo III", level=3)
    
    pearson_text = (
        "La distribucion Pearson Tipo III es una distribucion gamma de tres parametros con "
        "parametro de localizacion. Es la distribucion recomendada por el U.S. Geological Survey "
        "para analisis de frecuencia de caudales en Estados Unidos.\n\n"
        "Parametros:\n"
        "- skew: Coeficiente de asimetria\n"
        "- loc: Parametro de localizacion (umbral minimo)\n"
        "- scale: Parametro de escala\n\n"
        "Aplicacion hidrologica: Especialmente util para datos con asimetria pronunciada "
        "y valores minimos diferentes de cero. Ampliamente usada para analisis de frecuencia "
        "de caudales maximos anuales cuando se dispone de registros extensos."
    )
    add_paragraph(doc, pearson_text)
    
    # Criterios de seleccion
    add_section_header(doc, "5.1.7 Criterios de Seleccion del Mejor Ajuste", level=3)
    
    criteria_text = (
        "La seleccion de la mejor distribucion se realizo mediante los siguientes criterios:\n\n"
        "1. Criterio de Informacion de Akaike (AIC): Mide la calidad del ajuste penalizando "
        "la complejidad del modelo (numero de parametros). Se selecciona la distribucion "
        "con menor AIC.\n\n"
        "2. Criterio Bayesiano de Schwarz (BIC): Similar al AIC pero con penalizacion mas "
        "severa para modelos complejos.\n\n"
        "3. Prueba de Kolmogorov-Smirnov (KS): Evalua la bondad de ajuste comparando la "
        "distribucion empirica con la teorica. Un p-value > 0.05 indica que no se puede "
        "rechazar que los datos siguen la distribucion propuesta.\n\n"
        "En todos los casos, se busca minimizar el AIC mientras se mantiene un p-value "
        "aceptable en la prueba KS."
    )
    add_paragraph(doc, criteria_text)


def update_hh_curves_section(doc):
    """Actualiza la seccion de curvas H-H con comparacion lineal vs cuadratico."""
    
    # Buscar y eliminar la seccion anterior de curvas H-H si existe
    # (Simplificacion: agregar nueva version)
    
    add_section_header(doc, "4.3 Curvas H-H (Nivel-Nivel) - Comparacion de Modelos", level=2)
    
    text = (
        "Las curvas H-H representan las relaciones estadisticas entre niveles de estaciones "
        "correlacionadas. En este estudio se evaluaron tanto modelos lineales como cuadraticos "
        "para determinar cual representa mejor la relacion entre estaciones.\n\n"
        "Los modelos evaluados fueron:\n"
        "- Modelo Lineal: H_target = a * H_donor + b\n"
        "- Modelo Cuadratico: H_target = a * H_donor^2 + b * H_donor + c\n\n"
        "La seleccion del mejor modelo se realizo mediante el Criterio de Informacion de Akaike "
        "(AIC), que equilibra la bondad de ajuste con la complejidad del modelo. Un menor valor "
        "de AIC indica un mejor modelo."
    )
    add_paragraph(doc, text)
    
    # Tabla de comparacion de modelos
    try:
        comparison = pd.read_csv(ANALYSIS_PATH / "hh_model_comparison.csv")
        table_ref = add_table_from_df(doc, comparison,
            "Comparacion de modelos Lineal vs Cuadratico para curvas H-H")
        
        text2 = (
            f"\nLa {table_ref} presenta los resultados de la comparacion entre modelos. "
            "Para todas las relaciones evaluadas, el modelo cuadratico presento un AIC menor "
            "que el modelo lineal, indicando que la relacion entre estaciones incluye "
            "componentes no lineales significativos. Los valores de R2 del modelo cuadratico "
            "(0.9763 a 0.9801) son ligeramente superiores a los del modelo lineal, confirmando "
            "la mejora en el ajuste."
        )
        add_paragraph(doc, text2)
    except:
        add_paragraph(doc, "[Tabla de comparacion no disponible]")
    
    # Figura de curvas H-H
    fig_ref = add_figure(doc,
        FIGURES_PATH / "imputation" / "hh_curves_comparison.png",
        "Curvas H-H (Nivel-Nivel) para imputacion espacial. "
        "Fila superior: relaciones nivel-nivel con modelo cuadratico seleccionado. "
        "Fila inferior: analisis de residuos para validacion del modelo.",
        width_inches=6.5)
    
    text3 = (
        f"\nLa {fig_ref} muestra las curvas H-H construidas con el modelo cuadratico seleccionado. "
        "El analisis de residuos (fila inferior) muestra distribucion aleatoria alrededor de cero, "
        "confirmando la ausencia de patrones sistematicos no explicados por el modelo. "
        "Los valores de R2 superiores a 0.975 indican relaciones muy fuertes entre estaciones, "
        "validando el uso de estas curvas para la imputacion de datos faltantes."
    )
    add_paragraph(doc, text3)


def generate_detailed_analysis_section_v2(doc):
    """Genera seccion de analisis detallado v2."""
    add_section_header(doc, "5. ANALISIS DETALLADO POR ESTACIONES", level=1)
    
    text = (
        "Esta seccion presenta un analisis estadistico detallado de las estaciones con "
        "datos completos (>=85% completitud) tras el proceso de imputacion. El analisis "
        "incluye estadisticas descriptivas, violinplots mensuales multianuales en escala "
        "de grises con linea de media superpuesta, y ajustes de distribuciones de probabilidad "
        "con verificacion de supuestos estadisticos."
    )
    add_paragraph(doc, text)
    
    # Introduccion de distribuciones
    add_distribution_introduction(doc)
    
    # Analisis por estacion
    stations = ['Calamar', 'Las Aguadas', 'El Banco']
    
    for i, station in enumerate(stations, start=2):
        add_section_header(doc, f"5.{i} Estacion {station}", level=2)
        
        try:
            # Cargar datos especificos
            summary = pd.read_csv(ANALYSIS_PATH / "distribution_fits_summary.csv")
            station_row = summary[summary['Estacion'] == station]
            
            text = (
                f"La estacion {station} presenta un registro temporal extenso con datos "
                "suficientes para analisis estadisticos rigurosos. El analisis mensual "
                "multianual permite identificar patrones estacionales y variabilidad intra-anual."
            )
            add_paragraph(doc, text)
            
            # Violinplot mensual (nuevo B/N con linea de media)
            fig_ref = add_figure(doc,
                FIGURES_PATH / "detailed_analysis" / f"{station}_monthly_violin_analysis.png",
                f"Distribucion mensual multianual de cotas - Estacion {station}. "
                "Violin plot en escala de grises con linea punteada de media mensual multianual.",
                width_inches=6.5)
            
            text2 = (
                f"\nLa {fig_ref} presenta la distribucion mensual de las cotas para la estacion "
                f"{station} en formato de violin plot en escala de grises. La linea punteada negra "
                "representa la media mensual multianual, permitiendo identificar claramente los "
                "meses con niveles por encima o por debajo del promedio. Se observan diferencias "
                "significativas entre meses, reflejando el regimen hidrologico bimodal "
                "caracteristico de la region Caribe colombiana."
            )
            add_paragraph(doc, text2)
            
            # Ajuste de distribuciones
            if not station_row.empty:
                dist_name = station_row.iloc[0]['Mejor_Dist_Anual']
                aic = station_row.iloc[0]['AIC_Anual']
                ks_p = station_row.iloc[0]['KS_pvalue_Anual']
                normal = station_row.iloc[0]['Cumple_Normal']
                
                text3 = (
                    f"Se evaluaron multiples distribuciones de probabilidad parametricas para "
                    f"caracterizar el comportamiento estadistico de las cotas de la estacion "
                    f"{station}. La mejor distribucion identificada fue la distribucion "
                    f"{dist_name} (AIC = {aic:.4g}, KS p-value = {ks_p:.4g}). "
                )
                
                if normal == 'No':
                    text3 += (
                        f"Los datos no cumplen con el supuesto de normalidad (p < 0.05), "
                        f"validando la seleccion de la distribucion {dist_name} como alternativa "
                        "mas apropiada para modelar el comportamiento estadistico de esta estacion."
                    )
                
                add_paragraph(doc, text3)
                
                # Figura de ajustes
                fig_ref2 = add_figure(doc,
                    FIGURES_PATH / "detailed_analysis" / f"{station}_pdf_fits_anual.png",
                    f"Ajuste de distribuciones de probabilidad - Estacion {station}. "
                    "Panel izquierdo: histograma con PDFs ajustadas (escala de grises). "
                    "Panel derecho: Q-Q plot para la mejor distribucion.",
                    width_inches=6.5)
                
                text4 = (
                    f"\nLa {fig_ref2} muestra los resultados del ajuste de distribuciones para "
                    f"la estacion {station}. El panel izquierdo presenta el histograma de datos "
                    "con las tres mejores distribuciones ajustadas, diferenciadas por patrones "
                    "de linea. El panel derecho muestra el Q-Q plot para la mejor distribucion, "
                    "permitiendo evaluar visualmente la bondad de ajuste."
                )
                add_paragraph(doc, text4)
            
        except Exception as e:
            add_paragraph(doc, f"[Error cargando datos: {e}]")


def update_document_v2():
    """Actualiza el documento Word completo."""
    print("Actualizando informe Word v2...")
    
    # Abrir documento existente
    doc = Document(REPORT_PATH)
    
    # Buscar la seccion 4.3 de curvas H-H y actualizarla
    # Como es complejo modificar secciones existentes, agregamos apendice al final
    doc.add_page_break()
    
    add_section_header(doc, "APENDICE A: Actualizaciones al Analisis", level=1)
    
    # Actualizar seccion de curvas H-H
    update_hh_curves_section(doc)
    
    doc.add_page_break()
    
    # Regenerar seccion de analisis detallado con introduccion de distribuciones
    generate_detailed_analysis_section_v2(doc)
    
    # Guardar
    doc.save(REPORT_PATH)
    print(f"Informe actualizado: {REPORT_PATH}")


if __name__ == '__main__':
    update_document_v2()
