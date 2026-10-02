import os
import pandas as pd
from typing import List
from pydantic import BaseModel, Field, field_validator, ValidationError


# ---------- 1. Define the Pydantic model ----------
class Person(BaseModel):
    """Schema for a single row of the DataFrame."""
    Name: str = Field(..., min_length=1, description="Person's name")
    Age: int = Field(..., ge=0, le=120, description="Age must be 0-120")
    City: str = Field(..., min_length=1, description="City name")

    @field_validator("Name", "City")
    @classmethod
    def strip_and_check(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("must not be empty or whitespace")
        return v

    # (Optional) Example: normalize title case
    @field_validator("Name", "City")
    @classmethod
    def to_title(cls, v: str) -> str:
        return v.title()


# ---------- 2. Wrapper model for the full dataset ----------
class PeopleDataset(BaseModel):
    records: List[Person]


# ---------- 3. Build DataFrame ----------
data = {
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Age': [25, 30, 35],
    'City': ['New York', 'Los Angeles', 'Chicago'],
}
df = pd.DataFrame(data)

# ---------- 4. Validate each row with Pydantic ----------
validated_rows = []


for idx, row in df.iterrows(): # df.iterrows() gives you a (index, row) tuple, where row is a pandas Series
    try:
        # Person(**{'Name': 'Alice', 'Age': 25, 'City': 'New York'}) is exactly equivalent to Person(Name='Alice', Age=25, City='New York')
        person = Person(**row.to_dict()) 
        validated_rows.append(person.model_dump())  # model_dump() converts a model instance back into a plain Python dictionary
    except ValidationError as e:
        print(f"Row {idx} failed validation:\n{e}\n")


# ---------- 5. Rebuild DataFrame from validated data ----------
clean_df = pd.DataFrame(validated_rows)

# ---------- 6. Save to CSV ----------
data_dir = 'data'
os.makedirs(data_dir, exist_ok=True)
file_path = os.path.join(data_dir, 'sample_data.csv')

clean_df.to_csv(file_path, index=False)
print(f"CSV file saved to {file_path}")
print(clean_df)