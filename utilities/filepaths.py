from pathlib import Path

data_root = Path.cwd().joinpath("data")
names_dir = data_root.joinpath("name_dumps")
responses_dir = data_root.joinpath("responses")
discrepancies_dir = names_dir.joinpath("discrepancies")

discrepancies_unpopular_path = discrepancies_dir.joinpath("unpopular_names.json")
discrepancies_master_csv_path = discrepancies_dir.joinpath("master_output.csv")

unpopular_path = names_dir.joinpath("unpopular_names.json")
master_csv_path = names_dir.joinpath("master_output.csv")
