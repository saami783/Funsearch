class DummyFunsearch:
    @staticmethod
    def run(func): return func
    @staticmethod
    def evolve(func): return func

funsearch = DummyFunsearch()