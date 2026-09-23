"""Dual CCI extreme harness. Classification only. No orders. No official act."""


def classify(cci30, cci100, sma30, sma100):
    level_buy = cci30 > 100.0 and cci100 > 100.0
    level_sell = cci30 < -100.0 and cci100 < -100.0
    confirm_buy = level_buy and cci30 > sma30 and cci100 > sma100
    confirm_sell = level_sell and cci30 < sma30 and cci100 < sma100
    if level_buy:
        return {
            "level": "BUY",
            "confirm": confirm_buy,
            "active": "ACTIVE",
            "tide": "long_only",
            "act": "n/a",
            "state": "cci_extreme_confirmed" if confirm_buy else "cci_extreme",
        }
    if level_sell:
        return {
            "level": "SELL",
            "confirm": confirm_sell,
            "active": "ACTIVE",
            "tide": "short_only",
            "act": "n/a",
            "state": "cci_extreme_confirmed" if confirm_sell else "cci_extreme",
        }
    return {
        "level": "NONE",
        "confirm": False,
        "active": "INACTIVE",
        "tide": "flat",
        "act": "n/a",
        "state": "none",
    }


def _check(name, got, **expect):
    for key, value in expect.items():
        if got[key] != value:
            raise SystemExit(f"{name} {key}={got[key]!r} expected {value!r}")


def main():
    _check("confirm buy", classify(150, 120, 80, 90), level="BUY", confirm=True, act="n/a", tide="long_only")
    _check("level buy sma lag", classify(150, 120, 160, 90), level="BUY", confirm=False, state="cci_extreme", act="n/a")
    _check("confirm sell", classify(-150, -120, -80, -90), level="SELL", confirm=True, tide="short_only", act="n/a")
    _check("level sell sma lag", classify(-150, -120, -80, -200), level="SELL", confirm=False, state="cci_extreme")
    _check("one side only", classify(150, 50, 10, 10), level="NONE", active="INACTIVE", act="n/a")
    _check("split", classify(150, -150, 10, -10), level="NONE", tide="flat")
    _check("touch +100", classify(100, 150, 10, 10), level="NONE")
    _check("touch sma", classify(150, 120, 150, 90), level="BUY", confirm=False)
    print("CCI_HARNESS_OK")


if __name__ == "__main__":
    main()
