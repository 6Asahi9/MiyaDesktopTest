import json
from core.path import SETTINGS_JSON
from core.avatar_toggle import refresh_floating_miya
refresh_floating_miya()

furs = ["White", "Calico", "Tabby", "Orange", "custom"]

def switch_fur(direction, label):
    current = label.text()
    index = furs.index(current)
    if direction == "next":
        index = (index + 1) % len(furs)
    else:
        index = (index - 1) % len(furs)

    new_fur = furs[index]
    label.setText(new_fur)
    try:
        data = json.loads(SETTINGS_JSON.read_text(encoding="utf-8"))
    except Exception:
        data = {}

    data["current_fur"] = new_fur

    SETTINGS_JSON.write_text(
        json.dumps(data, indent=4),
        encoding="utf-8"
    )
    print("Fur switched to", new_fur)
