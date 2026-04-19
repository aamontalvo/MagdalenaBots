#!/usr/bin/env python3
"""
Generador de Reporte Word - Análisis Exploratorio Magdalena
===========================================================

Genera documentos Word profesionales con:
- Explicaciones previas a cada gráfico
- Referencias cruzadas a tablas y figuras
- Análisis hidrológico experto

Autor: MagdalenaBot Hydrology Team
"""

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from pathlib import Path
import pandas as pd
from datetime import datetime

# Rutas
OUTPUT_PATH = Path(r"C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\analysis_output")
REPORT_PATH = OUTPUT_PATH / 'Informe_Analisis_Exploratorio_Magdalena.docx'

# Constantes de formato
TITLE_FONT = 'Calibri Light'
BODY_FONT = 'Calibri'
COLOR_BLUE = RGBColor(0x2E, 0x5E, 0xAA)  # Azul corporativo
COLOR_GRAY = RGBColor(0x66, 0x66, 0x66)


class MagdalenaReportGenerator:
    """Generador de informes técnicos en Word."""
    
    def __init__(self):
        self.doc = Document()
        self.figure_count = 0
        self.table_count = 0
        self._setup_styles()
        
    def _setup_styles(self):
        """Configura estilos personalizados del documento."""
        # Estilo para títulos
        style = self.doc.styles['Heading 1']
        font = style.font
        font.name = TITLE_FONT
        font.size = Pt(18)
        font.bold = True
        font.color.rgb = COLOR_BLUE
        
        # Estilo para subtítulos
        style = self.doc.styles['Heading 2']
        font = style.font
        font.name = TITLE_FONT
        font.size = Pt(14)
        font.bold = True
        font.color.rgb = COLOR_BLUE
        
        # Estilo para body
        style = self.doc.styles['Normal']
        font = style.font
        font.name = BODY_FONT
        font.size = Pt(11)
        
    def add_title_page(self):
        """Agrega portada del informe."""
        # Título principal
        title = self.doc.add_heading('ANÁLISIS EXPLORATORIO DE DATOS', level=0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        subtitle = self.doc.add_heading(
            'Series Temporales de Niveles del Río Magdalena', level=1)
        subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Espacio
        self.doc.add_paragraph()
        
        # Detalles
        info = self.doc.add_paragraph()
        info.alignment = WD_ALIGN_PARAGRAPH.CENTER
        info.add_run('Fuente: IDEAM - Series de Niveles 1967-2026\n').bold = True
        info.add_run(f'Fecha de generación: {datetime.now().strftime("%d de %B de %Y")}\n')
        info.add_run('Elaborado por: MagdalenaBot Hydrology Team')
        
        # Salto de página
        self.doc.add_page_break()
        
    def add_section_header(self, title: str, level: int = 1):
        """Agrega encabezado de sección."""
        self.doc.add_heading(title, level=level)
        
    def add_paragraph(self, text: str, bold: bool = False, italic: bool = False):
        """Agrega párrafo de texto."""
        p = self.doc.add_paragraph()
        run = p.add_run(text)
        run.bold = bold
        run.italic = italic
        return p
        
    def add_figure(self, image_path: Path, caption: str, 
                   width_inches: float = 6.5) -> str:
        """
        Agrega figura con referencia cruzada.
        
        Returns:
            Referencia de figura (ej: "Figura 1")
        """
        self.figure_count += 1
        ref = f"Figura {self.figure_count}"
        
        # Agregar imagen
        if image_path.exists():
            self.doc.add_picture(str(image_path), width=Inches(width_inches))
            last_paragraph = self.doc.paragraphs[-1]
            last_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Caption
        caption_p = self.doc.add_paragraph()
        caption_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = caption_p.add_run(f"{ref}. {caption}")
        run.italic = True
        run.font.size = Pt(10)
        run.font.color.rgb = COLOR_GRAY
        
        return ref
        
    def add_table(self, df: pd.DataFrame, caption: str, 
                  max_rows: int = 20) -> str:
        """
        Agrega tabla con datos de DataFrame.
        
        Returns:
            Referencia de tabla (ej: "Tabla 1")
        """
        self.table_count += 1
        ref = f"Tabla {self.table_count}"
        
        # Limitar filas si es necesario
        if len(df) > max_rows:
            df_display = df.head(max_rows)
            note = f" (mostrando primeras {max_rows} filas de {len(df)})"
        else:
            df_display = df
            note = ""
        
        # Crear tabla
        table = self.doc.add_table(rows=1, cols=len(df_display.columns))
        table.style = 'Table Grid'
        
        # Encabezados
        hdr_cells = table.rows[0].cells
        for i, col in enumerate(df_display.columns):
            hdr_cells[i].text = str(col)
            # Formato encabezado
            for paragraph in hdr_cells[i].paragraphs:
                for run in paragraph.runs:
                    run.bold = True
                    run.font.size = Pt(10)
        
        # Datos
        for _, row in df_display.iterrows():
            row_cells = table.add_row().cells
            for i, value in enumerate(row):
                row_cells[i].text = str(value)
                # Formato celdas
                for paragraph in row_cells[i].paragraphs:
                    for run in paragraph.runs:
                        run.font.size = Pt(9)
        
        # Caption
        caption_p = self.doc.add_paragraph()
        caption_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = caption_p.add_run(f"{ref}. {caption}{note}")
        run.italic = True
        run.font.size = Pt(10)
        run.font.color.rgb = COLOR_GRAY
        
        return ref
        
    def generate_executive_summary(self, summary_df: pd.DataFrame):
        """Genera resumen ejecutivo."""
        self.add_section_header("1. RESUMEN EJECUTIVO")
        
        # Análisis de cobertura
        total_stations = len(summary_df)
        avg_completeness = summary_df['Completitud_Pct'].mean()
        oldest_station = summary_df.loc[summary_df['Anio_Inicio'].idxmin()]
        
        text = (
            f"El presente informe presenta el análisis exploratorio de datos de niveles "
            f"del río Magdalena correspondientes a {total_stations} estaciones del IDEAM, "
            f"con un período de registro que abarca desde {summary_df['Anio_Inicio'].min()} "
            f"hasta {summary_df['Anio_Fin'].max()}. "
            f"La estación con mayor antigüedad es {oldest_station['Estacion']} "
            f"(código {oldest_station['Codigo']}), la cual inició operaciones en {int(oldest_station['Anio_Inicio'])}.\n\n"
            
            f"La calidad de datos general presenta una completitud promedio del "
            f"{avg_completeness:.1f}%, con variaciones significativas entre estaciones. "
            f"Las estaciones ubicadas aguas abajo tienden a tener registros más completos, "
            f"mientras que algunas estaciones intermedias presentan mayores porcentajes de "
            f"datos faltantes, posiblemente asociados a interrupciones operativas o "
            f"fallas en los equipos de medición.\n\n"
            
            f"El análisis de valores atípicos (outliers) revela la presencia de mediciones "
            f"extremas que requieren validación hidrológica para determinar si corresponden "
            f"a eventos reales (crecidas extremas, estiajes severos) o errores de medición."
        )
        
        self.add_paragraph(text)
        
    def generate_data_quality_section(self, summary_df: pd.DataFrame):
        """Genera sección de calidad de datos."""
        self.add_section_header("2. ANÁLISIS DE CALIDAD DE DATOS")
        self.add_section_header("2.1 Cobertura Temporal y Datos Faltantes", level=2)
        
        # Texto introductorio
        text_intro = (
            "La evaluación de la cobertura temporal constituye el primer paso fundamental "
            "en cualquier análisis hidrológico, ya que determina la confiabilidad de las "
            "conclusiones que puedan derivarse de los datos. En esta sección se presenta "
            "un análisis exhaustivo de la disponibilidad de registros por estación y año.\n\n"
            
            "El mapa de calor presentado en la "
        )
        p = self.add_paragraph(text_intro)
        
        # Aquí agregaríamos la referencia a la figura después de crearla
        heatmap_path = OUTPUT_PATH / 'heatmap_nulls.png'
        fig_ref = self.add_figure(
            heatmap_path,
            "Mapa de calor de datos faltantes por estación y año. "
            "El eje vertical presenta las estaciones ordenadas geográficamente desde "
            "aguas arriba (Barrancabermeja) hasta aguas abajo (Tebsa). "
            "La intensidad del color azul indica la cantidad de días sin datos. "
            "Las marcas en X indican años anteriores a la instalación de la estación.",
            width_inches=6.5
        )
        
        # Continuar texto
        text_analysis = (
            f"{fig_ref} permite identificar patrones sistemáticos en la falta de datos. "
            "Se observa que la estación Calamar presenta el registro más antiguo y continuo, "
            "iniciando en 1967, lo cual la convierte en una estación de referencia para "
            "análisis de tendencias a largo plazo. En contraste, estaciones como El Contento "
            "y Gamarra Aut muestran registros más recientes, limitando su utilidad para "
            "análisis históricos pero siendo valiosas para estudios de eventos recientes.\n\n"
            
            "Los períodos de datos faltantes concentrados (bloques azules intensos) "
            "sugieren interrupciones operativas significativas, posiblemente asociadas a: "
            "(a) mantenimiento de equipos, (b) daños por eventos extremos (inundaciones), "
            "o (c) cambios en la política de monitoreo del IDEAM."
        )
        self.add_paragraph(text_analysis)
        
        # Agregar tabla resumen
        table_ref = self.add_table(
            summary_df[['Estacion', 'Codigo', 'Anio_Inicio', 'Anio_Fin', 'Total_Anios', 'Completitud_Pct']],
            "Resumen de cobertura temporal por estación",
            max_rows=20
        )
        
        text_table = (
            f"\nLa {table_ref} presenta un resumen estadístico de la cobertura de datos "
            "para cada estación analizada. Se destaca que la completitud varía desde "
            f"{summary_df['Completitud_Pct'].min():.1f}% hasta {summary_df['Completitud_Pct'].max():.1f}%, "
            f"con un valor promedio de {summary_df['Completitud_Pct'].mean():.1f}%. "
            "Estaciones con completitud superior al 90% son consideradas de alta calidad "
            "para análisis hidrológicos rigurosos."
        )
        self.add_paragraph(text_table)
        
    def generate_distribution_section(self, outlier_df: pd.DataFrame):
        """Genera sección de análisis de distribución."""
        self.add_section_header("2.2 Análisis de Distribución y Valores Atípicos", level=2)
        
        text_intro = (
            "El análisis de la distribución estadística de las cotas permite identificar "
            "la variabilidad natural del sistema fluvial, así como detectar posibles "
            "errores de medición o eventos extremos que requieren validación.\n\n"
            
            "La distribución de cotas en el río Magdalena está fuertemente influenciada "
            "por el régimen hidrológico bimodal característico de la región Caribe colombiana, "
            "con picos de nivel asociados a las temporadas de lluvias (abril-mayo y "
            "septiembre-noviembre). Esta variabilidad estacional se refleja en las "
            "características estadísticas presentadas a continuación."
        )
        self.add_paragraph(text_intro)
        
        # Agregar figura de distribución
        dist_path = OUTPUT_PATH / 'distribution_analysis.png'
        fig_ref = self.add_figure(
            dist_path,
            "Análisis de distribución de cotas por estación. "
            "Panel superior: Diagramas de caja (boxplots) mostrando mediana, cuartiles "
            "y valores atípicos. Panel inferior: Gráficos de violín mostrando la densidad "
            "de probabilidad de las cotas.",
            width_inches=6.5
        )
        
        text_analysis = (
            f"\nEl {fig_ref} revela patrones interesantes en la distribución de cotas. "
            "Las estaciones ubicadas aguas arriba (Puerto Wilches, Sitio Nuevo) presentan "
            "mayor variabilidad en sus cotas, reflejando la respuesta más directa a eventos "
            "de precipitación en la cuenca alta. En contraste, las estaciones aguas abajo "
            "(San Pedrito, Calamar) muestran distribuciones más simétricas, resultado del "
            "efecto atenuante de la gran capacidad de almacenamiento de la llanura aluvial "
            "y los complejos sistemas de ciénagas.\n\n"
            
            "Los valores atípicos identificados (puntos fuera de los bigotes en los boxplots) "
            "requieren análisis individual para determinar su naturaleza. Aquellos valores "
            "superiores al percentil 99.5 pueden corresponder a eventos de crecida extrema "
            "documentados históricamente (como el evento del Niño 1997-1998), mientras que "
            "valores anormalmente bajos pueden indicar estiajes severos o errores de medición."
        )
        self.add_paragraph(text_analysis)
        
        # Agregar tabla de outliers
        table_ref = self.add_table(
            outlier_df[['Estacion', 'N_Registros', 'Media', 'Mediana', 'Min', 'Max', 
                       'Total_Outliers', 'Porcentaje_Outliers']],
            "Estadísticas descriptivas y análisis de valores atípicos por estación",
            max_rows=20
        )
        
        text_table = (
            f"\nLa {table_ref} resume las estadísticas descriptivas principales para cada "
            "estación. Se observa que el porcentaje de outliers varía entre estaciones, "
            f"desde {outlier_df['Porcentaje_Outliers'].min():.2f}% hasta "
            f"{outlier_df['Porcentaje_Outliers'].max():.2f}%. "
            "Un porcentaje elevado de outliers puede indicar: (a) alta variabilidad natural "
            "del sistema, (b) problemas de calidad de datos, o (c) una combinación de ambos factores. "
            "Se recomienda realizar análisis de doble masa y comparaciones espaciales para "
            "validar la consistencia de estos valores extremos."
        )
        self.add_paragraph(text_table)
        
    def generate_recommendations_section(self):
        """Genera sección de recomendaciones."""
        self.add_section_header("3. RECOMENDACIONES")
        
        recommendations = (
            "Con base en el análisis exploratorio realizado, se formulan las siguientes "
            "recomendaciones para el procesamiento y análisis posterior de los datos:\n\n"
            
            "1. Imputación de datos faltantes: Para estaciones con completitud superior "
            "al 85%, se recomienda utilizar métodos de imputación basados en correlación "
            "espacial con estaciones vecinas. Para estaciones con mayor porcentaje de "
            "datos faltantes, limitar el análisis a períodos completos o utilizar "
            "modelos hidrológicos conceptuales.\n\n"
            
            "2. Validación de outliers: Los valores identificados como atípicos deben "
            "ser contrastados con registros históricos de eventos extremos y con datos "
            "de estaciones cercanas mediante análisis de doble masa.\n\n"
            
            "3. Homogeneización: Se recomienda aplicar pruebas de homogeneidad (Pettitt, "
            "Standard Normal Homogeneity Test) para detectar posibles saltos en las "
            "series temporales asociados a cambios de equipos o relocation de estaciones.\n\n"
            
            "4. Carga a base de datos: Los datos procesados en formato long están listos "
            "para ser cargados en la tabla water_level_measurements de Supabase, "
            "manteniendo la estructura documentada en el proyecto MagdalenaBot."
        )
        
        self.add_paragraph(recommendations)
        
    def generate_full_report(self):
        """Genera el informe completo."""
        print("Generando informe Word...")
        
        # Cargar datos
        summary_df = pd.read_csv(OUTPUT_PATH / 'station_coverage_summary.csv')
        outlier_df = pd.read_csv(OUTPUT_PATH / 'outlier_analysis.csv')
        
        # Generar contenido
        self.add_title_page()
        self.generate_executive_summary(summary_df)
        self.generate_data_quality_section(summary_df)
        self.generate_distribution_section(outlier_df)
        self.generate_recommendations_section()
        
        # Guardar
        self.doc.save(REPORT_PATH)
        print(f"Informe guardado: {REPORT_PATH}")
        
        return REPORT_PATH


if __name__ == '__main__':
    generator = MagdalenaReportGenerator()
    generator.generate_full_report()
