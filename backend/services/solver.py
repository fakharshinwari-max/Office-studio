"""Optimization solvers: Simplex LP (PuLP), GRG Nonlinear, Evolutionary."""
from __future__ import annotations
from typing import Any


def solve(model: dict[str, Any]) -> dict[str, Any]:
    method = model.get("method", "simplex")
    if method == "simplex":
        return _solve_simplex(model)
    if method == "grg":
        return _solve_grg(model)
    if method == "evolutionary":
        return _solve_evolutionary(model)
    return {"error": f"Unknown method {method}"}


def _solve_simplex(model):
    try:
        import pulp
    except ImportError:
        return {"error": "PuLP not installed. pip install pulp"}

    sense = pulp.LpMaximize if model["objective"]["sense"] == "max" else pulp.LpMinimize
    prob = pulp.LpProblem("Solver", sense)

    vars_ = {}
    for v in model.get("variables", []):
        name = v["name"]
        if v.get("binary"):
            vars_[name] = pulp.LpVariable(name, cat="Binary")
        elif v.get("integer"):
            vars_[name] = pulp.LpVariable(name, lowBound=v.get("min"), upBound=v.get("max"), cat="Integer")
        else:
            vars_[name] = pulp.LpVariable(name, lowBound=v.get("min"), upBound=v.get("max"), cat="Continuous")

    try:
        prob += _expr_to_pulp(model["objective"]["formula"], vars_), "objective"
    except Exception as e:
        return {"error": f"Invalid objective: {e}"}

    for c in model.get("constraints", []):
        try:
            lhs = _expr_to_pulp(c["formula"], vars_)
        except Exception as e:
            return {"error": f"Invalid constraint: {e}"}
        op = c.get("op", "<=")
        rhs = c.get("rhs", 0)
        if op == "<=":
            prob += lhs <= rhs
        elif op == ">=":
            prob += lhs >= rhs
        elif op == "=":
            prob += lhs == rhs

    status = prob.solve(pulp.PULP_CBC_CMD(msg=False))
    return {
        "status": pulp.LpStatus[status],
        "objective": pulp.value(prob.objective),
        "values": {name: var.value() for name, var in vars_.items()},
    }


def _expr_to_pulp(expr: str, vars_):
    env = {name: var for name, var in vars_.items()}
    return eval(expr, {"__builtins__": {}}, env)


def _solve_grg(model):
    try:
        from scipy.optimize import minimize
        import numpy as np
    except ImportError:
        return {"error": "scipy required for GRG"}

    variables = model.get("variables", [])
    if not variables:
        return {"error": "No variables"}
    x0 = np.array([v.get("initial", 0) for v in variables], dtype=float)
    bounds = [(v.get("min"), v.get("max")) for v in variables]

    def objective(x):
        env = {v["name"]: xi for v, xi in zip(variables, x)}
        try:
            val = eval(model["objective"]["formula"], {"__builtins__": {}}, env)
            return val if model["objective"]["sense"] == "max" else -val
        except Exception:
            return 1e12

    def cons(x):
        env = {v["name"]: xi for v, xi in zip(variables, x)}
        out = []
        for c in model.get("constraints", []):
            try:
                v = eval(c["formula"], {"__builtins__": {}}, env)
            except Exception:
                return [1e9]
            rhs = c.get("rhs", 0)
            if c.get("op") == "<=":
                out.append(rhs - v)
            elif c.get("op") == ">=":
                out.append(v - rhs)
            else:
                out.append(abs(v - rhs))
        return out

    constraints = [{"type": "ineq", "fun": cons}] if model.get("constraints") else []
    res = minimize(objective, x0, bounds=bounds, constraints=constraints, method="SLSQP")
    return {
        "status": "Optimal" if res.success else "Infeasible",
        "objective": -res.fun if model["objective"]["sense"] == "max" else res.fun,
        "values": {v["name"]: float(xi) for v, xi in zip(variables, res.x)},
    }


def _solve_evolutionary(model):
    try:
        from scipy.optimize import differential_evolution
        import numpy as np
    except ImportError:
        return {"error": "scipy required for Evolutionary"}

    variables = model.get("variables", [])
    if not variables:
        return {"error": "No variables"}
    bounds = [(v.get("min", -1e6), v.get("max", 1e6)) for v in variables]

    def objective(x):
        env = {v["name"]: xi for v, xi in zip(variables, x)}
        try:
            val = eval(model["objective"]["formula"], {"__builtins__": {}}, env)
            for c in model.get("constraints", []):
                v = eval(c["formula"], {"__builtins__": {}}, env)
                rhs = c.get("rhs", 0)
                if c.get("op") == "<=" and v > rhs:
                    val += 1e6 * (v - rhs)
                if c.get("op") == ">=" and v < rhs:
                    val += 1e6 * (rhs - v)
            return val if model["objective"]["sense"] == "max" else -val
        except Exception:
            return 1e12

    res = differential_evolution(objective, bounds, maxiter=200, tol=1e-6, seed=1)
    return {
        "status": "Optimal" if res.success else "Infeasible",
        "objective": -res.fun if model["objective"]["sense"] == "max" else res.fun,
        "values": {v["name"]: float(xi) for v, xi in zip(variables, res.x)},
    }