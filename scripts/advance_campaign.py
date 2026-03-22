from pathlib import Path

p = Path("C:/Users/fabia/AppData/Roaming/TempleGates/Dominion/profiles.xml")

with p.open() as f:
    content = f.read()
for i in [2, 3]:
    if f"<availability>{i}</availability>\n      </mission>" in content:
        content = content.replace(
            f"""<availability>{i}</availability>
      </mission>
      <mission>
      </mission>""",
            """<availability>4</availability>
        <completionLevel>2</completionLevel>
      </mission>
      <mission>
        <availability>2</availability>
      </mission>""",
        )
        print("Advanced successfully")
        break
with p.open("w") as f:
    f.write(content)
print("Done")
