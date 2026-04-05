class HomeSelector:
    def __init__(self, hdl):
        self.hdl = hdl

    def select(self):
        homes = self.hdl.get_homes()

        if not homes:
            raise Exception("No homes found")

        print("\nAvailable HDL homes:")
        for i, h in enumerate(homes):
            print(f"{i}: {h['homeName']} ({h['homeId']})")

        # пока берём первый (потом можно сделать выбор через config)
        return homes[0]