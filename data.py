

class Variants:
    def __init__(self):
        super(Variants, self).__init__()

    def buttons(self, index):
        return f"/html[@class=' json csscalc no-touchevents cssvhunit cssvwunit cssanimations flexbox']/body/div[@id='panel2_mainContainer']/div/div[@class='oprosso-poll']/div[@class='oprosso-poll__wrapper']/div[@class='oprosso-poll__horizontallContainer']/span/div/div[1]/div/div/div[@class='oprosso-poll__question-wrapper']/div[@class='oprosso-poll__question-wrapper-inner oprosso-poll__question-wrapper-inner_substrate']/div/div[@class='oprosso-poll__question-body']/div[@class='oprosso-poll-type__closed-wrapper']/div[@class='oprosso-panel-common-option'][{index}]/div[@class='oprosso-panel-common-option__content']/div[@class='oprosso-panel-common-option__text']"