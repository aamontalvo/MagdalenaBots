"""
Supabase Connector for MagdalenaBot
Optimized for time series retrieval
"""

import os
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import pandas as pd

# Try to import supabase
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("Warning: supabase package not installed. Install with: pip install supabase")


class SupabaseConnector:
    """
    Connector for Supabase water level database
    """
    
    def __init__(self, url: Optional[str] = None, key: Optional[str] = None):
        """
        Initialize Supabase connection
        
        Args:
            url: Supabase project URL
            key: Supabase API key (anon or service role)
        """
        # Default credentials for MagdalenaBot project
        default_url = "https://nwmkqpaibbwebovhacth.supabase.co"
        default_key = "sb_secret_8EcsBepYZ0vVYPk-ryoFtw_aZxEO7P_"  # Service role key
        
        self.url = url or os.getenv('SUPABASE_URL') or default_url
        self.key = key or os.getenv('SUPABASE_KEY') or default_key
        self.client: Optional[Client] = None
        self.connected = False
        
        if SUPABASE_AVAILABLE and self.url and self.key:
            self._connect()
    
    def _connect(self):
        """Establish connection"""
        try:
            self.client = create_client(self.url, self.key)
            self.connected = True
            print(f"✅ Connected to Supabase: {self.url}")
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            self.connected = False
    
    def get_station_data(
        self, 
        station_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        years: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Retrieve water level data for a station
        
        Args:
            station_code: Station identifier
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            years: If set, get last N years of data
            
        Returns:
            DataFrame with columns [date, water_level_cm, station_code]
        """
        if not self.connected:
            raise ConnectionError("Not connected to Supabase")
        
        # Build query
        query = (
            self.client
            .table('water_level_measurements')
            .select('measurement_date, value, station_code')
            .eq('station_code', station_code)
        )
        
        # Apply date filters
        if years:
            start = (datetime.now() - timedelta(days=365*years)).strftime('%Y-%m-%d')
            query = query.gte('measurement_date', start)
        elif start_date:
            query = query.gte('measurement_date', start_date)
        
        if end_date:
            query = query.lte('measurement_date', end_date)
        
        # Execute
        try:
            response = query.order('measurement_date').execute()
            
            if not response.data:
                return pd.DataFrame(columns=['date', 'water_level_cm', 'station_code'])
            
            # Convert to DataFrame
            df = pd.DataFrame(response.data)
            df = df.rename(columns={
                'measurement_date': 'date',
                'value': 'water_level_cm'
            })
            df['date'] = pd.to_datetime(df['date'])
            
            print(f"📊 Retrieved {len(df)} records for station {station_code}")
            return df
            
        except Exception as e:
            print(f"❌ Query failed: {e}")
            raise
    
    def get_station_summary(self, station_code: str) -> Dict:
        """Get summary statistics for a station"""
        if not self.connected:
            raise ConnectionError("Not connected to Supabase")
        
        try:
            # Get all data for station
            response = (
                self.client
                .table('water_level_measurements')
                .select('measurement_date, value')
                .eq('station_code', station_code)
                .execute()
            )
            
            if not response.data:
                return {}
            
            df = pd.DataFrame(response.data)
            
            return {
                'station_code': station_code,
                'total_records': len(df),
                'date_start': df['measurement_date'].min(),
                'date_end': df['measurement_date'].max(),
                'level_min_cm': df['value'].min(),
                'level_max_cm': df['value'].max(),
                'level_mean_cm': round(df['value'].mean(), 2),
            }
            
        except Exception as e:
            print(f"❌ Summary query failed: {e}")
            return {}
    
    def test_connection(self) -> bool:
        """Test if connection is working"""
        if not self.connected:
            return False
        
        try:
            # Try a simple query
            response = (
                self.client
                .table('water_level_measurements')
                .select('station_code')
                .limit(1)
                .execute()
            )
            return True
        except:
            return False


def get_connector() -> SupabaseConnector:
    """Factory function to get configured connector"""
    return SupabaseConnector()


if __name__ == '__main__':
    # Test the connector
    connector = get_connector()
    
    if connector.test_connection():
        print("\nConnection test passed!")
        
        # Try to get data for Calamar
        try:
            data = connector.get_station_data('29037020', years=2)
            print(f"\nSample data:")
            print(data.head())
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("\nConnection test failed. Check your credentials.")
