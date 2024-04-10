import logging

import requests as requests

from ..entities.processed_agent_data import ProcessedAgentData
from ..interfaces.hub_gateway import HubGateway
from fastapi.encoders import jsonable_encoder


class HubHttpAdapter(HubGateway):
    def __init__(self, api_base_url):
        self.api_base_url = api_base_url

    def save_data(self, processed_data: ProcessedAgentData):
        """
        Save the processed road data to the Hub.
        Parameters:
            processed_data (ProcessedAgentData): Processed road data to be saved.
        Returns:
            bool: True if the data is successfully saved, False otherwise.
        """
        url = f"{self.api_base_url}/processed_agent_data/"
        # print(processed_data)
        processed_data = jsonable_encoder(processed_data)

        response = requests.post(url, json=processed_data)
        response.raise_for_status()
        if response.status_code != 200:
            logging.info(
                f"Invalid Hub response\nData: {processed_data}\nResponse: {response}"
            )
            return False
        return True
