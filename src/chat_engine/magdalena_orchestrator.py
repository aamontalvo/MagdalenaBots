"""
MagdalenaBot Orchestrator
Main entry point for processing engineer requests
"""

import os
import sys
from typing import Dict, Optional
import json

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chat_engine.engineer_intent_parser import EngineerIntentParser, AnalysisType
from data_connectors.supabase_connector import SupabaseConnector
from analysis.hydrological_analyzer import HydrologicalAnalyzer


class MagdalenaOrchestrator:
    """
    Main orchestrator that processes engineer requests end-to-end:
    1. Parse natural language request
    2. Fetch data from Supabase
    3. Generate analyses
    4. Return CSVs ready for email
    """
    
    def __init__(self):
        self.parser = EngineerIntentParser()
        self.db = SupabaseConnector()
        
    def process_request(self, message: str, default_email: Optional[str] = None) -> Dict:
        """
        Process an engineer's request
        
        Args:
            message: Natural language request
            default_email: Fallback email if not in message
            
        Returns:
            Dictionary with:
            - success: bool
            - request: parsed request info
            - csvs: dict of CSV buffers
            - error: error message if failed
        """
        try:
            # Step 1: Parse the request
            print(f"📝 Parsing request: {message}")
            request = self.parser.parse(message, default_email)
            
            print(f"✅ Parsed: {request.station_name}, {request.analysis_type.value}")
            
            # Step 2: Fetch data from Supabase
            print(f"📡 Fetching data from Supabase...")
            
            # Apply filters
            years = request.filters.get('last_years', 10)  # Default 10 years
            
            df = self.db.get_station_data(
                station_code=request.station_code,
                years=years
            )
            
            if len(df) == 0:
                return {
                    'success': False,
                    'error': f"No data found for station {request.station_name}",
                    'request': request
                }
            
            print(f"📊 Retrieved {len(df)} records")
            
            # Step 3: Generate analyses
            print(f"🔬 Generating hydrological analyses...")
            analyzer = HydrologicalAnalyzer(df)
            
            # Get all analyses or specific one
            if request.analysis_type == AnalysisType.ALL:
                csvs = analyzer.analyze_all(request.station_code, request.email)
            else:
                # Generate specific analysis + metadata
                all_csvs = analyzer.analyze_all(request.station_code, request.email)
                
                analysis_key = request.analysis_type.value
                csvs = {
                    analysis_key: all_csvs[analysis_key],
                    'metadata': all_csvs['metadata']
                }
            
            print(f"✅ Generated {len(csvs)} CSV files")
            
            return {
                'success': True,
                'request': request,
                'csvs': csvs
            }
            
        except ValueError as e:
            # Parsing error
            return {
                'success': False,
                'error': str(e),
                'help_text': self.parser.get_help_text()
            }
            
        except Exception as e:
            # Other errors
            return {
                'success': False,
                'error': f"Processing error: {str(e)}"
            }
    
    def health_check(self) -> Dict:
        """Check system health"""
        return {
            'parser': True,
            'database': self.db.test_connection(),
            'analyzer': True
        }


def main():
    """CLI interface for testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='MagdalenaBot - Hydrological Analysis')
    parser.add_argument('message', help='Natural language request')
    parser.add_argument('--email', '-e', help='Default email address')
    parser.add_argument('--output', '-o', help='Output directory for CSVs')
    
    args = parser.parse_args()
    
    # Create orchestrator
    bot = MagdalenaOrchestrator()
    
    # Health check
    health = bot.health_check()
    print("🔍 System Health:")
    for component, status in health.items():
        icon = "✅" if status else "❌"
        print(f"   {icon} {component}")
    
    if not all(health.values()):
        print("\n⚠️  Some components are not healthy. Check configuration.")
        return
    
    # Process request
    print(f"\n{'='*60}")
    result = bot.process_request(args.message, args.email)
    
    if result['success']:
        print(f"\n✅ Request processed successfully!")
        print(f"   Station: {result['request'].station_name}")
        print(f"   Analysis: {result['request'].analysis_type.value}")
        print(f"   Email: {result['request'].email}")
        
        # Save CSVs if output directory specified
        if args.output:
            os.makedirs(args.output, exist_ok=True)
            for name, csv_buffer in result['csvs'].items():
                filename = f"{result['request'].station_code}_{name}.csv"
                filepath = os.path.join(args.output, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(csv_buffer.read())
                
                print(f"   💾 Saved: {filepath}")
    else:
        print(f"\n❌ Error: {result.get('error', 'Unknown error')}")
        if 'help_text' in result:
            print(f"\n{result['help_text']}")


if __name__ == '__main__':
    main()
