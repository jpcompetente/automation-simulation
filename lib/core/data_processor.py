class DataProcessor:
    def filter_noise(self, value, threshold=0.5):
        if abs(value) < threshold:
            return 0
        return value

    def normalize(self, value, min_val, max_val):
        if max_val == min_val:
            return 0
        return (value - min_val) / (max_val - min_val)

    def clamp(self, value, min_val, max_val):
        return max(min_val, min(value, max_val))