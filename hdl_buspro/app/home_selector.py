class HomeSelector:
    def __init__(self, hdl, home_names):
        self.hdl = hdl
        self.home_names = home_names or []

    def select(self):
        homes = self.hdl.get_homes()

        if not homes:
            raise Exception("❌ No HDL homes found")

        print("\n📦 Available HDL homes:")
        for h in homes:
            print(f" - {h['homeName']} ({h['homeId']})")

        if not self.home_names:
            raise Exception(
                "\n❌ home_names is empty!\n"
                "Please configure add-on options:\n"
                "home_names:\n"
                "  - \"Your Home Name\"\n"
            )

        selected = [
            h for h in homes
            if h["homeName"] in self.home_names
        ]

        if not selected:
            raise Exception(
                "\n❌ None of configured home_names found!\n"
                f"Configured: {self.home_names}\n"
                "Available homes printed above.\n"
            )

        found_names = [h["homeName"] for h in selected]
        missing = [n for n in self.home_names if n not in found_names]

        if missing:
            print(f"⚠️ Warning: some homes not found: {missing}")

        print("\n✅ Selected HDL homes:")
        for h in selected:
            print(f" - {h['homeName']} ({h['homeId']})")

        return selected


def select_homes(all_homes, home_names):
    if not all_homes:
        raise Exception("❌ No HDL homes found")

    print("\n📦 Available HDL homes:")
    for h in all_homes:
        print(f" - {h['homeName']} ({h['homeId']})")

    if not home_names:
        raise Exception(
            "\n❌ home_names is empty!\n"
            "Please configure add-on options:\n"
            "home_names:\n"
            "  - \"Your Home Name\"\n"
        )

    selected = [
        h for h in all_homes
        if h["homeName"] in home_names
    ]

    if not selected:
        raise Exception(
            "\n❌ None of configured home_names found!\n"
            f"Configured: {home_names}\n"
            "Available homes printed above.\n"
        )

    found_names = [h["homeName"] for h in selected]
    missing = [n for n in home_names if n not in found_names]

    if missing:
        print(f"⚠️ Warning: some homes not found: {missing}")

    print("\n✅ Selected HDL homes:")
    for h in selected:
        print(f" - {h['homeName']} ({h['homeId']})")

    return selected
1