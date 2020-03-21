import fingertips_py as ftp
import pandas as pd

out = "../../data/lookup_tables/{}"

# Get all of the indicators and areas than can be searched for and put them in CSV files, so it is easier to look
# up things we want to search for later. Since there is no documentation available online.

all_indicators = ftp.metadata.get_metadata_for_all_indicators_from_csv().sort_values(by ='Indicator ID')
all_areas = ftp.metadata.get_all_areas()
all_profiles = ftp.metadata.get_all_profiles()

profiles_df = pd.DataFrame(all_profiles)
profiles_meta = profiles_df.pop('GroupMetadata')

areas_df = pd.DataFrame.from_dict(all_areas, orient='index')
areas_df['Area type ID'] = areas_df.index

# Re-order the columns so area type id is first
cols = areas_df.columns
cols = cols[-1:].append(cols[:-1])

areas_df = areas_df[cols]

all_indicators.to_csv(out.format("phe_fingertips_indicators.csv"))
areas_df.to_csv(out.format("phe_fingertips_areas.csv"))
profiles_df.to_csv(out.format("phe_fingertips_profiles.csv"))
