import gdelt
import pandas as pd

gd2 = gdelt.gdelt(version=2)

# search for events according to date, and return a dataframe with coverage information
events_df = gd2.Search(['2026 May 11'], table='events', coverage=True)
print(events_df.head())

from datetime import datetime, timedelta

# define the CAMEO root codes for geopolitical events
geopolitical_root_codes = ['10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20']

# define the date range
print("downloading GDELT data...")
end_date = datetime.now()
start_date = end_date - timedelta(days=1)
date_range = pd.date_range(start_date, end_date).strftime('%Y %b %d').tolist()

# download events for the specified date range
all_events = gd2.Search(date_range, table='events', coverage=True)

if not all_events.empty:
    print(f"downloaded {len(all_events)} records from GDELT for the date range {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    # geopolitical events are typically those with EventCode starting with 1x, so we can filter based on that
    all_events['EventRootCode'] = all_events['EventCode'].astype(str).str[:2]
    
    geo_events = all_events[all_events['EventRootCode'].isin(geopolitical_root_codes)]
    print(f"geopolitical events: {len(geo_events)}")
    
    key_columns = ['SQLDATE', 'Actor1Name', 'Actor2Name', 'EventCode', 
                   'EventRootCode', 'GoldsteinScale', 'AvgTone', 'ActionGeo_FullName']
    
    display_columns = [col for col in key_columns if col in geo_events.columns]
    
    print("\n===== Geopolitical Events Example =====")
    print(geo_events[display_columns].head(10).to_string())
    
    # summarize event type distribution
    event_counts = geo_events['EventRootCode'].value_counts()
    print("\n===== Event Type Distribution =====")
    for code, count in event_counts.items():
        # Simple CAMEO explanation
        cameo_names = {
            '10': 'Demand', '11': 'Disapprove', '12': 'Reject',
            '13': 'Threaten', '14': 'Protest', '15': 'Force Posture',
            '16': 'Reduce Relations', '17': 'Coerce', 
            '18': 'Assault', '19': 'Fight', '20': 'Unconventional Mass Violence'
        }
        name = cameo_names.get(code, 'Unknown')
        print(f"{code} - {name}: {count} records")
    
    # save to CSV
    output_file = f"geopolitical_events_{datetime.now().strftime('%Y%m%d')}.csv"
    geo_events.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\nData saved to: {output_file}")
    
else:
    print("No data retrieved. Please check your network connection or the date range.")

    """find events(GLOBALEVENTID) by keyword"""

print("downloading...")
events_df = gd2.Search(['2026 May 10'], table='events', coverage=True)
print(f"downloaded {len(events_df)} records")

def search_events_by_keyword(df, keyword, column='Actor1Name'):
    """search in the specified column for the keyword and return the event IDs and basic information"""
    mask = df[column].astype(str).str.contains(keyword, case=False, na=False)
    results = df[mask][['GLOBALEVENTID', 'SQLDATE', 'Actor1Name', 'Actor2Name', 
                         'EventCode', 'ActionGeo_FullName', 'AvgTone']]
    return results.drop_duplicates(subset='GLOBALEVENTID')

# example: search for events involving "USA"
print("\n===== example: search for events involving \"USA\" =====")
usa_events = search_events_by_keyword(events_df, 'USA', 'Actor1Name')
print(f"found {len(usa_events)} events")
print(usa_events.head(10).to_string())



"""search for all articles related to a specific event ID"""

def get_event_news(df, event_id):
    event_data = df[df['GLOBALEVENTID'] == event_id]
    if len(event_data) == 0:
        return None
    return event_data[['GLOBALEVENTID', 'SQLDATE', 'Actor1Name', 'Actor2Name', 
                        'EventCode', 'NumArticles', 'AvgTone', 'SOURCEURL']]

# example: use the first found ID for demonstration
if len(usa_events) > 0:
    sample_id = usa_events.iloc[0]['GLOBALEVENTID']
    print(f"\n===== all articles for event ID: {sample_id} =====")
    news = get_event_news(events_df, sample_id)
    if news is not None:
        print(f"found {len(news)} records (from different sources)")
        print(f"total articles: {news['NumArticles'].sum()}")
        for i, row in news.head(5).iterrows():
            print(f"  source: {row['SOURCEURL'][:80]}...")
            print(f"  tone: {row['AvgTone']}")