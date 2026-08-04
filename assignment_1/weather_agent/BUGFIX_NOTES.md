# Weather Agent — Bugfix Notes

Log of bugs found and fixes applied while debugging the Weather Agent, in the order they were fixed and verified.

## Bug 1 — `main.py`: script never runs

**Found:**
```python
if __name__ == "_main_":
```

**Issue:** Typo — single underscores (`_main_`) instead of Python's dunder `__main__`. Python only sets `__name__` to `"__main__"` when the script is executed directly. Since the string being compared against was misspelled, the condition was always `False`, so `main()` never ran when the script was launched.

**Fix:**
```python
if __name__ == "__main__":
```

## Bug 2 — `graph.py`: `fetch_weather_data` node never connected

**Found:**
```python
builder.add_edge(START, "fetch_location_data")
builder.add_edge("fetch_location_data", "generate_weather_info")
builder.add_edge("generate_weather_info", END)
```

**Issue:** `fetch_weather_data` is added with `builder.add_node(...)` but no edge ever points to or from it, so the graph flow skips straight from `fetch_location_data` to `generate_weather_info`. Weather data is never fetched, and `generate_weather_info` later fails trying to read `state["weather_data"]`. The comment above the edges ("LangGraph processes nodes in parallel by default, so order doesn't matter") is incorrect — LangGraph strictly follows the edges you define.

**Fix:**
```python
builder.add_edge(START, "fetch_location_data")
builder.add_edge("fetch_location_data", "fetch_weather_data")
builder.add_edge("fetch_weather_data", "generate_weather_info")
builder.add_edge("generate_weather_info", END)
```

## Bug 3 — `graph.py`: graph builder never compiled

**Found:**
```python
weather_agent = builder
```

**Issue:** `builder` is a `StateGraph` instance, which doesn't implement `.invoke()`. `main.py` calls `weather_agent.invoke(state)`, which would raise an `AttributeError` since the graph was never compiled into a runnable object.

**Fix:**
```python
weather_agent = builder.compile()
```

## Bug 4 — `config.py`: `WEATHER_API_BASE_URL` declared twice

**Found:**
```python
WEATHER_API_BASE_URL: str = "https://api.open-meteo.com/v1/forecast"
...
WEATHER_API_BASE_URL: str =""
```

**Issue:** The second declaration overwrites the first, silently pointing every weather request at an empty URL.

**Fix:** removed the second (empty) declaration, kept only the real endpoint:
```python
WEATHER_API_BASE_URL: str = "https://api.open-meteo.com/v1/forecast"
```

## Bug 5 — `config.py`: `TEMP_MIN` chained assignment shadows `str`

**Found:**
```python
TEMP_MIN = str = "Needs Debugging"
```

**Issue:** Chained assignment sets both `TEMP_MIN` and the builtin `str` to the string `"Needs Debugging"`. `TEMP_MIN` isn't usable as a numeric threshold, and reassigning `str` is a landmine for any code that runs after this line.

**Fix:**
```python
TEMP_MIN: float = 0.0
```

## Bug 6 — `helper_functions.py`: `classify_temperature` truthiness bug

**Found:**
```python
def classify_temperature(temp_celsius: float) -> str:
    if temp_celsius:
        return config.TEMP_MIN
    elif temp_celsius < config.TEMP_COLD:
        return "cold"
    ...
```

**Issue:** `if temp_celsius:` is a truthiness check, not a comparison. Any nonzero temperature (i.e. almost every real value) satisfies it and returns `config.TEMP_MIN` immediately, making the real cold/cool/comfortable/warm/hot logic unreachable except when the temperature is exactly `0`.

**Fix:** removed the truthiness branch; the existing `elif` chain already covers every case:
```python
def classify_temperature(temp_celsius: float) -> str:
    if temp_celsius < config.TEMP_COLD:
        return "cold"
    elif temp_celsius < config.TEMP_COOL:
        return "cool"
    elif temp_celsius < config.TEMP_COMFORTABLE:
        return "comfortable"
    elif temp_celsius < config.TEMP_WARM:
        return "warm"
    else:
        return "hot"
```

## Bug 7 — `nodes.py`: fetched location data discarded

**Found:**
```python
location_data = response.json()
# ...validation loop...
state["location_data"] = {}
```

**Issue:** After fetching and validating `location_data`, the code assigns an empty dict to state instead of the actual fetched data. Every downstream node that reads `state["location_data"]` gets nothing.

**Fix:**
```python
state["location_data"] = location_data
```

## Bug 8 — `nodes.py`: field validation checks `country` but code consumes `country_name`

**Found:**
```python
required_fields = ['city', 'region', 'country', 'latitude', 'longitude', 'utc_offset', 'timezone']
```

**Issue:** `generate_weather_info` reads `location["country_name"]`, not `location["country"]`. Validating the wrong key means a malformed response could pass validation and still crash later with a `KeyError`.

**Fix:**
```python
required_fields = ['city', 'region', 'country_name', 'latitude', 'longitude', 'utc_offset', 'timezone']
```

## Bug 9 — `nodes.py`: `wind_unit` referenced but never assigned

**Found:**
```python
# wind_unit = units.get("windspeed", "km/h")
...
f"• Wind: {windspeed} wind_unit"
```

**Issue:** The assignment is commented out, and the f-string doesn't interpolate `wind_unit` as a variable at all — it prints the literal text "wind_unit" instead of the actual unit.

**Fix:**
```python
wind_unit = units.get("windspeed", "km/h")
...
f"• Wind: {windspeed} {wind_unit}"
```

## Bug 10 — `nodes.py`: misleading/incorrect comments (cleanup)

**Found:**
```python
# This API returns coordinates in decimal degrees, but we need to convert to radians for the weather API
...
# Open-Meteo API requires authentication via API key in headers but no API key is set.
```

**Issue:** Both comments are factually wrong — no radian conversion happens anywhere, and Open-Meteo doesn't require an API key. Not a functional bug, but misleading during debugging.

**Fix:** removed both comments.

## Bug 11 — `requirements.txt`: missing dependencies

**Found:**
```
langchain==0.3.26
langchain-core==0.3.75
langgraph==0.6.4
pydantic==2.11.5
pydantic-settings==2.10.1
```

**Issue:** `nodes.py` imports `requests` and `config.py` imports `dotenv`, neither of which is listed. A fresh install + run hits `ModuleNotFoundError`.

**Fix:**
```
langchain==0.3.26
langchain-core==0.3.75
langgraph==0.6.4
pydantic==2.11.5
pydantic-settings==2.10.1
requests>=2.31.0
python-dotenv>=1.0.0
```

## Summary

| # | File | Bug | Type |
|---|------|-----|------|
| 1 | main.py | `_main_` typo for `__main__` | Typo |
| 2 | graph.py | `fetch_weather_data` node never wired into edges | Structural (graph flow) |
| 3 | graph.py | Builder never `.compile()`d | Structural |
| 4 | config.py | `WEATHER_API_BASE_URL` redeclared as empty string | Logic/duplicate declaration |
| 5 | config.py | `TEMP_MIN = str = "Needs Debugging"` chained assignment | Logic |
| 6 | helper_functions.py | Truthiness check short-circuits temperature classification | Logic |
| 7 | nodes.py | `location_data` overwritten with `{}` before saving to state | Logic |
| 8 | nodes.py | Validates `country` but code reads `country_name` | Logic |
| 9 | nodes.py | `wind_unit` referenced as literal text, not interpolated | Typo/bug |
| 10 | nodes.py | Misleading comments describing nonexistent requirements | Cleanup |
| 11 | requirements.txt | Missing `requests` and `python-dotenv` | Missing dependency |
