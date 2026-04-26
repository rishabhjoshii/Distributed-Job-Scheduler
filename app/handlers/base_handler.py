"""Base job handler."""

from abc import ABC, abstractmethod

class JobHandler(ABC):

    @abstractmethod
    def execute(self, job):
        pass