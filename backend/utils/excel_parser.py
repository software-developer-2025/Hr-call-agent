import pandas as pd
from fastapi import UploadFile
from io import BytesIO


REQUIRED_COLUMNS = {"name", "phone", "email", "experience_years"}
OPTIONAL_COLUMNS = {"resume_text"}


def parse_candidate_excel(file: UploadFile) -> dict:
    """
    Returns:
    {
        "valid_rows": [ {candidate_dict}, ... ],
        "errors": [ {"row": int, "error": str}, ... ]
    }
    """

    try:
        contents = file.file.read()

        if file.filename.endswith(".xlsx"):
            df = pd.read_excel(BytesIO(contents), engine="openpyxl")
        elif file.filename.endswith(".csv"):
            df = pd.read_csv(BytesIO(contents))
        else:
            raise ValueError("Unsupported file format")

    except Exception as e:
        raise ValueError(f"Failed to read Excel file: {str(e)}")

    if df.empty:
        return {"valid_rows": [], "errors": []}

    # Normalize column names
    df.columns = df.columns.str.strip().str.lower()

    missing_columns = REQUIRED_COLUMNS - set(df.columns)
    if missing_columns:
        raise ValueError(
            f"Missing required columns: {', '.join(missing_columns)}"
        )

    valid_rows = []
    errors = []

    for index, row in df.iterrows():
        row_number = index + 2  # Excel row (header = 1)

        try:
            if pd.isna(row["name"]) or pd.isna(row["phone"]) or pd.isna(row["email"]):
                raise ValueError("Missing required value")

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

            valid_rows.append(candidate)

        except Exception as e:
            errors.append({
                "row": row_number,
                "error": str(e)
            })

    return {
        "valid_rows": valid_rows,
        "errors": errors
    }