import json
import logging
from typing import List

import pydantic_core
import requests

from app.entities.processed_agent_data import ProcessedAgentData
from app.interfaces.store_gateway import StoreGateway
from fastapi.encoders import jsonable_encoder


class StoreApiAdapter(StoreGateway):
    def __init__(self, api_base_url):
        self.api_base_url = api_base_url

    def save_data(self, processed_agent_data_batch: List[ProcessedAgentData]):
        """
        Save the processed road data to the Store API.
        Parameters:
            processed_agent_data_batch (dict): Processed road data to be saved.
        Returns:
            bool: True if the data is successfully saved, False otherwise.
        """
        url = f"{self.api_base_url}/processed_agent_data/"
        processed_agent_data_batch.reverse()
        data = [data for data in processed_agent_data_batch]
        try:
            response = requests.post(url, json=jsonable_encoder(data))
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logging.error(f"Error occure while trying to save data to the Store API: {e}")
            return False

