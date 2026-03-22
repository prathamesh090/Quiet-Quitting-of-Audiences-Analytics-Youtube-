import os

print("Running clean_data.py ...")
os.system(r'python "E:\SMA Project\src\clean_data.py"')

print("Running sentiment_analysis.py ...")
os.system(r'python "E:\SMA Project\src\sentiment_analysis.py"')

print("Running engagement_analysis.py ...")
os.system(r'python "E:\SMA Project\src\engagement_analysis.py"')

print("Running quiet_quitting_detector.py ...")
os.system(r'python "E:\SMA Project\src\quiet_quitting_detector.py"')

print("Full pipeline completed.")