"""Power Query-style step-based transformations executed with pandas."""
from __future__ import annotations
from typing import Any
import pandas as pd
import numpy as np


def run_query(table: list[dict], steps: list[dict]) -> list[dict]:
    df = pd.DataFrame(table)
    for step in steps:
        kind = step.get("kind")
        try:
            df = _apply_step(df, kind, step)
        except Exception as e:
            raise ValueError(f"Step {kind} failed: {e}")
    df = df.replace({np.nan: None})
    return df.to_dict(orient="records")


def _apply_step(df: pd.DataFrame, kind: str, step: dict) -> pd.DataFrame:
    if kind == "filter_rows":
        col, op, val = step["column"], step.get("op", "=="), step.get("value")
        if op == "==":       return df[df[col] == val]
        if op == "!=":       return df[df[col] != val]
        if op == ">":        return df[df[col] > val]
        if op == "<":        return df[df[col] < val]
        if op == ">=":       return df[df[col] >= val]
        if op == "<=":       return df[df[col] <= val]
        if op == "contains": return df[df[col].astype(str).str.contains(str(val), na=False)]
        if op == "starts":   return df[df[col].astype(str).str.startswith(str(val), na=False)]
        if op == "ends":     return df[df[col].astype(str).str.endswith(str(val), na=False)]
        return df
    if kind == "choose_columns":
        return df[[c for c in step["columns"] if c in df.columns]]
    if kind == "remove_columns":
        return df.drop(columns=[c for c in step["columns"] if c in df.columns])
    if kind == "rename_column":
        return df.rename(columns={step["from"]: step["to"]})
    if kind == "change_type":
        mapping = {"int": "Int64", "float": "float64", "str": "string",
                   "date": "datetime64[ns]", "bool": "bool"}
        df[step["column"]] = df[step["column"]].astype(mapping.get(step["to"], "object"))
        return df
    if kind == "replace_value":
        return df.replace({step["column"]: {step["find"]: step["replace"]}})
    if kind == "fill_down":
        df[step["column"]] = df[step["column"]].ffill()
        return df
    if kind == "fill_up":
        df[step["column"]] = df[step["column"]].bfill()
        return df
    if kind == "split_column":
        split = df[step["column"]].astype(str).str.split(step.get("by", ","), expand=True)
        for i, name in enumerate(step["into"]):
            df[name] = split[i] if i < split.shape[1] else None
        return df
    if kind == "merge_columns":
        df[step["into"]] = df[step["columns"]].astype(str).agg(step.get("separator", " ").join, axis=1)
        return df
    if kind == "group_by":
        agg = {a["column"]: a["op"] for a in step["aggregations"]}
        return df.groupby(step["columns"]).agg(agg).reset_index()
    if kind == "sort":
        return df.sort_values(step["column"], ascending=step.get("ascending", True))
    if kind == "pivot":
        return df.pivot_table(index=step["index"], columns=step["columns"], values=step["values"],
                              aggfunc=step.get("aggfunc", "sum")).reset_index()
    if kind == "unpivot":
        return df.melt(id_vars=step["id_vars"], value_vars=step["value_vars"],
                       var_name=step.get("var_name", "variable"),
                       value_name=step.get("value_name", "value"))
    if kind == "custom_column":
        df[step["name"]] = df.eval(step["formula"])
        return df
    if kind == "append":
        return pd.concat([df, pd.DataFrame(step["rows"])], ignore_index=True)
    if kind == "limit":
        return df.head(int(step["n"]))
    raise ValueError(f"Unknown step kind: {kind}")