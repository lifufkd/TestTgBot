

class Variants:
    def __init__(self):
        super(Variants, self).__init__()

    def cards_input_query(self, type, index):
        data = [
            f"/html/body/div[1]/div/div/div[1]/div[1]/span/div/div[1]/div[{index}]/div/div",
            f"/html/body/div[1]/div/div/div[1]/div[1]/span/div/div[{index}]/div/div/div/div",
            f"/html/body/div[1]/div/div/div[1]/div[1]/span/div/div[1]/div[{index}]/div/div/div"
        ]
        return data[type]

    def cards_buttons_query(self, type, card, index):
        data = [
            f"/html/body/div[1]/div/div/div[1]/div[1]/span/div/div[1]/div[{card}]/div/div/div/div/div[2]/div[2]/div[{index}]/div[1]",
            f"/html/body/div[1]/div/div/div[1]/div[1]/span/div/div[1]/div/div/div/div/div/div[2]/div[2]/div[{index}]/div[1]",
        ]
        return data[type]

    def circles(self, type, index, card=None):
        data = [
            f"/html/body/div[1]/div/div/div[1]/div[1]/span/div/div[1]/div/div/div/div/div/div[2]/div[2]/div/div/div/div[{index}]",
            f"/html/body/div[1]/div/div/div[1]/div[1]/span/div/div[1]/div[{card}]/div/div/div/div/div[2]/div[2]/div[1]/div/div/div[{index}]"
        ]
        return data[type]

    def checker(self, type):
        data = [
            "/html/body/div[1]/div/div/div[1]/div[1]/span/div/div[1]/div/div/div/div"
        ]
        return data[type]