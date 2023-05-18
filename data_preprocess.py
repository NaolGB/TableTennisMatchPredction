import pandas as pd
import json
import request_data

def merge_dataset_total(df, c):
    # c is in ['male', 'female']
    df.drop_duplicates(inplace=True)

    singles_df = df[df['assoc_b'].isna()]
    singles_df.drop(columns=['player_b_id', 'assoc_b', 'name_b', 'player_y_id', 'assoc_y', 'name_y'], inplace=True)
    singles_df['winner_bool'] = singles_df['res_a'] > singles_df['res_x']

    doubles_df = df[df['assoc_b'].notna()]
    doubles_df.drop(columns=['g5a', 'g5x', 'g6a', 'g6x', 'g7a', 'g7x'], inplace=True)
    doubles_df['winner_bool'] = singles_df['res_a'] > singles_df['res_x']

    clean_data_list = []
            
    for i in range(1, 50):
        try:
            with open(f'data/{c}_players_part' + str(i) + '.json', 'r') as file:
                json_file = json.loads(file.read())
                if type(json_file) == str:
                    json_file = json.loads(json_file)
                data_list = json_file['data'][0]
                for i in range(len(data_list)):
                    if data_list[i]['data'] not in clean_data_list:
                        clean_data_list.append(data_list[i]['data']) 
        except FileNotFoundError as file_nf_error:
            pass
        except json.JSONDecodeError as json_decode_error:
            pass

    players_df = pd.DataFrame.from_dict(clean_data_list)

    keep_players_df = players_df
    players_df.drop(columns=request_data.DROP_COLUMNS, inplace=True)
    players_df.rename(columns=request_data.RENAME_COLUMNS, inplace=True)
    keep_players_df = players_df.copy()

    # clean age and wins/losses columns
    players_df['age'] = players_df['age'].str[:2]

    # get player data in matches df
    players_df['total_wins'] = keep_players_df['total_wins']
    players_df['total_wins'] = players_df['total_wins'].str.split(' ').str[0]
    players_df['total_losses'] = players_df['total_losses'].str.split(' ').str[0]
    players_df['year_wins'] = players_df['year_wins'].str.split(' ').str[0]
    players_df['year_losses'] = players_df['year_losses'].str.split(' ').str[0]

    a = players_df['grip'].replace(0, pd.NA)
    a = players_df['grip'].replace([], pd.NA)
    players_df['grip'].replace('-', pd.NA)

    # add total wins
    players_df['player_id'] = pd.to_numeric(players_df['player_id'])
    singles_df['points_a'] = singles_df[['g1a', 'g2a','g3a', 'g4a','g5a', 'g6a', 'g7a']].sum(axis=1)
    singles_df['points_x'] = singles_df[['g1x', 'g2x','g3x', 'g4x','g5x', 'g6x', 'g7x']].sum(axis=1)

    merged = pd.merge(singles_df, players_df, left_on='player_a_id', right_on='player_id')
    merged = pd.merge(merged, players_df, left_on='player_x_id', right_on='player_id', suffixes=('_a', '_x'))

    # Create total points columns
    sums_a = merged.groupby('player_id_a')['points_a',].sum().reset_index()
    sums_x = merged.groupby('player_id_x')['points_x',].sum().reset_index()
    sums_a.rename(columns={'player_id_a' : 'player_id'}, inplace=True)
    sums_x.rename(columns={'player_id_x' : 'player_id'}, inplace=True)

    sums_merged = pd.merge(sums_a, sums_x, on='player_id', how='outer')

    # fill any missing values with zeros
    sums_merged.fillna(0, inplace=True)

    # create a new column that is the sum of data1 and data2 where both are present,
    # otherwise just the value of data1 or data2
    sums_merged['sum'] = sums_merged.apply(lambda row: row['points_a'] + row['points_x'], axis=1)
    sums_merged['player_id_a'] = sums_merged['player_id']
    sums_merged['player_id_x'] = sums_merged['player_id']

    # perform a left join on the second dataframe with the merged dataframe
    merged_sums = pd.merge(merged, sums_merged[['player_id_a', 'sum']], on='player_id_a', how='left')
    merged_sums.rename(columns={'sum':'total_points_a'}, inplace=True)
    merged_sums = pd.merge(merged_sums, sums_merged[['player_id_x', 'sum']], on='player_id_x', how='left')
    merged_sums.rename(columns={'sum':'total_points_x'}, inplace=True)

    merged_sums.to_csv(f'data/merged_{c}_sums_dataset.csv')
    return merged_sums

def get_features_target(df):
    X = df[request_data.ML_FEATURES]
    y = df['winner_bool'].map({True:1, False:0})

    event_map = request_data.EVENT_MAP
    X['event'] = X['event'].map(event_map)

    stage_map = request_data.STAGE_MAP
    X['stage'] = X['stage'].map(stage_map)

    event_type_map = request_data.EVENT_TYPE_MAP
    X['event_type'] = X['event_type'].map(event_type_map)

    ass = X['association_a'].unique().tolist() + X['association_x'].unique().tolist()
    ass = list(set(ass))
    association_map = {}
    for i in range(len(ass)):
        association_map[ass[i]] = i+1
        
    X['association_a'] = X['association_a'].map(association_map)
    X['association_x'] = X['association_x'].map(association_map)

    activity_map = {'T': 2, 'F':1}
    X['activity_a'] = X['activity_a'].map(activity_map)
    X['activity_x'] = X['activity_x'].map(activity_map)

    X.fillna(0, inplace=True)
    X = X.astype({'stage': 'int32', 'age_a':'int32', 'age_x':'int32',
                'total_matches_a':'int32','total_wins_a':'int32',
                'total_losses_a':'int32', 'year_matches_a':'int32',
                'year_wins_a':'int32', 'year_losses_a':'int32',
                'total_matches_x':'int32','total_wins_x':'int32',
                'total_losses_x':'int32', 'year_matches_x':'int32',
                'year_wins_x':'int32', 'year_losses_x':'int32' })
    return X, y