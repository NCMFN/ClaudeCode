import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import gzip
import os

def main():
    filepath = "redteam.txt.gz"

    records = []
    with gzip.open(filepath, 'rt') as f:
        for line in f:
            parts = line.strip().split(',')
            if len(parts) == 4:
                try:
                    ts = int(parts[0])
                    user = parts[1]
                    src = parts[2]
                    dst = parts[3]
                    records.append({'time': ts, 'user': user, 'source': src, 'dest': dst})
                except:
                    pass

    df = pd.DataFrame(records)

    # 1. redteam_events_per_day.csv
    df['day_index'] = np.floor((df['time'] - 1) / 86400) + 1
    events_per_day = df['day_index'].value_counts().sort_index().reset_index()
    events_per_day.columns = ['day_index', 'event_count']
    events_per_day['cumulative_count'] = events_per_day['event_count'].cumsum()
    events_per_day.to_csv('outputs/tables/redteam_events_per_day.csv', index=False)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(events_per_day['day_index'], events_per_day['event_count'])
    ax.set_title("Red-Team Events per Day Index\n(Source: redteam.txt.gz)")
    ax.set_xlabel("Day Index")
    ax.set_ylabel("Count")
    plt.savefig('outputs/figures/redteam_events_per_day.png', dpi=300)
    plt.close()

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(events_per_day['day_index'], events_per_day['cumulative_count'], marker='o')
    ax.set_title("Cumulative Red-Team Events\n(Source: redteam.txt.gz)")
    ax.set_xlabel("Day Index")
    ax.set_ylabel("Cumulative Count")
    plt.savefig('outputs/figures/redteam_cumulative_events.png', dpi=300)
    plt.close()

    # 2. redteam_events_per_hour_offset.csv
    time_min = df['time'].min()
    df['hour_offset_from_collection_start'] = np.floor((df['time'] - time_min) / 3600)
    events_per_hour = df['hour_offset_from_collection_start'].value_counts().sort_index().reset_index()
    events_per_hour.columns = ['hour_offset_from_collection_start', 'event_count']
    events_per_hour.to_csv('outputs/tables/redteam_events_per_hour_offset.csv', index=False)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(events_per_hour['hour_offset_from_collection_start'], events_per_hour['event_count'])
    ax.set_title("Red-Team Events per Hour Offset\n(Note: Offset from collection start, not wall-clock)\n(Source: redteam.txt.gz)")
    ax.set_xlabel("Hour Offset")
    ax.set_ylabel("Count")
    plt.savefig('outputs/figures/redteam_hour_offset_distribution.png', dpi=300)
    plt.close()

    # 3. redteam_events_per_user.csv
    events_per_user = df['user'].value_counts().reset_index()
    events_per_user.columns = ['user', 'event_count']
    events_per_user.to_csv('outputs/tables/redteam_events_per_user.csv', index=False)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(events_per_user['event_count'], bins=20)
    ax.set_title("Red-Team Events per User (Histogram)\n(Source: redteam.txt.gz)")
    ax.set_xlabel("Event Count per User")
    ax.set_ylabel("Frequency")
    plt.savefig('outputs/figures/redteam_events_per_user.png', dpi=300)
    plt.close()

    # 4. redteam_computer_pair_counts.csv
    df['pair'] = df['source'] + " -> " + df['dest']
    pair_counts = df['pair'].value_counts().reset_index()
    pair_counts.columns = ['computer_pair', 'count']
    top_50 = pair_counts.head(50).copy()
    total_row = pd.DataFrame({'computer_pair': ['TOTAL_ALL_PAIRS'], 'count': [pair_counts['count'].sum()]})
    pair_table = pd.concat([top_50, total_row], ignore_index=True)
    pair_table.to_csv('outputs/tables/redteam_computer_pair_counts.csv', index=False)

    # 5. redteam_interevent_time_summary.csv
    df_sorted = df.sort_values('time').copy()
    df_sorted['interevent_time'] = df_sorted['time'].diff()
    interevent_summary = df_sorted['interevent_time'].describe().reset_index()
    interevent_summary.columns = ['statistic', 'value']
    interevent_summary.to_csv('outputs/tables/redteam_interevent_time_summary.csv', index=False)

    # 6. redteam_split_feasibility.csv
    min_positives = 50
    feasibility = []
    for train_end in [10, 20, 30]:
        for val_end in [train_end+10, train_end+20]:
            test_end = val_end+10

            train_count = df[df['day_index'] <= train_end].shape[0]
            val_count = df[(df['day_index'] > train_end) & (df['day_index'] <= val_end)].shape[0]
            test_count = df[(df['day_index'] > val_end) & (df['day_index'] <= test_end)].shape[0]

            meets_min = (train_count >= min_positives and
                         val_count >= min_positives and
                         test_count >= min_positives)

            feasibility.append({
                'train_end_day': train_end,
                'val_end_day': val_end,
                'test_end_day': test_end,
                'train_positives': train_count,
                'val_positives': val_count,
                'test_positives': test_count,
                'meets_min_positives': meets_min
            })

    feas_df = pd.DataFrame(feasibility)
    feas_df.to_csv('outputs/tables/redteam_split_feasibility.csv', index=False)

    fig, ax = plt.subplots(figsize=(8, 6))
    grid = feas_df.pivot(index='train_end_day', columns='val_end_day', values='test_positives')
    im = ax.imshow(grid.fillna(0).values, cmap='viridis')
    ax.set_xticks(np.arange(len(grid.columns)))
    ax.set_yticks(np.arange(len(grid.index)))
    ax.set_xticklabels(grid.columns)
    ax.set_yticklabels(grid.index)
    ax.set_xlabel('Validation End Day')
    ax.set_ylabel('Train End Day')
    ax.set_title("Test Positives per Boundary\n(Source: redteam.txt.gz)")
    plt.colorbar(im, ax=ax, label='Positives')
    plt.savefig('outputs/figures/redteam_split_feasibility_heatmap.png', dpi=300)
    plt.close()

if __name__ == "__main__":
    main()
