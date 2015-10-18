class PaymentMode:
    id = ''
    text = ''
    replay_button_text = ''

    def execute(self, order):
        raise NotImplementedError
