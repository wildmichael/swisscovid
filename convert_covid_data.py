import pandas as pd
import numpy as np

def convert_data(data_url):
    data = pd.read_csv(
        data_url,
        parse_dates=['date']
    ).rename(
        columns={
            'date': 'Datum',
            'abbreviation_canton_and_fl': 'Kanton',
            'ncumul_conf': 'Bestätigt Kumulativ',
            'ncumul_deceased': 'Verstorben Kumulativ',
            'current_hosp': 'Hospitalisiert Aktuell',
            'current_icu': 'Intensivstation Aktuell',
            'current_isolated': 'Isoliert Aktuell',
            'current_quarantined': 'Quarantäne Aktuell',
            'current_vent': 'Beatmet Aktuell',
            'ncumul_released': 'Entlassen Kumulativ',
            'ncumul_tested': 'Getestet Kumulativ',
        },
    ).set_index(
        ['Datum', 'Kanton']
    ).drop(
        'FL',
        level=1
    ).drop(
        columns=['time', 'source', 'current_quarantined_riskareatravel', 'current_quarantined_total']
    ).unstack(
        level=1
    ).ffill(
    ).fillna(
        np.nan
    ).iloc[:-1]
    data = pd.concat(
        [
            data,
            data.loc[:, ('Bestätigt Kumulativ', slice(None))].diff().rolling(7).mean().rename(columns={'Bestätigt Kumulativ': 'Bestätigt Neu'}),
            data.loc[:, ('Verstorben Kumulativ', slice(None))].diff().rolling(7).mean().rename(columns={'Verstorben Kumulativ': 'Verstorben Neu'}),
            data.loc[:, ('new_hosp', slice(None))].rolling(7).mean().rename(columns={'new_hosp': 'Hospitalisiert Neu'}),
        ],
        axis=1
    ).drop(
        columns='new_hosp',
        level=0,
    )

    df = data.melt(
        ignore_index=False,
        value_name='Anzahl',
    ).rename(
        columns={None: 'Variable'},
    ).reset_index(
    )
    return df

if __name__ == '__main__':
    df = convert_data('https://raw.githubusercontent.com/openZH/covid_19/master/COVID19_Fallzahlen_CH_total_v2.csv')
    df.to_json('COVID19_Fallzahlen_CH_total.json', orient='records')