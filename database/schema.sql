-- Esquema de Base de Datos - MagdalenaBot v3.0
-- Proyecto: Analisis Hidrologico Rio Magdalena
-- Fecha: Marzo 2026

-- =====================================================
-- TABLA PRINCIPAL: Mediciones de Nivel
-- =====================================================
CREATE TABLE IF NOT EXISTS water_level_measurements (
    id SERIAL PRIMARY KEY,
    station_id VARCHAR(50) NOT NULL,
    station_name VARCHAR(100) NOT NULL,
    measurement_date DATE NOT NULL,
    water_level_m DECIMAL(8,3) NOT NULL,
    water_level_cm INTEGER GENERATED ALWAYS AS (water_level_m * 100) STORED,
    
    -- Flags de calidad
    is_imputed BOOLEAN DEFAULT FALSE,
    imputation_level INTEGER CHECK (imputation_level IN (0, 1, 2, 3)),
    -- 0 = Observado, 1 = Interpolacion, 2 = H-H, 3 = Multi-donante
    
    quality_flag VARCHAR(20) DEFAULT 'VALID',
    -- VALID, SUSPECT, INVALID, MISSING
    
    -- Metadata de imputacion
    donor_station VARCHAR(50),
    r_squared DECIMAL(4,3),
    model_type VARCHAR(20),
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_station_date UNIQUE (station_id, measurement_date)
);

-- Indices para consultas comunes
CREATE INDEX idx_measurements_station_date ON water_level_measurements(station_id, measurement_date);
CREATE INDEX idx_measurements_date ON water_level_measurements(measurement_date);
CREATE INDEX idx_measurements_imputed ON water_level_measurements(is_imputed) WHERE is_imputed = TRUE;
CREATE INDEX idx_measurements_quality ON water_level_measurements(quality_flag);

-- =====================================================
-- TABLA: Catalogo de Estaciones
-- =====================================================
CREATE TABLE IF NOT EXISTS stations (
    station_id VARCHAR(50) PRIMARY KEY,
    station_name VARCHAR(100) NOT NULL,
    station_code_ideam VARCHAR(20),
    
    -- Ubicacion geografica
    zone VARCHAR(20) CHECK (zone IN ('Baja', 'Media', 'Alta')),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    elevation_m DECIMAL(8, 2),
    
    -- Caracteristicas
    is_automatic BOOLEAN DEFAULT FALSE,
    installation_year INTEGER,
    
    -- Estado de calidad (del diagnostico)
    quality_status VARCHAR(20) DEFAULT 'PENDING',
    -- EXCELLENT, GOOD, USABLE_WITH_CAUTION, EXCLUDE
    
    -- Metricas calculadas
    coverage_pct DECIMAL(5, 2),
    total_records INTEGER,
    start_date DATE,
    end_date DATE,
    
    -- Campos de exclusion
    exclude_from_analysis BOOLEAN DEFAULT FALSE,
    exclusion_reason TEXT,
    excluded_periods JSONB,
    
    -- Relaciones espaciales
    upstream_station VARCHAR(50) REFERENCES stations(station_id),
    downstream_station VARCHAR(50) REFERENCES stations(station_id),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- TABLA: Modelos de Imputacion (H-H)
-- =====================================================
CREATE TABLE IF NOT EXISTS imputation_models (
    id SERIAL PRIMARY KEY,
    target_station VARCHAR(50) NOT NULL REFERENCES stations(station_id),
    donor_station VARCHAR(50) NOT NULL REFERENCES stations(station_id),
    model_type VARCHAR(20) NOT NULL,
    r_squared DECIMAL(4,3) NOT NULL,
    rmse DECIMAL(8,3),
    coef_a DECIMAL(12, 8),
    coef_b DECIMAL(12, 8),
    coef_c DECIMAL(12, 8),
    valid_range_min DECIMAL(8,3),
    valid_range_max DECIMAL(8,3),
    is_active BOOLEAN DEFAULT TRUE,
    is_accepted BOOLEAN DEFAULT FALSE,
    calibration_start DATE,
    calibration_end DATE,
    n_calibration_points INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_model_pair UNIQUE (target_station, donor_station, model_type)
);

-- =====================================================
-- TABLA: Validaciones Automaticas
-- =====================================================
CREATE TABLE IF NOT EXISTS validation_results (
    id SERIAL PRIMARY KEY,
    station_id VARCHAR(50) NOT NULL REFERENCES stations(station_id),
    validation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    check_outliers_status VARCHAR(20),
    check_duration_jumps_status VARCHAR(20),
    check_distribution_status VARCHAR(20),
    check_spatial_coherence_status VARCHAR(20),
    n_outliers INTEGER DEFAULT 0,
    n_duration_jumps INTEGER DEFAULT 0,
    n_spatial_anomalies INTEGER DEFAULT 0,
    quality_score INTEGER CHECK (quality_score >= 0 AND quality_score <= 100),
    details JSONB,
    alerts TEXT[]
);

-- =====================================================
-- VISTAS UTILES
-- =====================================================
CREATE OR REPLACE VIEW station_summary AS
SELECT 
    s.station_id,
    s.station_name,
    s.zone,
    s.quality_status,
    COUNT(m.id) as total_records,
    SUM(CASE WHEN m.is_imputed THEN 1 ELSE 0 END) as imputed_records,
    AVG(m.water_level_m) as mean_level,
    MIN(m.water_level_m) as min_level,
    MAX(m.water_level_m) as max_level,
    STDDEV(m.water_level_m) as std_level
FROM stations s
LEFT JOIN water_level_measurements m ON s.station_id = m.station_id
GROUP BY s.station_id, s.station_name, s.zone, s.quality_status;

-- =====================================================
-- FUNCIONES AUXILIARES
-- =====================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_stations_updated_at BEFORE UPDATE ON stations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
