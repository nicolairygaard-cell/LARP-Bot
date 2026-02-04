# =======================================================
#  Casual Havocer Bot Systems
#  Author: Nothing Around Us
#  Created: 2025
#  File: database.py
#  Description:
#      Provides database helper functions and utilities
#      for storing and retrieving persistent data.
#      Temporaroily disabled.
# =======================================================

# import json
# import os

# WARNINGS_FILE = "data/warnings.json"


# def save_warning_log(user_id: int, reason: str, signers: list, moderator_id: int):
#     """Append a warning entry to warnings.json"""
#     if not os.path.exists(WARNINGS_FILE):
#         with open(WARNINGS_FILE, "w") as f:
#             json.dump([], f, indent=4)

#     with open(WARNINGS_FILE, "r") as f:
#         data = json.load(f)

#     new_warning = {
#         "user_id": user_id,
#         "reasons": reason,
#         "signers": signers,
#         "moderator_id": moderator_id
#     }

#     data.append(new_warning)
#     with open(WARNINGS_FILE, "w") as f:
#         json.dump(data, f, indent=4)

"""
You can ignore this file as it has been left empty for now.
It doesn't update the json files.
"""