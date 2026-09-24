import os
import pandas as pd

def authenticate(username: str, password: str) -> bool:
    """
    Verifies user credentials from users.csv
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    users_path = os.path.join(base_dir, "users.csv")
    users = pd.read_csv(users_path)

    result = ((users["username"] == username) &
              (users["password"] == password)).any()
    return bool(result)
