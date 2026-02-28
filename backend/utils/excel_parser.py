import pandas as pd
from fastapi import UploadFile


REQUIRED_COLUMNS = {"name", "phone", "email", "experience_years"}
OPTIONAL_COLUMNS = {"resume_text"}


def parse_candidate_excel(file: UploadFile) -> list[dict]:

    try:
        # Detect file type
        if file.filename.endswith(".xlsx"):
            df = pd.read_excel(file.file)
        elif file.filename.endswith(".csv"):
            df = pd.read_csv(file.file)
        else:
            raise ValueError("Unsupported file format")

    except Exception:
        raise ValueError("Failed to read Excel file")

    # Normalize column names (lowercase + strip spaces)
    df.columns = df.columns.str.strip().str.lower()

    # Validate required columns
    missing_columns = REQUIRED_COLUMNS - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {', '.join(missing_columns)}"
        )

    candidates = []

    for index, row in df.iterrows():

        # Basic row validation
        if pd.isna(row["name"]) or pd.isna(row["phone"]) or pd.isna(row["email"]):
            raise ValueError(f"Missing required value in row {index + 2}")

        candidate = {
            "name": str(row["name"]).strip(),
            "phone": str(row["phone"]).strip(),
            "email": str(row["email"]).strip(),
            "experience_years": int(row["experience_years"]),
            "resume_text": (
                str(row["resume_text"]).strip()
                if "resume_text" in df.columns and not pd.isna(row.get("resume_text"))
                else None
            ),
        }

        candidates.append(candidate)

    return candidates