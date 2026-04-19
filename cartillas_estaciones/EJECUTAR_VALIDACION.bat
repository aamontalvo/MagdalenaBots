@echo off
chcp 65001 >nul
echo ========================================
echo  SISTEMA DE VALIDACIÓN - RIO MAGDALENA
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no está instalado o no está en PATH
    echo Por favor instala Python 3.8 o superior
    pause
    exit /b 1
)

echo [2/3] Ejecutando validación...
python validar_estaciones.py

echo.
echo [3/3] Generando visualizaciones...
python generar_visualizacion_validacion.py

echo.
echo ========================================
echo  PROCESO COMPLETADO
echo ========================================
echo.
echo Archivos generados en resultados/:
echo   - validacion_imputacion_problemas.md
echo   - periodos_problematicos.csv
echo   - Validacion_Resumen_Todas_Estaciones.png
echo   - Validacion_Detallada_*.png (5 archivos)
echo.
pause
