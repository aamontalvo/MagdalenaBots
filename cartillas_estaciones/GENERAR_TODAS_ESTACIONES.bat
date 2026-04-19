@echo off
chcp 65001 >nul
echo ========================================
echo  GENERAR CARTILLAS - ESTACIONES NO PROBLEMÁTICAS
echo ========================================
echo.

cd /d "%~dp0"

echo Estaciones a generar: 13
echo Excluyendo: COYONGAL, RIO_NUEVO, LAS_PALOMAS, ARMENIA, GAMARRA_AUT
echo.

echo [1/2] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no está instalado
    pause
    exit /b 1
)

echo [2/2] Generando cartillas...
echo.
echo NOTA: Este proceso tomará ~10-15 minutos
echo Generando 13 estaciones x 5 figuras = 65 imágenes
echo.

python generar_todas_estaciones_no_problematicas.py

echo.
echo ========================================
echo  PROCESO COMPLETADO
echo ========================================
echo.
echo Revisa la carpeta resultados/ con las subcarpetas:
echo   - CALAMAR, BARBOSA, TENERIFE, PLATO, MAGANGUE, SAN_PEDRITO
echo   - LAS_AGUADAS, EL_BANCO, PENONCITO
echo   - LA_GLORIA, EL_CONTENTO, SITIO_NUEVO, PUERTO_WILCHES
echo.
pause
