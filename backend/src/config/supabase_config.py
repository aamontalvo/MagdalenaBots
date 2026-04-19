"""Supabase configuration and connection management."""

from typing import Optional, Dict, Any, List
import asyncio
from datetime import datetime

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = None

from src.config.settings import settings
from src.utils.logger import logger
from src.models.water_level import WaterLevelMeasurement


class SupabaseManager:
    """Manager for Supabase database operations."""
    
    def __init__(self):
        """Initialize Supabase manager."""
        self.client: Optional[Client] = None
        self.connected = False
        
    def connect(self) -> bool:
        """
        Establish connection to Supabase.
        
        Returns:
            True if connection successful, False otherwise
        """
        if not SUPABASE_AVAILABLE:
            logger.error("Supabase client not available. Install with: pip install supabase")
            return False
        
        try:
            if not settings.supabase_url or not settings.supabase_key:
                logger.error("Supabase URL or key not configured")
                return False
            
            self.client = create_client(settings.supabase_url, settings.supabase_key)
            self.connected = True
            logger.info("Successfully connected to Supabase")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from Supabase."""
        self.client = None
        self.connected = False
        logger.info("Disconnected from Supabase")
    
    def is_connected(self) -> bool:
        """Check if connected to Supabase."""
        return self.connected and self.client is not None
    
    def create_water_level_table(self) -> bool:
        """
        Create the water level measurements table if it doesn't exist.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            logger.error("Not connected to Supabase")
            return False
        
        try:
            # SQL to create table
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS water_level_measurements (
                id SERIAL PRIMARY KEY,
                station_code VARCHAR(20) NOT NULL,
                station_name VARCHAR(255) NOT NULL,
                variable VARCHAR(50) NOT NULL,
                parameter VARCHAR(100) NOT NULL,
                measurement_date DATE NOT NULL,
                unit VARCHAR(10) NOT NULL,
                value DECIMAL(10,2) NOT NULL,
                approval_level VARCHAR(50) NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                UNIQUE(station_code, measurement_date)
            );
            
            -- Create indexes for better performance
            CREATE INDEX IF NOT EXISTS idx_water_level_station_code ON water_level_measurements(station_code);
            CREATE INDEX IF NOT EXISTS idx_water_level_date ON water_level_measurements(measurement_date);
            CREATE INDEX IF NOT EXISTS idx_water_level_station_date ON water_level_measurements(station_code, measurement_date);
            """
            
            # Execute the SQL
            self.client.rpc('exec_sql', {'sql': create_table_sql}).execute()
            
            logger.info("Water level measurements table created/verified")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create water level table: {e}")
            return False
    
    def insert_measurement(self, measurement: WaterLevelMeasurement) -> bool:
        """
        Insert a single water level measurement.
        
        Args:
            measurement: WaterLevelMeasurement object
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            logger.error("Not connected to Supabase")
            return False
        
        try:
            data = {
                'station_code': measurement.station_code,
                'station_name': measurement.station_name,
                'variable': measurement.variable,
                'parameter': measurement.parameter,
                'measurement_date': measurement.date.strftime('%Y-%m-%d'),
                'unit': measurement.unit,
                'value': float(measurement.value),
                'approval_level': measurement.approval_level
            }
            
            result = self.client.table('water_level_measurements').insert(data).execute()
            
            if result.data:
                logger.debug(f"Successfully inserted measurement for {measurement.station_code} on {measurement.date}")
                return True
            else:
                logger.warning(f"No data returned when inserting measurement")
                return False
                
        except Exception as e:
            logger.error(f"Failed to insert measurement: {e}")
            return False
    
    def insert_measurements_batch(self, measurements: List[WaterLevelMeasurement], batch_size: int = 100) -> Dict[str, int]:
        """
        Insert multiple water level measurements in batches.
        
        Args:
            measurements: List of WaterLevelMeasurement objects
            batch_size: Number of records to insert per batch
            
        Returns:
            Dictionary with insertion statistics
        """
        if not self.is_connected():
            logger.error("Not connected to Supabase")
            return {'success': 0, 'failed': len(measurements)}
        
        stats = {'success': 0, 'failed': 0}
        
        try:
            # Process in batches
            for i in range(0, len(measurements), batch_size):
                batch = measurements[i:i + batch_size]
                batch_data = []
                
                for measurement in batch:
                    batch_data.append({
                        'station_code': measurement.station_code,
                        'station_name': measurement.station_name,
                        'variable': measurement.variable,
                        'parameter': measurement.parameter,
                        'measurement_date': measurement.date.strftime('%Y-%m-%d'),
                        'unit': measurement.unit,
                        'value': float(measurement.value),
                        'approval_level': measurement.approval_level
                    })
                
                # Insert batch
                try:
                    result = self.client.table('water_level_measurements').insert(batch_data).execute()
                    if result.data:
                        stats['success'] += len(batch)
                        logger.info(f"Successfully inserted batch of {len(batch)} measurements")
                    else:
                        stats['failed'] += len(batch)
                        logger.warning(f"Failed to insert batch of {len(batch)} measurements")
                        
                except Exception as e:
                    logger.error(f"Batch insertion failed: {e}")
                    stats['failed'] += len(batch)
            
            logger.info(f"Batch insertion completed: {stats['success']} successful, {stats['failed']} failed")
            return stats
            
        except Exception as e:
            logger.error(f"Batch insertion process failed: {e}")
            return stats
    
    def get_measurements_by_station(self, station_code: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve measurements for a specific station.
        
        Args:
            station_code: Station code to filter by
            start_date: Optional start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD)
            
        Returns:
            List of measurement dictionaries
        """
        if not self.is_connected():
            logger.error("Not connected to Supabase")
            return []
        
        try:
            query = self.client.table('water_level_measurements').select('*').eq('station_code', station_code)
            
            if start_date:
                query = query.gte('measurement_date', start_date)
            if end_date:
                query = query.lte('measurement_date', end_date)
            
            result = query.order('measurement_date').execute()
            
            if result.data:
                logger.info(f"Retrieved {len(result.data)} measurements for station {station_code}")
                return result.data
            else:
                logger.info(f"No measurements found for station {station_code}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to retrieve measurements: {e}")
            return []
    
    def get_station_statistics(self, station_code: str) -> Dict[str, Any]:
        """
        Get statistics for a specific station.
        
        Args:
            station_code: Station code to analyze
            
        Returns:
            Dictionary with station statistics
        """
        if not self.is_connected():
            logger.error("Not connected to Supabase")
            return {}
        
        try:
            # Get basic statistics
            result = self.client.table('water_level_measurements').select('*').eq('station_code', station_code).execute()
            
            if not result.data:
                return {}
            
            df = pd.DataFrame(result.data)
            
            stats = {
                'station_code': station_code,
                'total_measurements': len(df),
                'date_range': {
                    'start': df['measurement_date'].min(),
                    'end': df['measurement_date'].max()
                },
                'value_statistics': {
                    'min': float(df['value'].min()),
                    'max': float(df['value'].max()),
                    'mean': float(df['value'].mean()),
                    'median': float(df['value'].median()),
                    'std': float(df['value'].std())
                },
                'approval_levels': df['approval_level'].value_counts().to_dict()
            }
            
            logger.info(f"Generated statistics for station {station_code}")
            return stats
                 
        except Exception as e:
            logger.error(f"Failed to generate station statistics: {e}")
            return {}
    
    def delete_measurements_by_date_range(self, station_code: str, start_date: str, end_date: str) -> int:
        """
        Delete measurements within a date range.
        
        Args:
            station_code: Station code
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Number of deleted records
        """
        if not self.is_connected():
            logger.error("Not connected to Supabase")
            return 0
        
        try:
            result = self.client.table('water_level_measurements').delete().eq('station_code', station_code).gte('measurement_date', start_date).lte('measurement_date', end_date).execute()
            
            deleted_count = len(result.data) if result.data else 0
            logger.info(f"Deleted {deleted_count} measurements for station {station_code} between {start_date} and {end_date}")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to delete measurements: {e}")
            return 0


# Global Supabase manager instance
supabase_manager = SupabaseManager()