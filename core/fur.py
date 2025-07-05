furs = ["White", "Calico", "Tabby", "Orange"]

def switch_fur(direction, label):
    current = label.text()
    index = furs.index(current)
    if direction == "next":
        index = (index + 1) % len(furs)
    else:
        index = (index - 1) % len(furs)
    label.setText(furs[index])
    print("Fur switched to", furs[index])
