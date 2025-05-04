import pandas as pd
from tabulate import tabulate
import seaborn as sns
import matplotlib.pyplot as plt

DEBUG = False

def cleandf(df):
    # Check for NaN/null values
    print("Null Values Before Cleaning:")
    print(df.isnull().sum())

    # Remove rows with NaN values
    df_cleaned = df.dropna()
    # Verify cleaning
    print("\nNull Values After Cleaning:")
    print(df_cleaned.isnull().sum())
    # =================================================================

    # Check for "ERROR" strings (non-numeric)
    print("\nRows with 'ERROR':")
    print(df[df.eq("ERROR").any(axis=1)])
    # Remove rows with "ERROR" (if any column contains it)
    df_cleaned = df_cleaned[~df_cleaned.eq("ERROR").any(axis=1)]

    print("\nDataFrame Shape Before ERROR removed:", df.shape)
    print("DataFrame Shape After ERROR removed:", df_cleaned.shape)
    # =================================================================

    # TYPOS
    # TODO: populate automatically, map most common val
    # to everything else

    # Create a mapping dictionary for corrections
    activity_corrections = {
        'Actve': 'Active', # Fixes typo
        'Highly Active': 'Highly_Active',  # Fixes space to underscore
        'Seddentary': 'Sedentary'  # Fixes double 'd'
    }

    # Apply the corrections to the Activity Level column
    df_cleaned['Activity Level'] = df_cleaned['Activity Level'].replace(activity_corrections)

    # Verify the changes
    print("Unique activity levels after cleaning:")
    print(df_cleaned['Activity Level'].unique())

    return df_cleaned

def check_types(df):
    # user id is an integer number not a fraction, so we convert
    df['User ID'] = df['User ID'].astype(int)
    df['Heart Rate (BPM)'] = pd.to_numeric(df['Heart Rate (BPM)'], errors='coerce')
    df['Step Count'] = pd.to_numeric(df['Step Count'], errors='coerce')
    df['Blood Oxygen Level (%)'] = pd.to_numeric(df['Blood Oxygen Level (%)'], errors='coerce')
    df['Sleep Duration (hours)'] = pd.to_numeric(df['Sleep Duration (hours)'], errors='coerce')
    df['Stress Level'] = pd.to_numeric(df['Stress Level'], errors='coerce')
    return df

def check_values(df):
    # HEART RATE
    too_low = df['Heart Rate (BPM)'] < 30
    too_high = df['Heart Rate (BPM)'] > 220
    invalid_heart_rate = too_low | too_high
    df = df[~invalid_heart_rate].copy()
    print(f"HEART RATE CHECK: rows removed: {invalid_heart_rate.sum()}")
    print("HEART RATE CHECK: shape:", df.shape)

    # BLOOD OXYGEN
    too_high = df['Blood Oxygen Level (%)'] > 100
    invalid_blood_oxygen = too_high
    df = df[~invalid_blood_oxygen].copy()
    print(f"BLOOD OXY CHECK: rows removed: {invalid_blood_oxygen.sum()}")
    print("BLOOD OXY CHECK: shape:", df.shape)

    # Negative step counts or sleep duration
    neg_steps = df['Step Count'] < 0
    neg_sleep = df['Sleep Duration (hours)'] < 0
    neg_vals = neg_steps | neg_sleep
    df = df[~neg_vals].copy()
    print(f"NEG VALS CHECK: rows removed: {neg_vals.sum()}")
    print("NEG VALS CHECK: shape:", df.shape)

    return df

def analyze_simple(df):
    # 2. Calculate averages
    print("\nAverage Metrics:")
    print(f"Heart Rate: {df['Heart Rate (BPM)'].mean():.1f} BPM")
    print(f"Step Count: {df['Step Count'].mean():,.0f} steps")
    print(f"Blood Oxygen: {df['Blood Oxygen Level (%)'].mean():.1f}%")

    # 3. Most common sleep duration (mode)
    sleep_mode = df['Sleep Duration (hours)'].round(2).mode()[0]
    print(f"Most common sleep duration (rounded): {sleep_mode:.2f} hours")

    # 4. Typical stress level (median)
    stress_median = df['Stress Level'].median()
    print(f"Typical stress level: {stress_median} (median)")

def analyze_advanced(df):
    # 1. Does sleep duration change with stress level?
    sleep_stress = df.groupby('Stress Level')['Sleep Duration (hours)'].mean()
    print("\nAverage Sleep Duration by Stress Level:")
    print(sleep_stress)

    # 2. Do more active people have more steps?
    activity_steps = df.groupby('Activity Level')['Step Count'].mean().sort_values(ascending=False)
    print("\nAverage Steps by Activity Level:")
    print(activity_steps)

    # 3. Heart rate vs stress relationship
    hr_stress = df.groupby('Stress Level')['Heart Rate (BPM)'].mean()
    print("\nAverage Heart Rate by Stress Level:")
    print(hr_stress)

def visualize(df):
    user_id = "User ID"
    heart_rate = "Heart Rate (BPM)"
    blood_oxygen = "Blood Oxygen Level (%)"
    step_count = "Step Count"
    sleep_duration = "Sleep Duration (hours)"
    activity_level = "Activity Level"
    stress_level = "Stress Level"

    # BAR PLOT
    # decimal_places = 2
    # sns.barplot(data=df.assign(**{sleep_duration: df[sleep_duration].round(decimal_places)}), 
    #             x=sleep_duration, y=heart_rate)

    sns.barplot(data=df, x=activity_level, y=stress_level)
    plt.yscale('log')
    plt.show()
    # =================================================================

    # HISTOGRAM
    sns.histplot(df[heart_rate])
    plt.show()
    # =================================================================

    # SCATTER PLOT
    df.plot.scatter(x=sleep_duration, y=step_count)
    plt.show()

def printdf(df, force=False):
    if DEBUG or force:
        print(tabulate(df, headers='keys', tablefmt='pretty', showindex=False))

def main():
    # Read the CSV file into a DataFrame
    df = pd.read_csv('unclean_smartwatch_health_data.csv')  # or use StringIO if working with the text directly

    # Pretty print the DataFrame with formatting
    printdf(df)

    # removing NaN and ERROR rows
    df = cleandf(df)
    printdf(df)

    # removing duplcates
    df_no_dupl = df.drop_duplicates()
    rows_before = len(df)
    rows_after = len(df_no_dupl)
    print("\nDuplicate Rows Removed:", rows_before - rows_after)

    df = df_no_dupl
    print("DataFrame Shape no duplicates:", df.shape)

    # correcting types   
    df = check_types(df)
    # checking whether values make sense
    df = check_values(df)

    printdf(df, True)

    analyze_simple(df)
    analyze_advanced(df)

    visualize(df)

main()


