import abc


class ProcessDistributorEventUseCase(abc.ABC):
    @abc.abstractmethod
    def process(self, event: dict):
        pass
