def validate_logic_config(config):
    """
    Validate that logic_config.json has all required keys with sane values.
    Raises ValueError with a clear message if something is missing or invalid.
    """
    if "temperature" not in config:
        raise ValueError("logic_config.json is missing the 'temperature' section")

    temp_cfg = config["temperature"]
    required_keys = ["high_threshold", "warning_limit", "error_limit", "min_valid", "max_valid"]

    for key in required_keys:
        if key not in temp_cfg:
            raise ValueError(f"logic_config.json -> 'temperature' is missing required key: '{key}'")
        if not isinstance(temp_cfg[key], (int, float)):
            raise ValueError(f"logic_config.json -> 'temperature.{key}' must be a number, got: {temp_cfg[key]!r}")

    if temp_cfg["min_valid"] >= temp_cfg["max_valid"]:
        raise ValueError("logic_config.json -> 'min_valid' must be less than 'max_valid'")

    if temp_cfg["high_threshold"] <= temp_cfg["min_valid"] or temp_cfg["high_threshold"] >= temp_cfg["max_valid"]:
        raise ValueError("logic_config.json -> 'high_threshold' must be between 'min_valid' and 'max_valid'")

    print("[OK] logic_config.json validated successfully")


def validate_devices_config(config):
    """
    Validate that devices.json has the expected structure.
    Raises ValueError with a clear message if something is missing or invalid.
    """
    for section in ["sensors", "actuators"]:
        if section not in config:
            raise ValueError(f"devices.json is missing the '{section}' section")

        for i, entry in enumerate(config[section]):
            for key in ["name", "module", "class"]:
                if key not in entry:
                    raise ValueError(f"devices.json -> {section}[{i}] is missing required key: '{key}'")

    print("[OK] devices.json validated successfully")
