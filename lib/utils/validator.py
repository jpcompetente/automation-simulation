class Validator:
    @staticmethod
    def validate_temperature(value):
        if value < -10 or value > 150:
            return False
        return True