from supabase_manager import SupabaseManager

def verify_data_upload():
    db_manager = SupabaseManager()
    
    try:
        # Check cloud_emissions table
        emissions = db_manager.supabase.table('cloud_emissions').select('*').execute()
        print(f"Cloud Emissions Records: {len(emissions.data)}")
        
        # Check provider_metrics table
        providers = db_manager.supabase.table('provider_metrics').select('*').execute()
        print(f"Provider Metrics Records: {len(providers.data)}")
        
        # Check location_metrics table
        locations = db_manager.supabase.table('location_metrics').select('*').execute()
        print(f"Location Metrics Records: {len(locations.data)}")
        
    except Exception as e:
        print(f"Error verifying data: {e}")

if __name__ == "__main__":
    verify_data_upload() 